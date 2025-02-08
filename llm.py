import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

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


class LLMHandler:
    def __init__(self):
        self.signals = LLMSignals()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.md = markdown.Markdown(extensions=["fenced_code", "tables"])
        self.patterns = {
            "think": r"<think>(.*?)</think>",
            "output": r"<output>(.*?)</output>",
        }
        self._current_future: Optional[object] = None

    def get_response(self, user_input: str, model: str, chat_history: list):
        """Start async response generation"""
        # Cancel any existing request
        if self._current_future:
            self._current_future.cancel()

        # Start new request
        self._current_future = self.executor.submit(
            self._generate_response, user_input, model, chat_history
        )

    def _generate_response(self, user_input: str, model: str, chat_history: list):
        """Generate response in background thread"""
        try:
            prompt = self._format_prompt(user_input, chat_history)
            response = self._call_api(model, prompt)
            self._process_response(response)
        except Exception as e:
            self.signals.error_occurred.emit(str(e))

    def _format_prompt(self, user_input, chat_history):
        """Format prompt with chat history"""
        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in chat_history[-5:]]
        )

        return f"""Previous conversation:
{history_text}

{FORMATTING_INSTRUCTIONS}

User: {user_input}"""

    def _call_api(self, model, prompt):
        """Call Ollama API"""
        payload = {"model": model, "prompt": prompt}
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
        response.raise_for_status()
        return response

    def _extract_section(self, text: str, tag: str) -> str:
        """Extract content from a specific XML-like tag"""
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _process_mermaid(self, content: str) -> str:
        """Process both explicit mermaid tags and markdown-style mermaid code blocks"""
        mermaid_blocks = []

        def save_mermaid(match):
            mermaid_blocks.append(match.group(1))
            return f"MERMAID_PLACEHOLDER_{len(mermaid_blocks)-1}"

        # Save explicit mermaid tags
        content = re.sub(
            r"<mermaid>(.*?)</mermaid>", save_mermaid, content, flags=re.DOTALL
        )

        # Save markdown-style mermaid blocks
        content = re.sub(
            r"```mermaid\s*(.*?)```", save_mermaid, content, flags=re.DOTALL
        )

        # Convert markdown to HTML
        content = self.md.convert(content)

        # Restore mermaid diagrams
        for i, diagram in enumerate(mermaid_blocks):
            content = content.replace(
                f"MERMAID_PLACEHOLDER_{i}", f'<div class="mermaid">{diagram}</div>'
            )

        return content

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

                # Extract thinking content
                thinking = self._extract_section(full_response, "think")
                if thinking and thinking != last_thinking:
                    self.signals.thinking_update.emit(thinking)
                    last_thinking = thinking

                # Extract output content
                output = self._extract_section(full_response, "output")
                if output and output != last_output:
                    # Process the output through markdown and mermaid formatting
                    formatted_output = self._process_mermaid(output)
                    self.signals.output_update.emit(
                        self._generate_html(formatted_output)
                    )
                    last_output = output

                # Update console with full response
                self.signals.console_update.emit(full_response)

    def _generate_html(self, content: str) -> str:
        """Generate HTML with consistent styling"""
        return HTMLTemplates.BASE.format(
            content=content,
            bg_tertiary=Styles.BACKGROUND_TERTIARY,
            bg_secondary=Styles.BACKGROUND_SECONDARY,
            bg_primary=Styles.BACKGROUND_PRIMARY,
            text_primary=Styles.TEXT_PRIMARY,
            accent=Styles.ACCENT_COLOR,
            border=Styles.BORDER_COLOR,
        )

    def _handle_error(self, error_message: str) -> str:
        """Generate error HTML"""
        error_content = HTMLTemplates.ERROR.format(
            error_color=Styles.ERROR_COLOR, message=error_message
        )
        return self._generate_html(error_content)

    def get_loading_html(self) -> str:
        """Generate loading HTML"""
        loading_content = HTMLTemplates.LOADING.format(
            text_secondary=Styles.TEXT_SECONDARY
        )
        return self._generate_html(loading_content)
