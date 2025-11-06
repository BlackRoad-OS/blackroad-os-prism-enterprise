"""Runtime implementation of the AutoNovel agent.

The project documentation makes frequent references to an "AutoNovel" agent
that can ideate small games, produce story snippets, and help with coding
exercises.  The previous incarnation of this module had an unresolved merge
conflict which left most behaviours unusable.  This implementation restores the
agent so that it behaves like a real piece of production code that can be
imported, instantiated and exercised from tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Iterable

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

    SAMPLE_SNIPPETS: ClassVar[dict[str, str]] = {
        "python": "def solve():\n    pass\n",
        "javascript": "function solve() {\n  return null;\n}\n",
        "java": "class Solution {\n    void solve() {\n    }\n}\n",
    }
    OPERATION_SCOPE_MAP: ClassVar[dict[str, str]] = dict(_OPERATION_SCOPE_MAP)
    LEAST_PRIVILEGE_SCOPES: ClassVar[set[str]] = set(DEFAULT_CONSENT_SCOPES)

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise ValueError("gamma must be positive.")
        self.supported_engines = {
            self._normalize_engine(engine) for engine in self.supported_engines
        }

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
        Args:
            engine: Game engine to use.
            include_weapons: If True, raise a ``ValueError`` because weapons are not
                allowed.

        Raises:
            ValueError: If ``engine`` is empty or ``include_weapons`` is ``True``.
        """
        engine_clean = engine.strip()
        if not engine_clean:
            raise ValueError("Engine name must be a non-empty string.")
        engine_lower = engine_clean.lower()
        if not self.supports_engine(engine_lower):
            supported = ", ".join(sorted(self.SUPPORTED_ENGINES))
            raise ValueError(f"Unsupported engine. Choose one of: {supported}.")
        if include_weapons:
            raise ValueError("Weapons are not allowed in generated games.")
        print(f"Creating a {engine_lower.capitalize()} game without weapons...")

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
        Args:
            engine: Name of the engine to allow.

        Raises:
            TypeError: If ``engine`` is not a string.
            ValueError: If ``engine`` is empty or only whitespace.
        """
        if not isinstance(engine, str):
            raise TypeError("Engine name must be provided as a string.")

            ValueError: If ``engine`` is empty or only whitespace.
        """
        engine_clean = engine.strip()
        if not engine_clean:
            raise ValueError("Engine name must be a non-empty string.")
        self.SUPPORTED_ENGINES.add(engine_clean.lower())

    def remove_supported_engine(self, engine: str) -> None:
        """Remove a game engine, raising ``ValueError`` if it is unknown."""

        self._require_scope("remove_supported_engine")
        normalized = self._normalize_engine(engine)
        if normalized not in self.supported_engines:
            supported = ", ".join(self.list_supported_engines())
            raise ValueError(
                f"Engine '{normalized}' is not supported. "
                f"Supported engines: {supported}."
            )
        self.supported_engines.remove(normalized)

    # ------------------------------------------------------------------
    # Primary abilities
    # ------------------------------------------------------------------
    def deploy(self) -> str:
        """Deploy the agent by returning a greeting."""

        self._require_scope("deploy")
        message = f"{self.name} deployed and ready to generate novels!"
        print(message)
        return message

    def _indefinite_article(self, engine_name: str) -> str:
        """Return the appropriate indefinite article for ``engine_name``."""

        if not engine_name:
            return "a"
        lower = engine_name.lower()
        if lower.startswith(("honest", "hour", "heir")):
            return "an"
        if lower[0] in "aeiou":
            if lower.startswith(("uni", "use", "ufo", "one", "eu")):
                return "a"
            return "an"
        return "a"

    def _build_creation_message(self, engine_lower: str) -> str:
        """Build the message describing the created game."""

        article = self._indefinite_article(engine_lower)
        return f"Creating {article} {engine_lower.capitalize()} game without weapons..."

    def create_game(self, engine: str, include_weapons: bool = False) -> str:
        """Create a basic game using a supported engine."""

        self._require_scope("create_game")
        normalized = self._normalize_engine(engine)
        if normalized not in self.supported_engines:
            supported = ", ".join(self.list_supported_engines())
            raise ValueError(
                "Unsupported engine "
                f"'{normalized}'. Supported engines: {supported}. "
                "Use add_supported_engine to register new engines."
            )
        if include_weapons:
            raise ValueError("Weapons are not allowed in generated games.")

        message = self._build_creation_message(normalized)
        print(message)
        return message

    def generate_game_idea(self, theme: str, engine: str) -> str:
        """Return a short description for a themed game."""

        self._require_scope("generate_game_idea")
        theme_clean = theme.strip()
        if not theme_clean:
            raise ValueError("Theme must be a non-empty string.")

        normalized = self._normalize_engine(engine)
        if normalized not in self.supported_engines:
            supported = ", ".join(self.list_supported_engines())
            raise ValueError(f"Unsupported engine. Choose one of: {supported}.")

        return (
            f"Imagine a {theme_clean} adventure crafted with "
            f"{normalized.capitalize()} where creativity reigns."
        )

    # ------------------------------------------------------------------
    # Story helpers
    # ------------------------------------------------------------------
    def generate_story(self, theme: str, protagonist: str = "An adventurer") -> str:
        """Generate a short themed story."""

        self._require_scope("generate_story")
        theme_clean = theme.strip()
        if not theme_clean:
            raise ValueError("Theme must be a non-empty string.")

        protagonist_clean = protagonist.strip() or "An adventurer"
        excitement = "!" * max(1, int(self.gamma))
        return (
            f"{protagonist_clean} embarks on a {theme_clean} journey, "
            f"discovering wonders along the way{excitement}"
        )

    def generate_story_series(
        self, themes: Iterable[str], protagonist: str = "An adventurer"
    ) -> list[str]:
        """Generate short stories for each theme in ``themes``."""

        self._require_scope("generate_story_series")
        stories: list[str] = []
        for theme in themes:
            theme_text = str(theme).strip()
            if not theme_text:
                raise ValueError("Each theme must be a non-empty string.")
            stories.append(self.generate_story(theme_text, protagonist))
        return stories

    def write_novel(self, title: str, chapters: int = 3) -> list[str]:
        """Create a simple outline for a novel."""

        self._require_scope("write_novel")
        title_clean = title.strip()
        if not title_clean:
            raise ValueError("Title must be a non-empty string.")
        if chapters < 1:
            raise ValueError("Novel must have at least one chapter.")

        outline = [f"Chapter {i}: TBD" for i in range(1, chapters + 1)]
        print(f"Drafting novel '{title_clean}' with {chapters} chapters...")
        for heading in outline:
            print(heading)
        return outline

    # ------------------------------------------------------------------
    # Coding and English assistance
    # ------------------------------------------------------------------
    def generate_coding_challenge(self, topic: str, difficulty: str = "medium") -> str:
        """Return a concise coding challenge prompt."""

        self._require_scope("generate_coding_challenge")
        topic_clean = topic.strip()
        if not topic_clean:
            raise ValueError("Topic must be a non-empty string.")

        difficulty_normalized = difficulty.lower()
        if difficulty_normalized not in {"easy", "medium", "hard"}:
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'.")

        return (
            f"[{difficulty_normalized.title()}] Implement a solution that addresses "
            f"the '{topic_clean}' challenge. Describe your approach before coding "
            "and ensure the solution handles edge cases."
        )

    def generate_code_snippet(self, description: str, language: str = "python") -> str:
        """Produce a starter code snippet in the requested language."""

        self._require_scope("generate_code_snippet")
        description_clean = description.strip()
        if not description_clean:
            raise ValueError("Description must be provided for code generation.")

        language_lower = language.strip().lower()
        snippet = self.SAMPLE_SNIPPETS.get(language_lower)
        if snippet is None:
            supported_languages = ", ".join(sorted(self.SAMPLE_SNIPPETS))
            raise ValueError(
                f"Unsupported language '{language_lower}'. "
                f"Supported languages: {supported_languages}."
            )

        comment_prefix = "#" if language_lower == "python" else "//"
        return f"{comment_prefix} TODO: {description_clean}\n{snippet}"

    def proofread_paragraph(self, paragraph: str) -> str:
        """Proofread a paragraph by normalising spacing and punctuation."""

        self._require_scope("proofread_paragraph")
        if not paragraph or not paragraph.strip():
            raise ValueError("Paragraph must be a non-empty string.")

        trimmed = " ".join(paragraph.split())
        sentence = trimmed[0].upper() + trimmed[1:]
        if sentence[-1] not in ".!?":
            sentence += "."
        return sentence

    def validate_scopes(self, requested_scopes: Iterable[str]) -> None:
        """Validate that requested scopes adhere to the least-privilege policy."""

        self._require_scope("validate_scopes")
        scopes = {scope.strip() for scope in requested_scopes if scope.strip()}
        invalid_scopes = sorted(scopes - self.LEAST_PRIVILEGE_SCOPES)
        if invalid_scopes:
            joined = ", ".join(invalid_scopes)
            raise ValueError(f"Invalid scopes: {joined}.")

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def set_gamma(self, gamma: float) -> None:
        """Update the creativity scaling factor."""

        self._require_scope("set_gamma")
        if gamma <= 0:
            raise ValueError("gamma must be positive.")
        self.gamma = gamma


def main() -> None:
    """Run a tiny demonstration when executed as a script."""

    consent = ConsentRecord.full(
        scopes=DEFAULT_CONSENT_SCOPES,
        evidence="AutoNovelAgent demo execution",
    )
    agent = AutoNovelAgent(consent=consent)
    agent.deploy()
    agent.create_game("unity")
    print(agent.generate_story("mystery", protagonist="Explorer"))
    agent.write_novel("The Adventure")


if __name__ == "__main__":
    main()


__all__ = ["AutoNovelAgent", "DEFAULT_SUPPORTED_ENGINES", "DEFAULT_CONSENT_SCOPES"]
