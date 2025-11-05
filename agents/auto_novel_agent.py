"""Auto novel agent with creative and coding abilities."""

from __future__ import annotations

<<<<<<< main
from dataclasses import dataclass, field
from typing import ClassVar, Iterable


DEFAULT_SUPPORTED_ENGINES: tuple[str, ...] = ("unity", "unreal")
=======
from dataclasses import dataclass
from typing import ClassVar
>>>>>>> origin/codex/complete-next-step-of-project-582c2w


@dataclass
class AutoNovelAgent:
    """A small agent that can build games and craft stories."""

    name: str = "AutoNovelAgent"
    gamma: float = 1.0
    supported_engines: set[str] = field(
        default_factory=lambda: set(DEFAULT_SUPPORTED_ENGINES)
    )

    SAMPLE_SNIPPETS: ClassVar[dict[str, str]] = {
        "python": "def solve():\n    pass\n",
        "javascript": "function solve() {\n  return null;\n}\n",
        "java": "class Solution {\n    void solve() {\n    }\n}\n",
    }
    LEAST_PRIVILEGE_SCOPES: ClassVar[set[str]] = {"outline:read", "outline:write"}

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise ValueError("gamma must be positive.")
        self.supported_engines = {
            self._normalize_engine(engine) for engine in self.supported_engines
        }

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

        self.supported_engines.add(self._normalize_engine(engine))

    def remove_supported_engine(self, engine: str) -> None:
        """Remove a game engine, raising ``ValueError`` if it is unknown."""

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
    def deploy(self) -> None:
        """Deploy the agent by printing a greeting."""

        print(f"{self.name} deployed and ready to generate novels!")

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

<<<<<<< main
        message = self._build_creation_message(normalized)
        print(message)
        return message

    def generate_game_idea(self, theme: str, engine: str) -> str:
        """Return a short description for a themed game."""

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

        stories: list[str] = []
        for theme in themes:
            theme_text = str(theme).strip()
            if not theme_text:
                raise ValueError("Each theme must be a non-empty string.")
            stories.append(self.generate_story(theme_text, protagonist))
        return stories

    # ------------------------------------------------------------------
    # Coding and English assistance
    # ------------------------------------------------------------------
    def generate_coding_challenge(self, topic: str, difficulty: str = "medium") -> str:
        """Return a concise coding challenge prompt."""

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

        if not paragraph or not paragraph.strip():
            raise ValueError("Paragraph must be a non-empty string.")

        trimmed = " ".join(paragraph.split())
        sentence = trimmed[0].upper() + trimmed[1:]
        if sentence[-1] not in ".!?":
            sentence += "."
        return sentence

    def validate_scopes(self, requested_scopes: Iterable[str]) -> None:
        """Validate that requested scopes adhere to the least-privilege policy."""

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

        if gamma <= 0:
            raise ValueError("gamma must be positive.")
        self.gamma = gamma


def main() -> None:
    """Run a tiny demonstration when executed as a script."""
=======
    def list_supported_engines(self) -> list[str]:
        """Return a list of supported game engines."""
        return sorted(self.SUPPORTED_ENGINES)

    def write_novel(self, title: str, chapters: int = 3) -> list[str]:
        """Create a simple outline for a novel.

        Args:
            title: Title of the novel to draft.
            chapters: Number of chapter headings to generate.

        Returns:
            A list of generated chapter headings.
        """
        if chapters < 1:
            raise ValueError("Novel must have at least one chapter.")

        outline = [f"Chapter {i}: TBD" for i in range(1, chapters + 1)]
        print(f"Drafting novel '{title}' with {chapters} chapters...")
        for heading in outline:
            print(heading)
        return outline

>>>>>>> origin/codex/complete-next-step-of-project-582c2w

    agent = AutoNovelAgent()
    agent.deploy()
    agent.create_game("unity")
<<<<<<< main
    print(agent.generate_story("mystery", protagonist="Explorer"))


if __name__ == "__main__":
    main()
=======
    agent.write_novel("The Adventure")
>>>>>>> origin/codex/complete-next-step-of-project-582c2w
