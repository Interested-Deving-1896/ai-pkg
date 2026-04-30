from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Label, Static, Input
from textual.message import Message
from textual.reactive import reactive

from ai_pkg.backends.base import SuggestionResult
from ai_pkg.config import PkgConfig


class PackageToggle(Static):
    """Custom toggle widget — keyboard and mouse friendly."""

    BINDINGS = [
        ("enter", "toggle", "Toggle"),
        ("space", "toggle", "Toggle"),
    ]

    def __init__(self, index: int, pkg, **kwargs):
        super().__init__(**kwargs)
        self.can_focus = True
        self.index = index
        self.pkg = pkg
        self.value = pkg.available
        self.disabled_pkg = not pkg.available
        self._refresh_label()

    def _refresh_label(self):
        if self.disabled_pkg:
            desc = self.pkg.description or self.pkg.reason or ""
            src = "AUR" if self.pkg.source == "aur" else "pac"
            text = f"[dim][ ] {self.pkg.name} [{src}] (not found) — {desc}[/dim]"
        else:
            box = "●" if self.value else "○"
            box_color = "bold green" if self.value else "dim white"
            src_tag = (
                "[bold #89b4fa]\\[AUR][/]" if self.pkg.source == "aur"
                else "[bold #a6e3a1]\\[pac][/]"
            )
            desc = self.pkg.description or self.pkg.reason or ""
            name_color = "bold white" if self.value else "#cdd6f4"
            text = (
                f"[{box_color}]{box}[/] [{name_color}]{self.pkg.name}[/] "
                f"{src_tag}[dim #6c7086] — {desc}[/dim #6c7086]"
            )
        self.update(text)

    def action_toggle(self) -> None:
        if self.disabled_pkg:
            return
        self.value = not self.value
        self._refresh_label()
        # Notify parent PlanWidget to update counter
        self.post_message(PlanWidget.SelectionChanged())

    def on_click(self, _: events.Click) -> None:
        if not self.disabled_pkg:
            self.action_toggle()
            self.focus()


