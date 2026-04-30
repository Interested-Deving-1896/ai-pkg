"""Main Textual application for ai-pkg v2."""
import asyncio
import json
import os
from typing import List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Center
from textual.widgets import Input, RichLog, Static, Label
from textual.binding import Binding
from textual.widget import Widget
from rich.markdown import Markdown
from rich.text import Text

from ai_pkg.config import load_config
from ai_pkg.backends import get_backend
from ai_pkg.aur import enrich
from ai_pkg.doc_fetcher import fetch_docs, build_docs_context
from ai_pkg.known_steps import apply_known_steps, build_kb_context
from ai_pkg.banner import BANNER_ART
from .settings import SettingsModal
from .plan_widget import PlanWidget, PackageToggle, CommandInput

class ChatInput(Input):
    BINDINGS = [
        Binding("up", "history_up", "Previous prompt", show=False),
        Binding("down", "history_down", "Next prompt", show=False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history: list[str] = []
        self.history_idx: int = -1
        self.current_draft: str = ""

    def action_history_up(self) -> None:
        if not self.history:
            return
        if self.history_idx == -1:
            self.current_draft = self.value
            self.history_idx = len(self.history) - 1
        elif self.history_idx > 0:
            self.history_idx -= 1
        self.value = self.history[self.history_idx]
        self.cursor_position = len(self.value)

    def action_history_down(self) -> None:
        if self.history_idx == -1:
            return
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.value = self.history[self.history_idx]
        else:
            self.history_idx = -1
            self.value = self.current_draft
        self.cursor_position = len(self.value)


class AIPkgApp(App):
    """Textual TUI mimicking the Cline / Gemini CLI aesthetic."""
    
    CSS_PATH = "app.tcss"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("f2", "open_settings", "Settings"),
    ]

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.messages = []
        self.pending_plan = None

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="chat-scroll")
        with Container(id="input-container"):
            yield ChatInput(placeholder="e.g., Install docker, start the service, and add me to the docker group...", id="chat-input")
        with Horizontal(id="status-bar"):
            yield Static(f"{os.getcwd()}", id="status-left")
            yield Static("", id="footer-hints")
            yield Static("gemini-2.5-pro", id="status-right")

    async def append_chat(self, widget: Widget) -> None:
        """Helper to append a widget to the chat and scroll down."""
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        await scroll.mount(widget)
        scroll.scroll_end(animate=False)

    def on_mount(self) -> None:
        self.update_status()
        self._set_footer(self._HINTS_CHAT)
        self.print_banner()
        self.query_one(ChatInput).focus()

    # ── Context-sensitive footer hints ───────────────────────────────────────

    _HINTS_CHAT = (
        "[dim #6c7086]"
        "[bold #89b4fa]Enter[/] send"
        "  [bold #89b4fa]↑↓[/] history"
        "  [bold #89b4fa]F2[/] settings"
        "  [bold #89b4fa]Ctrl+C[/] quit"
        "  [dim italic](Shift+Drag to copy)[/]"
        "[/]"
    )
    _HINTS_PLAN = (
        "[dim #6c7086]"
        "[bold #89b4fa]↑↓/jk[/] navigate"
        "  [bold #89b4fa]Spc[/] toggle"
        "  [bold #89b4fa]a[/] all  [bold #89b4fa]n[/] none"
        "  [bold #a6e3a1]r[/] run"
        "  [bold #f38ba8]Esc[/] cancel"
        "[/]"
    )
    _HINTS_CMD = (
        "[dim #6c7086]"
        "[bold #89b4fa]Tab[/] next cmd"
        "  [bold #89b4fa]Shift+Tab[/] prev"
        "  [bold #a6e3a1]r[/] run"
        "  [bold #f38ba8]Esc[/] cancel"
        "[/]"
    )

    def _set_footer(self, text: str) -> None:
        try:
            self.query_one("#footer-hints", Static).update(text)
        except Exception:
            pass

    def on_focus(self, event) -> None:  # noqa: ANN001
        w = event.widget
        if isinstance(w, PackageToggle):
            self._set_footer(self._HINTS_PLAN)
        elif isinstance(w, Input) and w.has_class("cmd-input"):
            self._set_footer(self._HINTS_CMD)
        else:
            self._set_footer(self._HINTS_CHAT)

    def update_status(self) -> None:
        self.config = load_config()
        right = self.query_one("#status-right", Static)
        provider = self.config.ai.model
        model_name = getattr(self.config.ai, f"{provider}_model", provider)
        right.update(f"{model_name} ({self.config.pkg.aur_helper})")

    def print_banner(self) -> None:
        scroll = self.query_one("#chat-scroll", VerticalScroll)
        lines = BANNER_ART.strip("\n").splitlines()
        max_len = max(len(line) for line in lines)
        
        # Color palette: Cyan -> Blue -> Purple -> Pink
        colors = ["#89b4fa", "#b4befe", "#cba6f7", "#f38ba8", "#eba0ac"]
        
        banner_text = Text()
        for line in lines:
            for x, char in enumerate(line):
                # Calculate interpolation factor
                factor = x / max(1, max_len - 1)
                idx = int(factor * (len(colors) - 1))
                banner_text.append(char, style=f"bold {colors[idx]}")
            banner_text.append("\n")
            
        from textual.containers import Center
        scroll.mount(Center(Static(banner_text, classes="centered-panel")))
        
        welcome_text = "\n[bold white]Welcome to AI-PKG v2[/bold white] — [dim]The Intelligent Arch Linux Package Manager[/dim]\n"
        scroll.mount(Center(Static(welcome_text, classes="centered-panel")))
        
        instructions = (
            "\n✨ [bold cyan]What can I do?[/bold cyan]\n"
            "  • Ask me to install any software or development stack.\n"
            "  • I will generate a [bold green]verified installation plan[/bold green] using official Arch Wiki docs.\n"
            "  • Review, modify, and execute commands safely with keyboard navigation.\n\n"
            "💡 [bold cyan]Example Prompt[/bold cyan]\n"
            "  [dim italic]\"Install Docker and Docker Compose. Make sure to enable the service\n"
            "  to start on boot, and add my current user to the docker group so I\n"
            "  don't have to use sudo every time.\"[/dim italic]\n\n"
            "⚙️  [bold cyan]Configuration[/bold cyan]\n"
            "  Press [bold #cba6f7 reverse] F2 [/] at any time to open Settings (change AI models & API keys).\n"
            "  Press [bold #f38ba8 reverse] Ctrl+C [/] to safely exit the application.\n\n"
            "[dim]Powered by conversational AI. Type your request below to begin...[/dim]\n"
        )
        scroll.mount(Static(instructions))

    def action_open_settings(self) -> None:
        def check_settings(saved: bool):
            if saved:
                self.update_status()
                
        self.push_screen(SettingsModal(), check_settings)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        inp = self.query_one("#chat-input", ChatInput)
        inp.value = ""
        
        if not text:
            return

        if not inp.history or inp.history[-1] != text:
            inp.history.append(text)
        inp.history_idx = -1
        inp.current_draft = ""

        inp.disabled = True
        await self.append_chat(Static(f"\n[bold cyan]>[/bold cyan] [bold]{text}[/bold]\n"))

        self.messages.append({"role": "user", "content": text})
        await self.generate_plan()

    async def generate_plan(self, retry_count: int = 0) -> None:
        inp = self.query_one("#chat-input", ChatInput)
        
        backend = get_backend(self.config)
        if not backend.is_configured:
            await self.append_chat(Static(f"[bold red]✗ {backend.name} is not configured! Press F2 to setup.[/bold red]"))
            inp.disabled = False
            inp.focus()
            return

        thinking = Static(f"[dim]Thinking ({backend.name})...[/dim]")
        await self.append_chat(thinking)
        
        result = await backend.suggest(self.messages)
        
        if result.error:
            await self.append_chat(Static(f"[bold red]Error:[/] {result.error}"))
            self.messages.pop() # remove failed prompt
            inp.disabled = False
            inp.focus()
            return

        if result.packages:
            await self.append_chat(Static("[dim]Enriching from AUR...[/dim]"))
            result.packages = await enrich(result.packages)
            
            missing_pkgs = [p for p in result.packages if not p.available]
            if missing_pkgs and retry_count < 1:
                await self.append_chat(Static("[dim]Some packages not found. Searching and asking AI to revise...[/dim]"))
                
                search_results = []
                for p in missing_pkgs:
                    proc = await asyncio.create_subprocess_exec(
                        self.config.pkg.aur_helper, "-Ss", p.name,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL
                    )
                    stdout, _ = await proc.communicate()
                    out = stdout.decode().strip()
                    if out:
                        out = "\n".join(out.splitlines()[:15])
                        search_results.append(f"Search for '{p.name}' returned:\n{out}")
                    else:
                        search_results.append(f"Search for '{p.name}' returned no results.")
                
                prompt = (
                    "The following packages in your plan were not found by the package manager:\n"
                    + "\n".join(f"- {p.name}" for p in missing_pkgs) + "\n\n"
                    "I searched the package manager and got these results:\n\n"
                    + "\n\n".join(search_results) + "\n\n"
                    "Please revise your plan using the correct package names from the search results if applicable."
                )
                self.messages.append({"role": "user", "content": prompt})
                return await self.generate_plan(retry_count=retry_count + 1)

            # ── Phase 2: Ground env_steps with KB knowledge + Arch Wiki docs ──
            available_pkgs = [p for p in result.packages if p.available]
            if available_pkgs:
                wiki_msg = Static("[dim]Reading official docs from Arch Wiki...[/dim]")
                await self.append_chat(wiki_msg)

                # Fetch wiki docs while building KB context (sync) simultaneously
                docs = await fetch_docs(available_pkgs)
                kb_context = build_kb_context(available_pkgs)

                context_parts: list[str] = []

                if kb_context:
                    context_parts.append(
                        "## Verified Setup Steps (from official docs — treat as ground truth)\n"
                        + kb_context
                    )

                if docs:
                    context_parts.append(
                        "## Arch Wiki Documentation\n" + build_docs_context(docs)
                    )

                if context_parts:
                    combined_context = "\n\n".join(context_parts)
                    goal = self.messages[-1]["content"]
                    doc_messages = [
                        {
                            "role": "user",
                            "content": (
                                f"User goal: {goal}\n\n"
                                f"Packages to install: {', '.join(p.name for p in available_pkgs)}\n\n"
                                f"{combined_context}\n\n"
                                "Using the verified steps and documentation above as ground truth, "
                                "generate the final \"env_steps\" JSON array of shell commands "
                                "needed AFTER installing these packages. "
                                "Rules: use exact commands from verified steps for known packages; "
                                "no placeholders; no package installation commands; "
                                "order commands correctly; combine steps intelligently. "
                                "Return ONLY: {\"env_steps\": [\"cmd1\", ...]}"
                            ),
                        }
                    ]
                    steps_result = await backend.suggest(doc_messages)
                    if not steps_result.error and steps_result.env_steps is not None:
                        result.env_steps = steps_result.env_steps
                else:
                    # No context at all — fall back to static KB merge
                    result.env_steps = apply_known_steps(available_pkgs, result.env_steps or [])

        if not result.packages and not result.env_steps:
            await self.append_chat(Static("[bold yellow]No actionable plan generated.[/bold yellow]"))
            inp.disabled = False
            inp.focus()
            return

        # Instead of the modal, mount the PlanWidget inline!
        await self.append_chat(PlanWidget(result, self.config.pkg))

    async def on_plan_widget_plan_run(self, event: PlanWidget.PlanRun) -> None:
        # Hide the buttons so they can't be clicked again
        btns = event.widget.query_one(".buttons")
        btns.display = False
        
        approved_plan = event.plan
        deselected = event.deselected
        
        planned_json = {
            "packages": [{"name": p.name, "source": p.source, "reason": p.reason} for p in approved_plan.packages],
            "steps": approved_plan.env_steps
        }
        self.messages.append({"role": "assistant", "content": json.dumps(planned_json)})
        
        if deselected and approved_plan.env_steps:
            asyncio.create_task(self._auto_filter_and_execute(approved_plan, deselected))
        else:
            self.pending_plan = approved_plan
            asyncio.create_task(self.execute_plan())

    async def _auto_filter_and_execute(self, plan, deselected) -> None:
        backend = get_backend(self.config)
        
        filter_msg = Static("[dim]Automatically filtering commands for deselected packages...[/dim]")
        await self.append_chat(filter_msg)
        
        deselected_names = ", ".join(p.name for p in deselected)
        prompt = (
            f"I have decided NOT to install these packages: {deselected_names}.\n"
            f"Here are the planned shell commands: {json.dumps(plan.env_steps)}\n\n"
            "Please return ONLY a JSON object with 'env_steps' containing the subset of these commands "
            "that are still safe to run. Exclude any commands that rely on the uninstalled packages."
        )
        
        temp_messages = self.messages + [{"role": "user", "content": prompt}]
        res = await backend.suggest(temp_messages)
        
        if not res.error and res.env_steps is not None:
            plan.env_steps = res.env_steps
            await self.append_chat(Static(f"[dim]Filtered out commands dependent on {deselected_names}.[/dim]"))
        else:
            await self.append_chat(Static("[bold yellow]Warning: Failed to auto-filter commands. Proceeding with original commands...[/bold yellow]"))
            
        self.pending_plan = plan
        await self.execute_plan()

    async def on_plan_widget_plan_cancel(self, event: PlanWidget.PlanCancel) -> None:
        # Hide the buttons so they can't be clicked again
        btns = event.widget.query_one(".buttons")
        btns.display = False
        
        await self.append_chat(Static("[dim]Plan refinement: please type your adjustments.[/dim]"))
        inp = self.query_one("#chat-input", ChatInput)
        inp.disabled = False
        inp.focus()

    async def execute_plan(self) -> None:
        inp = self.query_one("#chat-input", ChatInput)
        inp.disabled = True
        
        result = self.pending_plan
        
        # We need a log for the command output so it's efficient
        execution_log = RichLog(markup=True, wrap=True)
        await self.append_chat(execution_log)
        
        pkgs = [f"{'aur:' if p.source == 'aur' else ''}{p.name}" for p in result.packages if p.available]
        if pkgs:
            execution_log.write("[bold green]Installing packages...[/bold green]")
            
            pacman_pkgs = [p for p in pkgs if not p.startswith("aur:")]
            aur_pkgs = [p[4:] for p in pkgs if p.startswith("aur:")]
            
            async def run_cmd(cmd: List[str]):
                execution_log.write(f"[dim]$ {' '.join(cmd)}[/dim]")
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT
                )
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    execution_log.write(line.decode().rstrip())
                await proc.wait()
                return proc.returncode

            if pacman_pkgs:
                cmd = ["sudo", "pacman", "-S", "--needed", "--noconfirm"]
                cmd.extend(pacman_pkgs)
                rc = await run_cmd(cmd)
                if rc != 0:
                    execution_log.write("[bold red]pacman failed.[/bold red]")
                    inp.disabled = False
                    inp.focus()
                    return

            if aur_pkgs:
                cmd = [self.config.pkg.aur_helper, "-S", "--needed", "--noconfirm"]
                cmd.extend(aur_pkgs)
                rc = await run_cmd(cmd)
                if rc != 0:
                    execution_log.write(f"[bold red]{self.config.pkg.aur_helper} failed.[/bold red]")
                    inp.disabled = False
                    inp.focus()
                    return

        if result.env_steps:
            execution_log.write("\n[bold green]Running environment steps...[/bold green]")
            for step in result.env_steps:
                execution_log.write(f"\n[dim]$ {step}[/dim]")
                proc = await asyncio.create_subprocess_shell(
                    step,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    executable="/bin/bash"
                )
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    execution_log.write(line.decode().rstrip())
                rc = await proc.wait()
                if rc != 0:
                    execution_log.write(f"[bold red]Step failed (exit {rc}). Stopping.[/bold red]")
                    break

        execution_log.write("\n[bold green]✨ All operations completed![/bold green]\n")
        inp.disabled = False
        inp.focus()

def run_tui():
    app = AIPkgApp()
    app.run()
