import json
import os
import re

import markdown
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
OLLAMA_API_URL = f"{OLLAMA_HOST}/api/generate"


class LLMHandler:
    def __init__(self):
        self.patterns = {
            "think": re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE),
            "output": re.compile(r"<output>(.*?)</output>", re.DOTALL | re.IGNORECASE),
        }

    def get_response(self, user_input, model, chat_history):
        """Get response from LLM model"""
        prompt = self._format_prompt(user_input, chat_history)
        response = self._call_api(model, prompt)
        return self._process_response(response)

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

    def _process_response(self, response):
        """Process streaming response"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                response_text = json_response.get("response", "")
                full_response += response_text

                # Extract thinking content
                thinking = self._extract_content(full_response, self.patterns["think"])
                if thinking:
                    yield "thinking", thinking

                # Extract output content
                output = self._extract_content(full_response, self.patterns["output"])
                if output:
                    yield "output", self._generate_html(output)

                # Raw output
                yield "raw", full_response

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
