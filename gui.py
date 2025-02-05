import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from llm import LLMHandler
from widgets import CollapsibleFrame


class OllamaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.llm_handler = LLMHandler()
        self.setWindowTitle("Ollama GUI")
        self.setGeometry(100, 100, 1200, 600)
        self.setup_ui()
        self.chat_history = []

    def setup_ui(self):
        """Setup the main UI components"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Create splitter for panels
        splitter = QSplitter(Qt.Horizontal)
        left_panels = QSplitter(Qt.Horizontal)

        self.model_panel = self.create_input_panel("Input")
        self.thinking_panel = self.create_display_panel("Thinking Process")
        self.output_panel = self.create_display_panel("Output")

        left_panels.addWidget(self.model_panel)
        left_panels.addWidget(self.thinking_panel)
        left_panels.addWidget(self.output_panel)

        self.raw_panel = CollapsibleFrame("Raw Output")
        self.raw_panel.setMaximumWidth(300)
        self.raw_panel.setMinimumWidth(200)

        splitter.addWidget(left_panels)
        splitter.addWidget(self.raw_panel)
        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)
        self.setup_menu()

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        save_action = file_menu.addAction("Save Conversation")
        save_action.triggered.connect(self.save_conversation)
        load_action = file_menu.addAction("Load Conversation")
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
        self.model_selector.addItems(
            ["deepseek-r1:32b", "llama2", "mistral", "codellama"]
        )
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
        """Process user input and get LLM response"""
        user_input = self.model_input.toPlainText()
        self.chat_history.append({"role": "user", "content": user_input})
        self.model_input.clear()
        self.clear_displays()

        try:
            response = self.llm_handler.get_response(
                user_input, self.model_selector.currentText(), self.chat_history
            )
            self.handle_response(response)
        except Exception as e:
            self._handle_error(str(e))

    def clear_displays(self):
        """Clear all display panels"""
        self.thinking_panel.display.clear()
        if isinstance(self.output_panel.display, QWebEngineView):
            self.output_panel.display.setHtml("")
        else:
            self.output_panel.display.clear()
        self.raw_panel.content.clear()

    def handle_response(self, response):
        """Handle streaming response from LLM"""
        for content_type, content in response:
            if content_type == "thinking":
                self.thinking_panel.display.setPlainText(content)
            elif content_type == "output":
                self._display_html_in_output(content)
            elif content_type == "raw":
                self.raw_panel.content.setPlainText(content)

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
        with open(filename, "w") as f:
            json.dump(
                {
                    "model": self.model_selector.currentText(),
                    "history": self.chat_history,
                },
                f,
                indent=2,
            )

    def load_conversation(self):
        """Load conversation from file"""

        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Conversation", "conversations", "JSON Files (*.json)"
        )

        if filename:
            with open(filename, "r") as f:
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
