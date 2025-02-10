import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Protocol

import markdown
import requests
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from PySide6.QtCore import QObject, Signal

from constants import FORMATTING_INSTRUCTIONS
from styles import OneDarkStyle, Styles
from templates import HTMLTemplates

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
OLLAMA_API_URL = f"{OLLAMA_HOST}/api/generate"


class LLMSignals(QObject):
    thinking_update = Signal(str)
    output_update = Signal(str)
    console_update = Signal(str)
    error_occurred = Signal(str)
    llm_history_update = Signal(str)


class ResponseFormatter(Protocol):
    def format_response(self, response_text: str) -> tuple[str, str]:
        """Format the response and return (thinking, output) tuple"""
        pass


class MarkdownResponseFormatter:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                "fenced_code",
                "tables",
                "markdown.extensions.attr_list",
                "markdown.extensions.def_list",
                "markdown.extensions.sane_lists",
                "markdown.extensions.extra",
            ]
        )
        self.code_formatter = HtmlFormatter(
            style=OneDarkStyle, cssclass="highlight", linenos=False, noclasses=True
        )

    def _extract_section(self, text: str, tag: str) -> str:
        """Extract content from a specific XML-like tag"""
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _process_code_blocks(self, content: str) -> str:
        """Pre-process code blocks to protect them from markdown conversion"""
        if not content:
            return content

        def replace_code_block(match):
            lang = match.group(1) if len(match.groups()) > 1 else "text"
            code = match.group(2) if len(match.groups()) > 1 else match.group(1)
            code = code.strip()

            try:
                lexer = get_lexer_by_name(lang)
            except ClassNotFound:
                try:
                    lexer = guess_lexer(code)
                except ClassNotFound:
                    lexer = get_lexer_by_name("text")

            highlighted = highlight(code, lexer, self.code_formatter)

            # Add both Pygments highlighting and markdown code block classes
            return f'<pre class="code-block"><code class="language-{lang}">{highlighted}</code></pre>'

        # Process code blocks with language specification
        content = re.sub(
            r"(?m)^[ \t]*```(\w+)\r?\n(.*?)^[ \t]*```",
            replace_code_block,
            content,
            flags=re.DOTALL | re.MULTILINE,
        )

        # Process code blocks without language specification
        content = re.sub(
            r"(?m)^[ \t]*```\r?\n(.*?)^[ \t]*```",
            replace_code_block,
            content,
            flags=re.DOTALL | re.MULTILINE,
        )

        return content

    def _preprocess_lists(self, content: str) -> str:
        """Pre-process lists to ensure proper nesting and formatting"""
        lines = []
        current_indent = 0
        in_list = False
        in_numbered_list = False
        numbered_list_indent = 0

        for line in content.split("\n"):
            stripped = line.lstrip()

            # Skip empty lines
            if not stripped:
                lines.append(line)
                continue

            indent = len(line) - len(stripped)

            # Handle numbered lists
            if re.match(r"^\d+\.", stripped):
                if not in_list:
                    lines.append("")
                in_list = True
                in_numbered_list = True
                numbered_list_indent = indent
                lines.append(line)
                current_indent = indent
                continue

            # Handle bullet points
            if stripped.startswith("- ") or stripped.startswith("* "):
                # If this is a nested bullet under a numbered list
                if in_numbered_list and indent > numbered_list_indent:
                    # Convert to proper nested format with extra indentation
                    lines.append(" " * (indent) + "  - " + stripped[2:])
                else:
                    if not in_list:
                        lines.append("")
                    in_list = True
                    lines.append(line)
                current_indent = indent
                continue

            # Not a list item
            if stripped and not line.startswith(" " * current_indent):
                in_list = False
                in_numbered_list = False
                current_indent = 0
                numbered_list_indent = 0
                lines.append("")

            lines.append(line)

        return "\n".join(lines)

    def _postprocess_html(self, content: str) -> str:
        """Post-process HTML to fix nested lists and other formatting"""
        # Fix nested bullet points under numbered lists
        content = re.sub(
            r"(<li>[^<]*)\n\s*-\s+([^<]*)</li>",
            r'\1<ul class="nested-list"><li>\2</li></ul></li>',
            content,
        )

        # Fix multiple nested items
        content = re.sub(
            r"</ul></li>\n\s*-\s+([^<]*)</li>", r"<li>\1</li></ul></li>", content
        )

        return content

    def _process_mermaid(self, content: str) -> str:
        """Process mermaid diagrams, but only those not inside code blocks"""
        if not content:
            return content

        # First, temporarily replace non-mermaid code blocks to protect them
        code_blocks = []

        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"CODE_BLOCK_{len(code_blocks)-1}"

        content = re.sub(
            r"```(?!mermaid\n)(\w+)?\n(.*?)```",
            save_code_block,
            content,
            flags=re.DOTALL,
        )

        # Rest of the mermaid processing remains the same
        mermaid_blocks = []

        def save_mermaid(match):
            diagram = match.group(1).strip()
            diagram = "\n".join(line.strip() for line in diagram.splitlines())
            mermaid_blocks.append(diagram)
            return f"MERMAID_PLACEHOLDER_{len(mermaid_blocks)-1}"

        content = re.sub(
            r"<mermaid>\s*(.*?)\s*</mermaid>", save_mermaid, content, flags=re.DOTALL
        )

        content = re.sub(
            r"```mermaid\s*(.*?)\s*```", save_mermaid, content, flags=re.DOTALL
        )

        # Restore code blocks before processing them
        for i, block in enumerate(code_blocks):
            content = content.replace(f"CODE_BLOCK_{i}", block)

        # Process code blocks
        content = self._process_code_blocks(content)

        # Convert markdown to HTML
        content = self.md.convert(content)

        # Restore mermaid diagrams
        for i, diagram in enumerate(mermaid_blocks):
            mermaid_div = f'<div class="mermaid">\n{diagram}\n</div>'
            content = content.replace(f"MERMAID_PLACEHOLDER_{i}", mermaid_div)

        return content

    def _fix_nested_lists(self, content: str) -> str:
        """Fix nested list formatting and ensure proper list type preservation"""
        # Fix nested unordered lists
        content = re.sub(
            r"(<ul>(?:[^<]|<(?!ul|/ul>))*)<ul>", r'\1<ul class="nested-list">', content
        )

        # Fix nested ordered lists
        content = re.sub(
            r"(<ol>(?:[^<]|<(?!ol|/ol>))*)<ol>", r'\1<ol class="nested-list">', content
        )

        # Fix mixed list types (unordered under ordered)
        content = re.sub(
            r"(<li>.*?)<br\s*/>\s*-\s*(.*?)(?=</li>)",
            r'\1<ul class="nested-list"><li>\2</li></ul>',
            content,
            flags=re.DOTALL,
        )

        return content

    def _generate_html(self, content: str) -> str:
        """Generate HTML with consistent styling"""
        if not content:
            return ""

        return HTMLTemplates.apply_style(content)

    def format_response(self, response_text: str) -> tuple[str, str]:
        """Format the response and return (thinking, output) tuple"""
        thinking = self._extract_section(response_text, "think")
        output = self._extract_section(response_text, "output")

        if not output and thinking:
            output = response_text.replace(thinking, "")

        if output:
            # Preprocess lists
            output = self._preprocess_lists(output)

            # Pre-process lists before any other processing
            output = self._preprocess_lists(output)

            # Process code blocks and mermaid
            output = self._process_mermaid(output)
            content = self._process_code_blocks(output)

            # Fix nested list formatting
            formatted_output = self._fix_nested_lists(content)

            # Convert to HTML
            html_output = self._generate_html(formatted_output)
            # Post-process HTML
            html_output = self._postprocess_html(html_output)
        else:
            html_output = ""

        return thinking, html_output


