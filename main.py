import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTextEdit,
    QVBoxLayout, QWidget, QPushButton, QLineEdit, QFrame,
    QHBoxLayout, QLabel, QComboBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import markdown
import os
import json
import re
from datetime import datetime
import threading
from pathlib import Path

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
OLLAMA_API_URL = f"{OLLAMA_HOST}/api/generate"

class CollapsibleFrame(QWidget):
    """Collapsible panel component"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Remove spacing between widgets

        # Create title button
        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                background-color: #f0f0f0;
                border: none;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_content)

        # Create content area
        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to layout
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)

        # Initial state is collapsed
        self.is_collapsed = False
        self.content.setVisible(True)
        self.content_height = self.content.height()

    def toggle_content(self):
        """Toggle content area visibility"""
        self.is_collapsed = not self.is_collapsed
        self.content.setVisible(not self.is_collapsed)

        if self.is_collapsed:
            self.content.setMaximumHeight(0)
        else:
            self.content.setMaximumHeight(16777215)  # Qt's QWIDGETSIZE_MAX


class OllamaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama GUI")
        self.setGeometry(100, 100, 1200, 600)

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Create splitter for panels
        splitter = QSplitter(Qt.Horizontal)

        # Create main panels
        left_panels = QSplitter(Qt.Horizontal)
        self.model_panel = self.create_input_panel("Input")
        self.thinking_panel = self.create_display_panel("Thinking Process")
        self.output_panel = self.create_display_panel("Output")

        # Add main panels to left splitter
        left_panels.addWidget(self.model_panel)
        left_panels.addWidget(self.thinking_panel)
        left_panels.addWidget(self.output_panel)

        # Create collapsible raw output panel
        self.raw_panel = CollapsibleFrame("Raw Output")
        self.raw_panel.setMaximumWidth(300)
        self.raw_panel.setMinimumWidth(200)

        # Add panels to main splitter
        splitter.addWidget(left_panels)
        splitter.addWidget(self.raw_panel)

        # Add splitter to main layout
        main_layout.addWidget(splitter)

        # Set main widget
        self.setCentralWidget(main_widget)

        self.chat_history = []

        # Add menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Add save action
        save_action = file_menu.addAction('Save Conversation')
        save_action.triggered.connect(self.save_conversation)

        # Add load action
        load_action = file_menu.addAction('Load Conversation')
        load_action.triggered.connect(self.load_conversation)

    def create_input_panel(self, title):
        """Create an input panel with title"""
        container = QWidget()
        layout = QVBoxLayout(container)

        # Add header
        header = QTextEdit()
        header.setPlainText(title)
        header.setReadOnly(True)
        header.setMaximumHeight(30)
        header.setStyleSheet("background-color: #f0f0f0; border: none;")

        # Add model selector
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_selector = QComboBox()
        self.model_selector.addItems(["deepseek-r1:32b", "llama2", "mistral", "codellama"])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()

        # Create input area
        self.model_input = QTextEdit()
        self.model_input.setMinimumHeight(100)

        # Create send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)

        # Add widgets to layout
        layout.addWidget(header)
        layout.addLayout(model_layout)
        layout.addWidget(self.model_input)
        layout.addWidget(self.send_button)

        return container

    def create_display_panel(self, title):
        """Create a display panel with title"""
        container = QWidget()
        layout = QVBoxLayout(container)

        # Add header
        header = QTextEdit()
        header.setPlainText(title)
        header.setReadOnly(True)
        header.setMaximumHeight(30)
        header.setStyleSheet("background-color: #f0f0f0; border: none;")

        # Create display area - use QWebEngineView for output panel, QTextEdit for others
        if title == "Output":
            display = QWebEngineView()
            display.setContextMenuPolicy(Qt.NoContextMenu)  # Disable right-click menu
        else:
            display = QTextEdit()
            display.setReadOnly(True)
            display.setAcceptRichText(True)

        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(display)

        # Store the display widget as an attribute of the container
        container.display = display

        return container

    def process_input(self):
        """Process user input and call Ollama API for response"""
        user_input = self.model_input.toPlainText()
        self.chat_history.append({"role": "user", "content": user_input})

        # Clear input after sending
        self.model_input.clear()

        self.thinking_panel.display.clear()

        # Use setHtml with empty string instead of clear() for QWebEngineView
        if isinstance(self.output_panel.display, QWebEngineView):
            self.output_panel.display.setHtml("")
        else:
            self.output_panel.display.clear()

        self.raw_panel.content.clear()

        try:
            response = self._call_ollama_api(user_input)
            self._process_streaming_response(response)
        except Exception as e:
            self._handle_error(str(e))

    def _call_ollama_api(self, user_input):
        """Call Ollama API"""
        payload = {
            "model": self.model_selector.currentText(),
            "prompt": self._format_prompt(user_input)
        }
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
        response.raise_for_status()
        return response

    def _format_prompt(self, user_input):
        """Format the prompt text sent to API"""
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history[-5:]])
        return f"""Previous conversation:
{history_text}

