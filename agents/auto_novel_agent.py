"""Utility agent capable of ideating stories and lightweight games."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Iterable, Sequence

import sys

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent))
    from consent_policy import ConsentRecord, ensure_full_consent  # type: ignore
else:  # pragma: no cover - executed when the package is installed
    from .consent_policy import ConsentRecord, ensure_full_consent

DEFAULT_SUPPORTED_ENGINES: tuple[str, ...] = ("unity", "unreal")

_OPERATION_SCOPE_MAP: dict[str, str] = {
    "deploy": "agent:deploy",
    "create_game": "game:create",
    "generate_game_idea": "story:ideate",
    "generate_story": "story:create",
    "generate_story_series": "story:create",
    "generate_coding_challenge": "content:create",
    "generate_code_snippet": "code:suggest",
    "proofread_paragraph": "content:edit",
    "validate_scopes": "consent:validate",
    "add_supported_engine": "agent:configure",
    "remove_supported_engine": "agent:configure",
    "set_gamma": "agent:configure",
    "write_novel": "story:create",
}

_BASE_CONSENT_SCOPES = {"outline:read", "outline:write"}
DEFAULT_CONSENT_SCOPES = frozenset(
    _BASE_CONSENT_SCOPES.union(_OPERATION_SCOPE_MAP.values())
)


@dataclass
class AutoNovelAgent:
    """A small agent that can build games and craft stories."""

    name: str = "AutoNovelAgent"
    gamma: float = 1.0
    supported_engines: set[str] = field(
        default_factory=lambda: set(DEFAULT_SUPPORTED_ENGINES)
    )
    consent: ConsentRecord = field(
        default_factory=lambda: ConsentRecord.full(
            scopes=DEFAULT_CONSENT_SCOPES,
            evidence="AutoNovelAgent default configuration",
        )
    )
    _created_games: list[str] = field(default_factory=list, init=False, repr=False)

    SAMPLE_SNIPPETS: ClassVar[dict[str, str]] = {
        "python": "def solve():\n    # TODO: Implement addition\n    pass\n",
        "javascript": "function solve() {\n  // TODO: Implement addition\n  return null;\n}\n",
        "java": (
            "class Solution {\n"
            "    void solve() {\n"
            "        // TODO: Implement addition\n"
            "    }\n"
            "}\n"
        ),
    }
    OPERATION_SCOPE_MAP: ClassVar[dict[str, str]] = dict(_OPERATION_SCOPE_MAP)
    LEAST_PRIVILEGE_SCOPES: ClassVar[set[str]] = set(DEFAULT_CONSENT_SCOPES)

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise ValueError("gamma must be positive.")
        self.supported_engines = {
            self._normalize_engine(engine) for engine in self.supported_engines
        }
        ensure_full_consent(
            self.consent,
            scope=self.OPERATION_SCOPE_MAP.get("deploy"),
            actor=f"{self.name}.bootstrap",
        )

    # ------------------------------------------------------------------
    # Consent helpers
    # ------------------------------------------------------------------
    def _require_scope(self, operation: str) -> None:
        """Ensure the agent has full consent for the requested operation."""

        ensure_full_consent(
            self.consent,
            scope=self.OPERATION_SCOPE_MAP.get(operation),
            actor=f"{self.name}.{operation}",
        )

    # ------------------------------------------------------------------
    # Engine helpers
    # ------------------------------------------------------------------
    def _normalize_engine(self, engine: str) -> str:
        """Return a lowercase, trimmed engine name."""

        engine_normalized = engine.strip().lower()
        if not engine_normalized:
            raise ValueError("Engine name must be a non-empty string.")
        return engine_normalized

    def supports_engine(self, engine: str) -> bool:
        """Return ``True`` when ``engine`` is present in the supported set."""

        try:
            return self._normalize_engine(engine) in self.supported_engines
        except ValueError:
            return False

    def list_supported_engines(self) -> list[str]:
        """Return a sorted snapshot of supported engines."""

        return sorted(self.supported_engines)

    def add_supported_engine(self, engine: str) -> None:
        """Register a new game engine."""

        self._require_scope("add_supported_engine")
        self.supported_engines.add(self._normalize_engine(engine))

    def remove_supported_engine(self, engine: str) -> None:
        """Remove an engine from the supported set."""

        self._require_scope("remove_supported_engine")
        normalized = self._normalize_engine(engine)
        if normalized not in self.supported_engines:
            raise ValueError(f"Engine '{engine}' is not currently supported.")
        self.supported_engines.remove(normalized)

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------
    def deploy(self) -> str:
        """Return a message indicating the agent is ready for use."""

        self._require_scope("deploy")
        return f"{self.name} ready to generate novels!"

    def create_game(self, engine: str, include_weapons: bool = False) -> str:
        """Create a basic game using a supported engine without weapons."""

        self._require_scope("create_game")
        normalized = self._normalize_engine(engine)
        if normalized not in self.supported_engines:
            supported = ", ".join(sorted(self.supported_engines))
            raise ValueError(f"Unsupported engine. Choose one of: {supported}.")
        if include_weapons:
            raise ValueError("Weapons are not allowed in generated games.")
        message = f"Creating a {normalized.capitalize()} game without weapons..."
        self._created_games.append(normalized)
        return message

    def generate_story_series(
        self, genres: Sequence[str], *, protagonist: str
    ) -> list[str]:
        """Return a series of story snippets for the supplied ``genres``."""

        self._require_scope("generate_story_series")
        if not protagonist.strip():
            raise ValueError("Protagonist must be a non-empty string.")
        stories = []
        for index, genre in enumerate(genres, start=1):
            topic = genre.strip() or "untitled"
            stories.append(
                f"Episode {index} ({topic}): {protagonist} faces an unexpected twist."
            )
        return stories

    def generate_code_snippet(self, prompt: str, *, language: str = "python") -> str:
        """Return a starter code snippet for the given ``language``."""

        self._require_scope("generate_code_snippet")
        lang_key = language.strip().lower()
        try:
            template = self.SAMPLE_SNIPPETS[lang_key]
        except KeyError as exc:  # pragma: no cover - defensive guard
            supported = ", ".join(sorted(self.SAMPLE_SNIPPETS))
            raise ValueError(f"Unsupported language: {language}. [{supported}]") from exc
        header = f"# {prompt.strip() or 'TODO'}\n"
        return header + template

    def validate_scopes(self, scopes: Iterable[str]) -> frozenset[str]:
        """Validate ``scopes`` returning the normalised set."""

        self._require_scope("validate_scopes")
        cleaned = {scope.strip() for scope in scopes}
        if not cleaned or any(not scope for scope in cleaned):
            raise ValueError("Invalid scopes: empty values are not allowed.")
        if not cleaned.issubset(self.LEAST_PRIVILEGE_SCOPES):
            raise ValueError("Invalid scopes requested.")
        return frozenset(cleaned)

    def set_gamma(self, value: float) -> None:
        """Update the novelty factor used by the agent."""

        self._require_scope("set_gamma")
        if value <= 0:
            raise ValueError("gamma must be positive.")
        self.gamma = value

    def write_novel(self, title: str, chapters: int = 3) -> list[str]:
        """Return a simple outline for a multi-chapter novel."""

        self._require_scope("write_novel")
        if chapters <= 0:
            raise ValueError("At least one chapter is required.")
        title_clean = title.strip() or "Untitled"
        return [f"Chapter {index}: TBD" for index in range(1, chapters + 1)]

    def generate_storyline(self, protagonist: str, setting: str) -> str:
        """Generate a simple storyline for a given protagonist and setting.

        Args:
            protagonist: Name of the main character.
            setting: Location where the story takes place.

        Returns:
            A short storyline sentence.
        """
        return (
            f"{protagonist} embarks on an adventure in {setting}, "
            "discovering the true meaning of courage."
        )


__all__ = [
    "AutoNovelAgent",
    "DEFAULT_CONSENT_SCOPES",
    "DEFAULT_SUPPORTED_ENGINES",
]
if __name__ == "__main__":
    agent = AutoNovelAgent()
    agent.deploy()
    agent.create_game("unity")
    print(agent.generate_storyline("Ada", "a digital forest"))
