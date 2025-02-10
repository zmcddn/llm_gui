import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Protocol

import markdown
import requests
from PySide6.QtCore import QObject, Signal

from constants import FORMATTING_INSTRUCTIONS
from styles import Styles
from templates import HTMLTemplates

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
OLLAMA_API_URL = f"{OLLAMA_HOST}/api/generate"


class LLMSignals(QObject):
    thinking_update = Signal(str)
    output_update = Signal(str)
    console_update = Signal(str)
    error_occurred = Signal(str)


class ResponseFormatter(Protocol):
    def format_response(self, response_text: str) -> tuple[str, str]:
        """Format the response and return (thinking, output) tuple"""
        pass


class MarkdownResponseFormatter:
    def __init__(self):
        self.md = markdown.Markdown(extensions=[
            'fenced_code',
            'tables',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.sane_lists',
            'markdown.extensions.extra'
        ])

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
            lang = match.group(1)
            code = match.group(2).strip()
            return f'<pre><code class="language-{lang}">{code}</code></pre>'

        # Process code blocks with language specification
        content = re.sub(
            r'```(\w+)\n(.*?)```',
            replace_code_block,
            content,
            flags=re.DOTALL
        )
        return content

    def _preprocess_lists(self, content: str) -> str:
        """Pre-process lists to ensure proper nesting and formatting"""
        lines = []
        current_indent = 0
        in_list = False
        in_numbered_list = False
        numbered_list_indent = 0

        for line in content.split('\n'):
            stripped = line.lstrip()

            # Skip empty lines
            if not stripped:
                lines.append(line)
                continue

            indent = len(line) - len(stripped)

            # Handle numbered lists
            if re.match(r'^\d+\.', stripped):
                if not in_list:
                    lines.append('')
                in_list = True
                in_numbered_list = True
                numbered_list_indent = indent
                lines.append(line)
                current_indent = indent
                continue

            # Handle bullet points
            if stripped.startswith('- ') or stripped.startswith('* '):
                # If this is a nested bullet under a numbered list
                if in_numbered_list and indent > numbered_list_indent:
                    # Convert to proper nested format with extra indentation
                    lines.append(' ' * (indent) + '  - ' + stripped[2:])
                else:
                    if not in_list:
                        lines.append('')
                    in_list = True
                    lines.append(line)
                current_indent = indent
                continue

            # Not a list item
            if stripped and not line.startswith(' ' * current_indent):
                in_list = False
                in_numbered_list = False
                current_indent = 0
                numbered_list_indent = 0
                lines.append('')

            lines.append(line)

        return '\n'.join(lines)

    def _postprocess_html(self, content: str) -> str:
        """Post-process HTML to fix nested lists and other formatting"""
        # Fix nested bullet points under numbered lists
        content = re.sub(
            r'(<li>[^<]*)\n\s*-\s+([^<]*)</li>',
            r'\1<ul class="nested-list"><li>\2</li></ul></li>',
            content
        )

        # Fix multiple nested items
        content = re.sub(
            r'</ul></li>\n\s*-\s+([^<]*)</li>',
            r'<li>\1</li></ul></li>',
            content
        )

        return content

    def _process_mermaid(self, content: str) -> str:
        """Process both explicit mermaid tags and markdown-style mermaid code blocks"""
        if not content:
            return content

        # Pre-process lists before any other processing
        content = self._preprocess_lists(content)

        # Rest of the mermaid processing remains the same
        mermaid_blocks = []
        def save_mermaid(match):
            diagram = match.group(1).strip()
            diagram = "\n".join(line.strip() for line in diagram.splitlines())
            mermaid_blocks.append(diagram)
            return f"MERMAID_PLACEHOLDER_{len(mermaid_blocks)-1}"

        content = re.sub(
            r"<mermaid>\s*(.*?)\s*</mermaid>",
            save_mermaid,
            content,
            flags=re.DOTALL
        )

        content = re.sub(
            r"```mermaid\s*(.*?)\s*```",
            save_mermaid,
            content,
            flags=re.DOTALL
        )

        # Process code blocks
        content = self._process_code_blocks(content)

        # Convert markdown to HTML
        content = self.md.convert(content)

        # Restore mermaid diagrams
        for i, diagram in enumerate(mermaid_blocks):
            mermaid_div = f"""<div class="mermaid">
{diagram}
</div>"""
            content = content.replace(f"MERMAID_PLACEHOLDER_{i}", mermaid_div)

        # Fix nested list formatting
        content = self._fix_nested_lists(content)

        return content

    def _fix_nested_lists(self, content: str) -> str:
        """Fix nested list formatting and ensure proper list type preservation"""
        # Fix nested unordered lists
        content = re.sub(
            r'(<ul>(?:[^<]|<(?!ul|/ul>))*)<ul>',
            r'\1<ul class="nested-list">',
            content
        )

        # Fix nested ordered lists
        content = re.sub(
            r'(<ol>(?:[^<]|<(?!ol|/ol>))*)<ol>',
            r'\1<ol class="nested-list">',
            content
        )

        # Fix mixed list types (unordered under ordered)
        content = re.sub(
            r'(<li>.*?)<br\s*/>\s*-\s*(.*?)(?=</li>)',
            r'\1<ul class="nested-list"><li>\2</li></ul>',
            content,
            flags=re.DOTALL
        )

        return content

    def _generate_html(self, content: str) -> str:
        """Generate HTML with consistent styling"""
        if not content:
            return ""

        # Add CSS for nested lists and code blocks
        additional_styles = """
        <style>
            ul, ol { padding-left: 2em; margin: 1em 0; }
            .nested-list { margin-left: 1em; }
            pre { background-color: #f6f8fa; padding: 1em; border-radius: 6px; margin: 1em 0; }
            code { font-family: monospace; }
            li { margin: 0.5em 0; }
            li > ul, li > ol { margin: 0.5em 0; }
            .nested-list li { margin: 0.25em 0; }
        </style>
        """
        return HTMLTemplates.apply_style(content + additional_styles)

    def format_response(self, response_text: str) -> tuple[str, str]:
        """Format the response and return (thinking, output) tuple"""
        thinking = self._extract_section(response_text, "think")
        output = self._extract_section(response_text, "output")

        if output:
            # Preprocess lists
            output = self._preprocess_lists(output)
            # Process code blocks and mermaid
            output = self._process_code_blocks(output)
            formatted_output = self._process_mermaid(output)
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
            self._process_response(response)
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

    def get_loading_html(self) -> str:
        """Generate loading HTML"""
        loading_content = HTMLTemplates.LOADING.format(
            text_secondary=Styles.TEXT_SECONDARY
        )
        return self.formatter._generate_html(loading_content)