class CommandInput(Horizontal):
    """An editable command row."""

    def __init__(self, index: int, command: str, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.initial_command = command

    def compose(self) -> ComposeResult:
        yield Static("[dim #6c7086]$[/]", classes="cmd-dollar")
        yield Input(
            value=self.initial_command,
            id=f"cmd-{self.index}",
            classes="cmd-input",
        )

    def get_value(self) -> str:
        return self.query_one(Input).value


class PlanWidget(Vertical):
    """Inline widget: select packages + edit commands + confirm."""

    class PlanRun(Message):
        def __init__(self, widget: "PlanWidget", plan: SuggestionResult, deselected: list) -> None:
            self.widget = widget
            self.plan = plan
            self.deselected = deselected
            super().__init__()

    class PlanCancel(Message):
        def __init__(self, widget: "PlanWidget") -> None:
            self.widget = widget
            super().__init__()

    class SelectionChanged(Message):
        """Posted by PackageToggle when its value flips."""

    # Intercept arrows at this level so VerticalScroll doesn't steal them
    BINDINGS = [
        ("up",    "move_up",   "Up"),
        ("down",  "move_down", "Down"),
        ("k",     "move_up",   "Up (vim)"),
        ("j",     "move_down", "Down (vim)"),
        ("a",     "select_all",   "Select all"),
        ("n",     "select_none",  "Deselect all"),
        ("r",     "do_run",    "Run"),
        ("escape","do_cancel", "Cancel"),
    ]

    def __init__(self, plan: SuggestionResult, pkg_config: PkgConfig, **kwargs):
        super().__init__(**kwargs)
        self.plan = plan
        self.pkg_config = pkg_config
        self._n_toggleable = sum(1 for p in plan.packages if p.available)
        self._n_steps = len(plan.env_steps)

    def _selected_count(self) -> int:
        try:
            return sum(
                1 for i, p in enumerate(self.plan.packages)
                if p.available and self.query_one(f"#pkg-{i}", PackageToggle).value
            )
        except Exception:
            return 0

    def _update_counter(self) -> None:
        if self._n_toggleable == 0:
            return
        try:
            lbl = self.query_one("#sel-counter", Label)
            sel = self._selected_count()
            lbl.update(
                f"[bold #cba6f7]{sel}[/][dim #6c7086]/{self._n_toggleable} selected[/]"
            )
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        # ── Header ────────────────────────────────────────────────────────────
        with Horizontal(classes="plan-header"):
            yield Label("[bold #cba6f7]◆ Installation Plan[/]", classes="plan-title")
            if self._n_toggleable > 0:
                yield Label(
                    f"[bold #cba6f7]{self._n_toggleable}[/][dim #6c7086]/{self._n_toggleable} selected[/]",
                    id="sel-counter",
                    classes="sel-counter",
                )

        # ── Keyboard hint bar ─────────────────────────────────────────────────
        yield Static(
            "[dim #6c7086]"
            " [bold #89b4fa]↑↓[/] / [bold #89b4fa]j k[/] navigate"
            "  [bold #89b4fa]Space[/] toggle"
            "  [bold #89b4fa]a[/] all  [bold #89b4fa]n[/] none"
            "  [bold #a6e3a1]r[/] run"
            "  [bold #f38ba8]Esc[/] cancel"
            "[/]",
            classes="plan-hint",
        )

        # ── Packages ──────────────────────────────────────────────────────────
        if self.plan.packages:
            for i, p in enumerate(self.plan.packages):
                yield PackageToggle(i, p, id=f"pkg-{i}", classes="pkg-toggle")
        else:
            yield Label("[dim]No packages to install.[/dim]")

        # ── Commands ──────────────────────────────────────────────────────────
        if self.plan.env_steps:
            yield Static(
                "[dim #6c7086]── Commands to run [bold]Tab[/] to focus and edit ──[/]",
                classes="section-sep",
            )
            for i, s in enumerate(self.plan.env_steps):
                yield CommandInput(i, s, id=f"cmd-row-{i}", classes="cmd-row")

        # ── Actions ───────────────────────────────────────────────────────────
        yield Static("", classes="spacer")
        with Horizontal(classes="buttons"):
            yield Button("  Esc  Cancel / Refine", id="cancel-btn")
            yield Button("  r  ▶ Run Selected", id="run-btn")

    # ── Reactive: update counter when any toggle changes ─────────────────────

    def on_plan_widget_selection_changed(self, _: "PlanWidget.SelectionChanged") -> None:
        self._update_counter()

    # ── Focus navigation ──────────────────────────────────────────────────────

    def action_move_up(self) -> None:
        self.screen.focus_previous()

    def action_move_down(self) -> None:
        self.screen.focus_next()

    # ── Bulk select ───────────────────────────────────────────────────────────

    def action_select_all(self) -> None:
        for i, p in enumerate(self.plan.packages):
            if p.available:
                t = self.query_one(f"#pkg-{i}", PackageToggle)
                t.value = True
                t._refresh_label()
        self._update_counter()

    def action_select_none(self) -> None:
        for i, p in enumerate(self.plan.packages):
            if p.available:
                t = self.query_one(f"#pkg-{i}", PackageToggle)
                t.value = False
                t._refresh_label()
        self._update_counter()

    # ── Run / Cancel shortcuts ────────────────────────────────────────────────

    def action_do_run(self) -> None:
        self._emit_run()

    def action_do_cancel(self) -> None:
        self.post_message(self.PlanCancel(self))

    def _emit_run(self) -> None:
        deselected = []
        if self.plan.packages:
            selected = []
            for i, p in enumerate(self.plan.packages):
                if self.query_one(f"#pkg-{i}", PackageToggle).value:
                    selected.append(p)
                else:
                    deselected.append(p)
            self.plan.packages = selected

        if self.plan.env_steps:
            self.plan.env_steps = [
                self.query_one(f"#cmd-row-{i}", CommandInput).get_value()
                for i in range(self._n_steps)
            ]
        self.post_message(self.PlanRun(self, self.plan, deselected))

    # ── Button press ─────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.post_message(self.PlanCancel(self))
        elif event.button.id == "run-btn":
            self._emit_run()
