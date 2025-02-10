from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from constants import APP_NAME, MODEL_LIST
from llm import LLMHandler
from styles import Styles
from templates import HTMLTemplates


class OllamaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.llm_handler = LLMHandler()
        self.setup_llm_signals()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1920, 1080)
        self.setup_ui()
        self.apply_styles()
        self.chat_history = []

    def apply_styles(self):
        """Apply custom styles to the application"""
        self.setStyleSheet(Styles.COMMON + Styles.MAIN_WINDOW)
        self.menuBar().setStyleSheet(Styles.MENU_BAR)
        self.main_splitter.setStyleSheet(Styles.SPLITTER)

        # Apply styles to all QTextEdit widgets
        for widget in self.findChildren(QTextEdit):
            if widget.maximumHeight() == 30:  # Header
                widget.setStyleSheet(Styles.PANEL_HEADER)
            else:  # Content
                widget.setStyleSheet(Styles.PANEL_CONTENT + Styles.SCROLLBAR)

        # Style the model selector and send button
        self.model_selector.setStyleSheet(Styles.MODEL_SELECTOR)
        self.send_button.setStyleSheet(Styles.SEND_BUTTON)

    def setup_llm_signals(self):
        """Setup signal connections for LLM handler"""
        self.llm_handler.signals.thinking_update.connect(self.update_thinking)
        self.llm_handler.signals.output_update.connect(self.update_output)
        self.llm_handler.signals.console_update.connect(self.update_console)
        self.llm_handler.signals.error_occurred.connect(self.handle_error)

    def setup_ui(self):
        """Setup the main UI components"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Create splitter for panels
        self.main_splitter = QSplitter(Qt.Horizontal)
        left_panels = QSplitter(Qt.Horizontal)

        # Set stretch factors and handle width for better resizing
        self.main_splitter.setHandleWidth(2)
        self.main_splitter.setChildrenCollapsible(False)
        left_panels.setHandleWidth(2)
        left_panels.setChildrenCollapsible(False)

        # Create panels
        self.history_panel = self.create_display_panel("History")
        self.model_panel = self.create_input_panel("Input")
        self.thinking_panel = self.create_display_panel("Thinking Process")
        self.output_panel = self.create_display_panel("Output")

        # Set size policies for left panels
        self.history_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.model_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.thinking_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create vertical splitter for history and input panels
        input_splitter = QSplitter(Qt.Vertical)
        input_splitter.addWidget(self.history_panel)
        input_splitter.addWidget(self.model_panel)
        input_splitter.setHandleWidth(2)
        input_splitter.setChildrenCollapsible(False)

        # Add panels to left splitter
        left_panels.addWidget(input_splitter)
        left_panels.addWidget(self.thinking_panel)
        left_panels.addWidget(self.output_panel)

        # Set initial sizes for left panels (equal distribution)
        panel_width = self.width() // 3  # Divide width by number of panels
        left_panels.setSizes([panel_width, panel_width, panel_width])

        # Create console panel
        self.console_panel = QWidget()
        console_layout = QVBoxLayout(self.console_panel)
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)

        # Create header container with title and close button
        header_container = QWidget()
        header_container.setFixedHeight(30)  # Fix the height to match other headers
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(8, 0, 4, 0)  # Reduced margins
        header_layout.setSpacing(0)  # Remove spacing between elements

        # Add header text as QLabel instead of QTextEdit
        header_label = QLabel("Console")
        header_label.setStyleSheet(
            f"""
            background-color: {Styles.BACKGROUND_SECONDARY};
            color: {Styles.TEXT_PRIMARY};
            font-weight: bold;
            padding: 4px;
        """
        )

        # Create close button
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.hide_console_panel)
        close_button.setStyleSheet(Styles.CLOSE_BUTTON)

        header_layout.addWidget(header_label, 1)  # Give the label stretch factor
        header_layout.addWidget(close_button, 0)  # Don't stretch the button

        # Style the header container
        header_container.setStyleSheet(
            f"""
            background-color: {Styles.BACKGROUND_SECONDARY};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        """
        )

        self.console_content = QTextEdit()
        self.console_content.setReadOnly(True)
        self.console_content.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.console_content.setLineWrapMode(QTextEdit.WidgetWidth)

        console_layout.addWidget(header_container)
        console_layout.addWidget(self.console_content)

        # Set size constraints for console panel
        self.console_panel.setMinimumWidth(100)
        self.console_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Add panels to main splitter
        self.main_splitter.addWidget(left_panels)
        self.main_splitter.addWidget(self.console_panel)

        # Set initial sizes for main splitter (75% left panels, 25% console)
        total_width = self.width()
        self.main_splitter.setSizes([int(total_width * 0.75), int(total_width * 0.25)])

        main_layout.addWidget(self.main_splitter)
        self.setCentralWidget(main_widget)
        self.setup_menu()

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        save_action = file_menu.addAction("Save Conversation")
        save_action.triggered.connect(self.save_conversation)

        # View menu
        view_menu = menubar.addMenu("View")
        self.toggle_console_action = view_menu.addAction("Show Console")
        self.toggle_console_action.setCheckable(True)
        self.toggle_console_action.setChecked(True)
        self.toggle_console_action.triggered.connect(self.toggle_console_panel)

    def create_input_panel(self, title):
        """Create an input panel with title"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Add header
        header = QTextEdit()
        header.setPlainText(title)
        header.setReadOnly(True)
        header.setMaximumHeight(30)
        header.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )  # Disable vertical scrollbar
        header.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )  # Disable horizontal scrollbar

        # Create model selector with label
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_selector = QComboBox()
        self.model_selector.addItems(MODEL_LIST)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)
        model_layout.addStretch()

        # Create input area
        self.model_input = QTextEdit()
        self.model_input.setMinimumHeight(100)
        self.model_input.setStyleSheet(Styles.PANEL_CONTENT + Styles.SCROLLBAR)

        # Create send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)
        self.send_button.setFixedHeight(32)

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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create header container
        header_container = QWidget()
        header_container.setFixedHeight(30)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(8, 0, 4, 0)
        header_layout.setSpacing(0)

        # Add header text as QLabel
        header_label = QLabel(title)
        header_label.setStyleSheet(
            f"""
            background-color: {Styles.BACKGROUND_SECONDARY};
            color: {Styles.TEXT_PRIMARY};
            font-weight: bold;
            padding: 4px;
        """
        )
        header_layout.addWidget(header_label, 1)

        # Style the header container
        header_container.setStyleSheet(
            f"""
            background-color: {Styles.BACKGROUND_SECONDARY};
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        """
        )

        # Create content container for proper styling
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(1, 0, 1, 1)  # Border width
        content_layout.setSpacing(0)

        # Style the content container to match other panels
        content_container.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Styles.BORDER_COLOR};
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
            }}
        """
        )

        # Create display area - use QWebEngineView for output panel, QTextEdit for others
        if title == "Output":
            display = QWebEngineView()
            display.setContextMenuPolicy(Qt.NoContextMenu)
            display.setHtml(
                HTMLTemplates.BASE.format(
                    content=f"Welcome to {APP_NAME}!",
                    bg_tertiary=Styles.BACKGROUND_TERTIARY,
                    bg_secondary=Styles.BACKGROUND_SECONDARY,
                    bg_primary=Styles.BACKGROUND_PRIMARY,
                    text_primary=Styles.TEXT_PRIMARY,
                    accent=Styles.ACCENT_COLOR,
                    border=Styles.BORDER_COLOR,
                )
            )
        else:
            display = QTextEdit()
            display.setReadOnly(True)
            display.setAcceptRichText(True)
            display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            display.setLineWrapMode(QTextEdit.WidgetWidth)
            display.setStyleSheet(Styles.PANEL_CONTENT + Styles.SCROLLBAR)

        # Add display to content container
        content_layout.addWidget(display)

        # Add widgets to main layout
        layout.addWidget(header_container)
        layout.addWidget(content_container)

        # Store the display widget as an attribute of the container
        container.display = display

        return container

    def process_input(self):
        """Process user input and get LLM response"""
        user_input = self.model_input.toPlainText()
        if not user_input.strip():  # Skip empty input
            return

        # Update history panel
        current_history = self.history_panel.display.toPlainText()
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_entry = f"[{timestamp}] {user_input}\n"
        if current_history:
            new_entry = f"{current_history}{new_entry}"
        self.history_panel.display.setPlainText(new_entry)

        # Scroll to bottom of history
        scrollbar = self.history_panel.display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        self.chat_history.append({"role": "user", "content": user_input})
        self.model_input.clear()
        self.clear_displays()

        # Show loading indicators
        self.thinking_panel.display.setPlainText("Analyzing your request...")
        self.output_panel.display.setHtml(self.llm_handler.get_loading_html())
        self.console_content.setPlainText("Processing request in progress...")

        # Start async processing
        self.llm_handler.get_response(
            user_input, self.model_selector.currentText(), self.chat_history
        )

    def update_thinking(self, content):
        """Update thinking panel with new content"""
        self.thinking_panel.display.setPlainText(content)
        self.thinking_panel.display.verticalScrollBar().setValue(
            self.thinking_panel.display.verticalScrollBar().maximum()
        )

    def update_output(self, content):
        """Update output panel with new content"""
        self._display_html_in_output(content)

    def update_console(self, content):
        """Update console panel with new content"""
        self.console_content.setPlainText(content)
        self.console_content.verticalScrollBar().setValue(
            self.console_content.verticalScrollBar().maximum()
        )

    def handle_error(self, error_message):
        """Handle error cases"""
        self.thinking_panel.display.setPlainText(f"Error occurred: {error_message}")
        self.output_panel.display.setHtml(self.llm_handler._handle_error(error_message))
        self.console_content.setPlainText(f"Error: {error_message}")

    def clear_displays(self):
        """Clear all display panels"""
        self.thinking_panel.display.clear()
        if isinstance(self.output_panel.display, QWebEngineView):
            self.output_panel.display.setHtml("")
        else:
            self.output_panel.display.clear()
        self.console_content.clear()

    def _display_html_in_output(self, html_content):
        """Helper method to display HTML content in the output panel"""
        styled_html = HTMLTemplates.apply_style(html_content)
        self.output_panel.display.setHtml(styled_html)

    def save_conversation(self):
        """Save current conversation to markdown file"""
        if not self.chat_history:
            return

        # Create conversations directory if it doesn't exist
        Path("conversations").mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversations/chat_{timestamp}.md"

        with open(filename, "w", encoding="utf-8") as f:
            # Write header
            f.write(
                f"# Chat History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write(f"Model: {self.model_selector.currentText()}\n\n")

            # Write chat history
            for entry in self.chat_history:
                role = entry["role"]
                content = entry["content"]

                if role == "user":
                    f.write("## User Input\n")
                    f.write(f"{content}\n\n")
                else:
                    f.write("## Assistant Response\n")
                    # Extract thinking and output sections if present
                    thinking = self.llm_handler._extract_section(content, "think")
                    output = self.llm_handler._extract_section(content, "output")

                    if thinking:
                        f.write("### Thinking Process\n")
                        f.write(f"{thinking}\n\n")

                    if output:
                        f.write("### Output\n")
                        f.write(f"{output}\n\n")

                    # If no sections found, write the raw content
                    if not thinking and not output:
                        f.write(f"{content}\n\n")

                f.write("---\n\n")  # Add separator between entries

    def hide_console_panel(self):
        """Hide console panel and update menu action"""
        self.toggle_console_action.setChecked(False)
        self.toggle_console_panel()

    def toggle_console_panel(self):
        """Toggle console panel visibility"""
        is_visible = self.toggle_console_action.isChecked()
        self.console_panel.setVisible(is_visible)
        self.toggle_console_action.setText(
            "Hide Console" if is_visible else "Show Console"
        )

        if not is_visible:
            # Store the current sizes before hiding
            self.previous_sizes = self.main_splitter.sizes()
            # Collapse the console panel
            new_sizes = list(self.previous_sizes)
            new_sizes[-1] = 0
            self.main_splitter.setSizes(new_sizes)
        else:
            # Restore previous sizes if they exist
            if hasattr(self, "previous_sizes"):
                self.main_splitter.setSizes(self.previous_sizes)
