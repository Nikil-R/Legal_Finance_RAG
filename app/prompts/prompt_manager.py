"""
Prompt Manager — handles loading, caching, and formatting of versioned YAML prompts.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.utils.logger import get_logger

logger = get_logger(__name__)


class PromptManager:
    """Manages versioned prompts stored in YAML files."""

    def __init__(self, prompts_dir: str | None = None) -> None:
        if prompts_dir is None:
            # Default to the directory where this file sits
            prompts_dir = str(Path(__file__).parent)

        self.prompts_dir = Path(prompts_dir)
        self._cache: dict[str, dict] = {}
        logger.info("PromptManager initialized with directory: %s", self.prompts_dir)

    def load_prompt(self, version: str = "v1") -> dict:
        """
        Loads the YAML file: system_prompt_{version}.yaml

        Returns a dictionary containing the prompt contents.
        Caches the result for performance.
        """
        # Caching disabled for development so changes to YAML take effect immediately
        # if version in self._cache:
        #     return self._cache[version]

        filename = f"system_prompt_{version}.yaml"
        filepath = self.prompts_dir / filename

        if not filepath.exists():
            error_msg = f"Prompt version '{version}' not found at {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                prompt_data = yaml.safe_load(f)

            self._cache[version] = prompt_data
            logger.info("Loaded prompt version: %s", version)
            return prompt_data
        except Exception as e:
            logger.error("Error loading prompt YAML: %s", str(e))
            raise

    def format_user_prompt(self, version: str, context: str, question: str) -> str:
        """Loads and formats the user prompt template with context and question."""
        prompt_data = self.load_prompt(version)
        template = prompt_data.get("user_prompt_template", "")
        return template.format(context=context, question=question)

    def get_system_prompt(self, version: str = "v1") -> str:
        """Returns the system prompt string for the given version."""
        prompt_data = self.load_prompt(version)
        return prompt_data.get("system_prompt", "")

    def get_parameters(self, version: str = "v1") -> dict:
        """Returns the parameters dictionary for the given version."""
        prompt_data = self.load_prompt(version)
        return prompt_data.get("parameters", {})

    def list_versions(self) -> list[str]:
        """Scans prompts directory for all system_prompt_*.yaml files."""
        versions = []
        for file in self.prompts_dir.glob("system_prompt_*.yaml"):
            # Extract 'v1' from 'system_prompt_v1.yaml'
            version = file.stem.replace("system_prompt_", "")
            versions.append(version)
        return sorted(versions)
