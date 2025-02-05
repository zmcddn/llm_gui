import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import markdown
import requests
from PySide6.QtCore import QObject, Signal

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
        self.patterns = {
            "think": re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE),
            "output": re.compile(r"<output>(.*?)</output>", re.DOTALL | re.IGNORECASE),
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

Please format your response with <think> tags for your thinking process and <output> tags for the final response. If you need to include a any chart, please use Mermaid syntax within <mermaid> tags.

User: {user_input}"""

    def _call_api(self, model, prompt):
        """Call Ollama API"""
        payload = {"model": model, "prompt": prompt}
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
        response.raise_for_status()
        return response

    def _process_response(self, response: requests.Response) -> None:
        """Process streaming response"""
        full_response = ""
        last_thinking = ""  # Track last thinking content
        last_output = ""  # Track last output content

        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                response_text = json_response.get("response", "")
                full_response += response_text

                # Extract thinking content
                thinking = self._extract_content(full_response, self.patterns["think"])
                if thinking and thinking != last_thinking:
                    self.signals.thinking_update.emit(thinking)
                    last_thinking = thinking

                # Extract output content
                output = self._extract_content(full_response, self.patterns["output"])
                if output and output != last_output:
                    self.signals.output_update.emit(self._generate_html(output))
                    last_output = output

                # Console output
                self.signals.console_update.emit(full_response)

    def _extract_content(self, text, pattern):
        """Extract content using regex pattern"""
        matches = pattern.findall(text)
        return "".join(matches) if matches else ""

    def _generate_html(self, content):
        """Generate HTML output with Mermaid support"""
        # Process Mermaid flowchart - look for both ```mermaid and <mermaid> tags
        content = re.sub(r"```mermaid|<mermaid>", '<div class="mermaid">', content)
        content = re.sub(r"```|</mermaid>", "</div>", content)

        # Convert markdown to HTML
        html_content = markdown.markdown(
            content, extensions=["fenced_code", "tables", "codehilite"]
        )

        return f"""
        <html>
        <head>
            <script type="text/javascript">
                // Disable web security for local content
                window.webSecurityEnabled = false;
            </script>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                }}
                .mermaid {{
                    margin: 10px 0;
                    text-align: center;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }}
                code {{
                    font-family: 'Courier New', Courier, monospace;
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f5f5f5;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    margin: 0;
                    padding-left: 16px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html_content}
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                    fontFamily: 'Arial, sans-serif'
                }});
                // Force mermaid to render after a short delay
                setTimeout(function() {{
                    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                }}, 100);
            </script>
        </body>
        </html>
        """