Please format your response with <think> tags for your thinking process and <output> tags for the final response. If you need to include a any chart, please use Mermaid syntax within <mermaid> tags.

User: {user_input}"""

    def _process_streaming_response(self, response):
        """Process streaming response"""
        full_response = ""
        output_content = ""

        patterns = {
            'think': re.compile(r'<think>(.*?)</think>', re.DOTALL | re.IGNORECASE),
            'output': re.compile(r'<output>(.*?)</output>', re.DOTALL | re.IGNORECASE)
        }

        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                response_text = json_response.get('response', '')
                full_response += response_text

                # Update raw output panel
                self.raw_panel.content.setPlainText(full_response)

                self._extract_thinking_content(full_response, patterns['think'])
                output_content = self._extract_output_content(full_response, patterns['output'])

                QApplication.processEvents()

        if not output_content.strip():
            self._display_raw_response(full_response)

    def _extract_thinking_content(self, full_response, pattern):
        """Extract and display thinking process content"""
        matches = pattern.findall(full_response)
        if matches:
            thinking_content = ''.join(matches)
            self.thinking_panel.display.setPlainText(thinking_content)
            return thinking_content
        return ""

    def _extract_output_content(self, full_response, pattern):
        """Extract and display output content"""
        matches = pattern.findall(full_response)
        if matches:
            output_content = ''.join(matches)
            html_output = self._generate_html_output(output_content)
            self._display_html_in_output(html_output)
            return output_content
        return ""

    def _display_raw_response(self, response):
        """Display raw response content"""
        # Convert markdown to HTML and wrap in our HTML template
        html_output = self._generate_html_output(response)
        self._display_html_in_output(html_output)

    def _generate_html_output(self, content):
        """Generate HTML output with Mermaid support"""
        # Process Mermaid flowchart - look for both ```mermaid and <mermaid> tags
        content = re.sub(r'```mermaid|<mermaid>',
            '<div class="mermaid">', content)
        content = re.sub(r'```|</mermaid>', '</div>', content)

        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'codehilite'])

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

    def _display_html_in_output(self, html_content):
        """Helper method to display HTML content in the output panel"""
        if isinstance(self.output_panel.display, QWebEngineView):
            self.output_panel.display.setHtml(html_content)
        else:
            self.output_panel.display.setHtml(html_content)

    def _handle_error(self, error_message):
        """Handle error cases"""
        error_msg = f"Error: {error_message}"
        self.thinking_panel.display.setPlainText(error_msg)
        self.output_panel.display.setPlainText(error_msg)
        self.raw_panel.content.setPlainText(error_msg)

    def save_conversation(self):
        """Save current conversation to file"""
        if not self.chat_history:
            return

        # Create conversations directory if it doesn't exist
        Path("conversations").mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversations/chat_{timestamp}.json"

        # Save conversation
        with open(filename, 'w') as f:
            json.dump({
                "model": self.model_selector.currentText(),
                "history": self.chat_history
            }, f, indent=2)

    def load_conversation(self):
        """Load conversation from file"""
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Conversation",
            "conversations",
            "JSON Files (*.json)"
        )

        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.chat_history = data["history"]

                # Set the model if it exists in the selector
                model = data.get("model")
                if model and self.model_selector.findText(model) != -1:
                    self.model_selector.setCurrentText(model)

                # Update display with last response
                if self.chat_history:
                    last_response = self.chat_history[-1].get("content", "")
                    self._display_raw_response(last_response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OllamaGUI()
    window.show()
    sys.exit(app.exec())