class LLMClient:
    def __init__(self):
        self.api_url = OLLAMA_API_URL

    def _format_prompt(self, user_input: str, chat_history: list) -> str:
        """Format prompt with chat history"""
        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in chat_history[-5:]]
        )
        return f"""Previous conversation:
{history_text}

{FORMATTING_INSTRUCTIONS}

User: {user_input}"""

    def stream_response(self, model: str, prompt: str):
        """Stream response from API"""
        payload = {"model": model, "prompt": prompt}
        response = requests.post(self.api_url, json=payload, stream=True)
        response.raise_for_status()
        return response


class LLMHandler:
    def __init__(self, formatter: ResponseFormatter = None):
        self.signals = LLMSignals()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.formatter = formatter or MarkdownResponseFormatter()
        self.client = LLMClient()
        self._current_future: Optional[object] = None

    def get_response(self, user_input: str, model: str, chat_history: list):
        """Start async response generation"""
        if self._current_future:
            self._current_future.cancel()

        self._current_future = self.executor.submit(
            self._generate_response, user_input, model, chat_history
        )

    def _generate_response(self, user_input: str, model: str, chat_history: list):
        """Generate response in background thread"""
        try:
            prompt = self.client._format_prompt(user_input, chat_history)
            response = self.client.stream_response(model, prompt)
            full_response = self._process_response(response)
            self.signals.llm_history_update.emit(full_response)
        except Exception as e:
            self.signals.error_occurred.emit(str(e))

    def _process_response(self, response) -> None:
        """Process streaming response"""
        full_response = ""
        last_thinking = ""
        last_output = ""

        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                response_text = json_response.get("response", "")
                full_response += response_text

                # Format the response
                thinking, output = self.formatter.format_response(full_response)

                if thinking and thinking != last_thinking:
                    self.signals.thinking_update.emit(thinking)
                    last_thinking = thinking

                if output and output != last_output:
                    self.signals.output_update.emit(output)
                    last_output = output

                self.signals.console_update.emit(full_response)

        return full_response

    def get_loading_html(self) -> str:
        """Generate loading HTML"""
        loading_content = HTMLTemplates.LOADING.format(
            text_secondary=Styles.TEXT_SECONDARY
        )
        return self.formatter._generate_html(loading_content)
