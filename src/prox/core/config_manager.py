import json
from typing import List, Optional
from src.prox.core import paths
from src.prox.models.base_models import Settings, TicketTemplate

class ConfigManager:
    """
    Manages loading and saving application settings and ticket templates from JSON files.
    Handles initial file creation with default values.
    """
    def __init__(self):
        # Ensure the directories exist before any file operations
        paths.ensure_app_dirs_exist()

    def load_settings(self) -> Settings:
        """
        Loads the application settings. If the file doesn't exist, it creates
        it with default settings.
        """
        if not paths.SETTINGS_FILE.exists():
            default_settings = Settings()
            self.save_settings(default_settings)
            return default_settings

        with open(paths.SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Settings.model_validate(data)

    def save_settings(self, settings: Settings):
        """Saves the application settings to its JSON file."""
        with open(paths.SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings.model_dump(), f, indent=4)

    def load_ticket_templates(self) -> List[TicketTemplate]:
        """
        Loads all ticket templates. If the file doesn't exist, it returns an
        empty list.
        """
        if not paths.TICKET_TEMPLATES_FILE.exists():
            return []

        with open(paths.TICKET_TEMPLATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [TicketTemplate.model_validate(item) for item in data]

    def save_ticket_templates(self, templates: List[TicketTemplate]):
        """Saves a list of ticket templates to its JSON file."""
        with open(paths.TICKET_TEMPLATES_FILE, "w", encoding="utf-8") as f:
            # Pydantic's json serializer handles date objects correctly
            json_data = [template.model_dump(mode="json") for template in templates]
            json.dump(json_data, f, indent=4)

    def get_template_by_id(self, template_id: str) -> Optional[TicketTemplate]:
        """Retrieves a single ticket template by its ID."""
        templates = self.load_ticket_templates()
        for template in templates:
            if template.template_id == template_id:
                return template
        return None
