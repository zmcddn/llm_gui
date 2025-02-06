class Styles:
    # VSCode One Dark color palette
    BACKGROUND_PRIMARY = "#282c34"  # Main background
    BACKGROUND_SECONDARY = "#21252b"  # Sidebar/panel background
    BACKGROUND_TERTIARY = "#2c313a"  # Input/active areas

    TEXT_PRIMARY = "#abb2bf"  # Main text color
    TEXT_SECONDARY = "#5c6370"  # Secondary text/comments
    ACCENT_COLOR = "#61afef"  # Blue for buttons/highlights
    BORDER_COLOR = "#181a1f"  # Dark borders

    # Syntax highlighting colors (for potential future use)
    SYNTAX_STRING = "#98c379"  # Green
    SYNTAX_KEYWORD = "#c678dd"  # Purple
    SYNTAX_FUNCTION = "#61afef"  # Blue
    SYNTAX_NUMBER = "#d19a66"  # Orange

    ERROR_COLOR = "#e06c75"  # Red
    SUCCESS_COLOR = "#98c379"  # Green

    # Common styles
    COMMON = f"""
        QWidget {{
            font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
            font-size: 13px;
            color: {TEXT_PRIMARY};
            background-color: {BACKGROUND_PRIMARY};
        }}
    """

    # Main window
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {BACKGROUND_PRIMARY};
        }}
    """

    # Menu bar
    MENU_BAR = f"""
        QMenuBar {{
            background-color: {BACKGROUND_SECONDARY};
            border-bottom: 1px solid {BORDER_COLOR};
            padding: 2px;
        }}
        QMenuBar::item {{
            padding: 4px 10px;
            background-color: transparent;
            border-radius: 4px;
        }}
        QMenuBar::item:selected {{
            background-color: {BACKGROUND_TERTIARY};
        }}
        QMenu {{
            background-color: {BACKGROUND_SECONDARY};
            border: 1px solid {BORDER_COLOR};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 4px 20px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {BACKGROUND_TERTIARY};
        }}
    """

    # Panels
    PANEL_HEADER = f"""
        QTextEdit {{
            background-color: {BACKGROUND_SECONDARY};
            color: {TEXT_PRIMARY};
            border: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px;
            font-weight: bold;
            /* Disable scrollbars */
            overflow: hidden;
        }}
        QTextEdit::viewport {{
            background: transparent;
        }}
    """

    PANEL_CONTENT = f"""
        QTextEdit {{
            background-color: {BACKGROUND_TERTIARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            padding: 8px;
            selection-background-color: {ACCENT_COLOR}40;
        }}
        QTextEdit::viewport {{
            border: none;
        }}
    """

    # Input area
    MODEL_SELECTOR = f"""
        QComboBox {{
            background-color: {BACKGROUND_TERTIARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-radius: 4px;
            padding: 4px 8px;
            min-height: 24px;
        }}
        QComboBox:hover {{
            border-color: {ACCENT_COLOR};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: url(resources/down-arrow-light.png);
            width: 12px;
            height: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {BACKGROUND_SECONDARY};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            selection-background-color: {BACKGROUND_TERTIARY};
        }}
    """

    SEND_BUTTON = f"""
        QPushButton {{
            background-color: {ACCENT_COLOR};
            color: {BACKGROUND_PRIMARY};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_COLOR}dd;
        }}
        QPushButton:pressed {{
            background-color: {ACCENT_COLOR}bb;
        }}
        QPushButton:disabled {{
            background-color: {TEXT_SECONDARY};
            color: {TEXT_PRIMARY}77;
        }}
    """

    # Splitters
    SPLITTER = f"""
        QSplitter::handle {{
            background-color: {BORDER_COLOR};
            margin: 1px;
        }}
        QSplitter::handle:hover {{
            background-color: {ACCENT_COLOR};
        }}
    """

    # Scrollbars - VSCode style
    SCROLLBAR = f"""
        QScrollBar:vertical {{
            border: none;
            background-color: {BACKGROUND_PRIMARY};
            width: 14px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {TEXT_SECONDARY}40;
            min-height: 20px;
            margin: 2px;
            border-radius: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {TEXT_SECONDARY}80;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            border: none;
            background-color: {BACKGROUND_PRIMARY};
            height: 14px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {TEXT_SECONDARY}40;
            min-width: 20px;
            margin: 2px;
            border-radius: 2px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {TEXT_SECONDARY}80;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
    """

    # Close button
    CLOSE_BUTTON = f"""
        QPushButton {{
            background-color: transparent;
            color: {TEXT_SECONDARY};
            border: none;
            border-radius: 2px;
            font-size: 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ERROR_COLOR}40;
            color: {ERROR_COLOR};
        }}
        QPushButton:pressed {{
            background-color: {ERROR_COLOR}60;
            color: {ERROR_COLOR};
        }}
    """
