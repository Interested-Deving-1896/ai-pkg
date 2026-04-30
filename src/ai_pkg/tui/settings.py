"""Settings modal for AI-PKG."""
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Select, Button, Label
from textual.containers import Vertical, Horizontal, Container

from ai_pkg.config import load_config, save_config

class SettingsModal(ModalScreen[bool]):
    """Modal dialog to change AI backend, specific models, and API keys."""
    
    def compose(self) -> ComposeResult:
        self.config = load_config()
        
        backends = [
            ("gemini", "gemini"),
            ("openai", "openai"),
            ("groq", "groq"),
            ("ollama", "ollama"),
        ]

        aur_helpers = [
            ("yay", "yay"),
            ("paru", "paru"),
        ]
        
        with Vertical(id="settings-dialog"):
            yield Label("⚙️  Configuration Settings", id="settings-title")
            
            yield Label("AI Provider:", classes="settings-label")
            yield Select(backends, value=self.config.ai.model, id="backend-select")
            
            yield Label("Model Name:", classes="settings-label")
            model_val = getattr(self.config.ai, f"{self.config.ai.model}_model", "")
            yield Input(value=model_val, id="model-name-input")
            
            yield Label("API Key (or Base URL):", classes="settings-label")
            key_val = getattr(self.config.ai, f"{self.config.ai.model}_api_key", "")
            if self.config.ai.model == "ollama":
                key_val = self.config.ai.ollama_base_url
            elif self.config.ai.model == "openai" and not key_val:
                 pass

            yield Input(value=key_val, id="key-input", password=(self.config.ai.model != "ollama"))

            yield Label("AUR Helper:", classes="settings-label")
            yield Select(aur_helpers, value=self.config.pkg.aur_helper, id="aur-select")
            
            with Horizontal(id="settings-buttons"):
                yield Button("Cancel", variant="error", id="cancel-btn")
                yield Button("Save & Close", variant="success", id="save-btn")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "backend-select":
            backend = event.select.value
            
            # Update Model Name Input
            model_inp = self.query_one("#model-name-input", Input)
            model_inp.value = getattr(self.config.ai, f"{backend}_model", "")

            # Update API Key / Base URL Input
            key_inp = self.query_one("#key-input", Input)
            if backend == "ollama":
                key_inp.value = self.config.ai.ollama_base_url
                key_inp.password = False
            else:
                key_inp.value = getattr(self.config.ai, f"{backend}_api_key", "")
                key_inp.password = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            backend = self.query_one("#backend-select", Select).value
            model_name = self.query_one("#model-name-input", Input).value
            key = self.query_one("#key-input", Input).value
            aur_helper = self.query_one("#aur-select", Select).value
            
            self.config.ai.model = backend
            self.config.pkg.aur_helper = aur_helper
            
            setattr(self.config.ai, f"{backend}_model", model_name)
            
            if backend == "ollama":
                self.config.ai.ollama_base_url = key
            else:
                setattr(self.config.ai, f"{backend}_api_key", key)
                
            save_config(self.config)
            self.dismiss(True)
            
        elif event.button.id == "cancel-btn":
            self.dismiss(False)
