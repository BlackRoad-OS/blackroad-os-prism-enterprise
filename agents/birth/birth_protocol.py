"""Utilities for "birthing" agent identities from census and archetype data."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import yaml

LOGGER = logging.getLogger(__name__)


@dataclass
class AgentCandidate:
    """Lightweight container for a potential agent identity."""

    id: str
    name: str
    role: str
    archetype: str
    source: str
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_identity(self) -> Dict[str, object]:
        """Convert the candidate into a finalized identity record."""

        if not self.id or not self.name:
            raise ValueError("AgentCandidate requires both id and name")

        metadata = dict(self.metadata or {})
        tags = metadata.get("tags") or []
        metadata["tags"] = list(tags)
        metadata.setdefault("source", self.source)

        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        return {
            "id": self.id,
            "name": self.name,
            "role": self.role or "unknown",
            "archetype": self.archetype or self.role or self.id,
            "status": "born",
            "created_at": created_at,
            "metadata": metadata,
        }


class AgentBirthProtocol:
    """Load the census + archetypes and emit JSONL identity records."""

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        census_path: Optional[Path] = None,
        archetype_root: Optional[Path] = None,
        identities_path: Optional[Path] = None,
    ) -> None:
        base_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
        self.repo_root = base_root
        self.census_path = Path(census_path) if census_path else base_root / "AGENT_CENSUS_COMPLETE.md"
        self.archetype_root = (
            Path(archetype_root) if archetype_root else base_root / "agents" / "archetypes"
        )
        self.identities_path = (
            Path(identities_path) if identities_path else base_root / "artifacts" / "agents" / "identities.jsonl"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, limit: Optional[int] = None, dry_run: bool = False) -> Dict[str, int]:
        """Birth agent identities, returning a summary of the run."""

        candidates = self._discover_candidates()
        total_candidates = len(candidates)

        existing_records, known_ids = self._load_existing_identities()
        born: List[Dict[str, object]] = []
        skipped = 0
        failed = 0
        seen_ids = set(known_ids)

        for candidate in candidates:
            if limit is not None and len(born) >= limit:
                break

            if not candidate.id or not candidate.name:
                failed += 1
                LOGGER.warning("Skipping candidate with missing id or name: %s", candidate)
                continue

            if candidate.id in seen_ids:
                skipped += 1
                continue

            try:
                record = candidate.to_identity()
            except ValueError as exc:
                failed += 1
                LOGGER.warning("Failed to birth candidate %s: %s", candidate.id, exc)
                continue

            born.append(record)
            seen_ids.add(candidate.id)

        if not dry_run:
            self._write_identities(existing_records, born)
        else:
            LOGGER.info("Dry run: would write %s new identities", len(born))

        summary = {
            "discovered": total_candidates,
            "born": len(born),
            "skipped": skipped,
            "failed": failed,
            "existing": len(existing_records),
        }

        self._log_summary(summary, dry_run=dry_run)
        return summary

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _discover_candidates(self) -> List[AgentCandidate]:
        candidates: List[AgentCandidate] = []

        if self.census_path.exists():
            candidates.extend(self._load_census_candidates())
        else:
            LOGGER.info("Census file not found at %s", self.census_path)

        if self.archetype_root.exists():
            candidates.extend(self._load_archetype_candidates())
        else:
            LOGGER.info("Archetype root not found at %s", self.archetype_root)

        return candidates

    def _load_census_candidates(self) -> List[AgentCandidate]:
        text = self.census_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        candidates: List[AgentCandidate] = []
        header: Optional[List[str]] = None
        category: Optional[str] = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("###"):
                category = line.lstrip("#").strip()
                header = None
                continue

            if self._is_table_line(line):
                cells = self._split_table_cells(line)
                if header is None:
                    header = [cell.lower() for cell in cells]
                    continue

                if self._is_separator_row(cells):
                    continue

                row = {header[i]: cells[i] for i in range(min(len(header), len(cells)))}
                candidate = self._row_to_candidate(row, category)
                if candidate:
                    candidates.append(candidate)
                else:
                    LOGGER.warning("Unable to parse census row: %s", row)
                continue

            header = None

        LOGGER.info("Loaded %s census candidates", len(candidates))
        return candidates

    def _row_to_candidate(self, row: Dict[str, str], category: Optional[str]) -> Optional[AgentCandidate]:
        normalized = {key.strip().lower(): value.strip() for key, value in row.items()}
        agent_id = (
            normalized.get("id")
            or normalized.get("agent id")
            or normalized.get("slug")
            or normalized.get("code")
        )
        if not agent_id:
            return None

        name = normalized.get("name") or normalized.get("agent") or agent_id
        role = (
            normalized.get("role")
            or normalized.get("primary role")
            or normalized.get("type")
            or normalized.get("full title")
            or "unknown"
        )
        archetype = (
            normalized.get("archetype")
            or normalized.get("full title")
            or normalized.get("cluster")
            or role
        )

        tags: List[str] = []
        if category:
            tags.append(category)

        metadata: Dict[str, object] = {
            "source": "AGENT_CENSUS_COMPLETE.md",
            "tags": tags,
        }
        if normalized.get("status"):
            metadata["status"] = normalized.get("status")
        if normalized.get("category"):
            metadata["category"] = normalized.get("category")

        return AgentCandidate(
            id=agent_id.strip(),
            name=name.strip(),
            role=role.strip(),
            archetype=archetype.strip(),
            source="census",
            metadata=metadata,
        )

    def _load_archetype_candidates(self) -> List[AgentCandidate]:
        manifests = sorted(self.archetype_root.rglob("*.manifest.yaml"))
        candidates: List[AgentCandidate] = []

        for manifest_path in manifests:
            try:
                data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
            except Exception as exc:  # pragma: no cover - defensive logging
                LOGGER.warning("Failed to parse archetype %s: %s", manifest_path, exc)
                continue

            agent_id = str(data.get("id") or manifest_path.stem)
            name = str(data.get("name") or agent_id.replace("-", " ").title())
            role = str(data.get("role") or data.get("domain") or "unknown")

            tags = data.get("covenant_tags") or []
            if not isinstance(tags, list):
                tags = [str(tags)]

            metadata: Dict[str, object] = {
                "cluster": data.get("cluster"),
                "domain": data.get("domain"),
                "tags": tags,
                "source": "archetype",
            }

            relative_path = self._relative_path(manifest_path)

            candidates.append(
                AgentCandidate(
                    id=agent_id,
                    name=name,
                    role=role,
                    archetype=relative_path,
                    source="archetype",
                    metadata=metadata,
                )
            )

        LOGGER.info("Loaded %s archetype candidates", len(candidates))
        return candidates

    # ------------------------------------------------------------------
    # File helpers
    # ------------------------------------------------------------------
    def _load_existing_identities(self) -> (List[Dict[str, object]], Dict[str, Dict[str, object]]):
        records: List[Dict[str, object]] = []
        index: Dict[str, Dict[str, object]] = {}

        if not self.identities_path.exists():
            return records, index

        for line in self.identities_path.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive logging
                LOGGER.warning("Skipping malformed identity line: %s", exc)
                continue
            record_id = data.get("id")
            if not record_id:
                continue
            records.append(data)
            index[str(record_id)] = data

        return records, index

    def _write_identities(self, existing: Sequence[Dict[str, object]], new: Sequence[Dict[str, object]]) -> None:
        combined = list(existing) + list(new)
        self.identities_path.parent.mkdir(parents=True, exist_ok=True)
        with self.identities_path.open("w", encoding="utf-8") as handle:
            for record in combined:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------
    # Misc helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _is_table_line(line: str) -> bool:
        return line.startswith("|") and "|" in line[1:]

    @staticmethod
    def _split_table_cells(line: str) -> List[str]:
        parts = [cell.strip() for cell in line.strip().strip("|").split("|")]
        return parts

    @staticmethod
    def _is_separator_row(cells: Sequence[str]) -> bool:
        return all(re.fullmatch(r"[:-]+", cell.replace(" ", "")) for cell in cells)

    def _relative_path(self, manifest_path: Path) -> str:
        try:
            return str(manifest_path.relative_to(self.repo_root))
        except ValueError:
            return str(manifest_path)

    @staticmethod
    def _log_summary(summary: Dict[str, int], dry_run: bool) -> None:
        prefix = "[dry-run] " if dry_run else ""
        LOGGER.info(
            "%sBirth summary: discovered=%s, born=%s, skipped=%s, failed=%s, existing=%s",
            prefix,
            summary["discovered"],
            summary["born"],
            summary["skipped"],
            summary["failed"],
            summary["existing"],
        )

