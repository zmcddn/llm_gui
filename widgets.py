from PySide6.QtWidgets import QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget


class CollapsibleFrame(QWidget):
    """Collapsible panel component"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setup_ui(title)

    def setup_ui(self, title):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                padding: 5px;
                background-color: #f0f0f0;
                border: none;
            }
        """
        )
        self.toggle_button.clicked.connect(self.toggle_content)

        self.content = QTextEdit()
        self.content.setReadOnly(True)
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content)

        self.is_collapsed = False
        self.content.setVisible(True)

    def toggle_content(self):
        """Toggle content area visibility"""
        self.is_collapsed = not self.is_collapsed
        self.content.setVisible(not self.is_collapsed)
        self.content.setMaximumHeight(0 if self.is_collapsed else 16777215)
