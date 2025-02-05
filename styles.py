class Styles:
    # Color palette
    BACKGROUND_PRIMARY = "#ffffff"
    BACKGROUND_SECONDARY = "#f5f7f9"
    BACKGROUND_TERTIARY = "#e9ecef"

    TEXT_PRIMARY = "#2d3436"
    TEXT_SECONDARY = "#636e72"
    ACCENT_COLOR = "#0984e3"
    BORDER_COLOR = "#dfe6e9"

    ERROR_COLOR = "#d63031"
    SUCCESS_COLOR = "#00b894"

    # Common styles
    COMMON = f"""
        QWidget {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            color: {TEXT_PRIMARY};
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
            background-color: {BACKGROUND_PRIMARY};
            border-bottom: 1px solid {BORDER_COLOR};
            padding: 2px;
        }}
        QMenuBar::item {{
            padding: 4px 10px;
            background-color: transparent;
        }}
        QMenuBar::item:selected {{
            background-color: {BACKGROUND_SECONDARY};
            border-radius: 4px;
        }}
    """

    # Panels
    PANEL_HEADER = f"""
        QTextEdit {{
            background-color: {BACKGROUND_SECONDARY};
            border: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
            /* Disable scrollbars */
            overflow: hidden;
        }}
        QTextEdit::viewport {{
            background: transparent;
        }}
    """

    PANEL_CONTENT = f"""
        QTextEdit {{
            background-color: {BACKGROUND_PRIMARY};
            border: 1px solid {BORDER_COLOR};
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            padding: 8px;
            selection-background-color: {ACCENT_COLOR}40;
        }}
    """

    # Input area
    MODEL_SELECTOR = f"""
        QComboBox {{
            background-color: {BACKGROUND_PRIMARY};
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
            image: url(resources/down-arrow.png);
            width: 12px;
            height: 12px;
        }}
    """

    SEND_BUTTON = f"""
        QPushButton {{
            background-color: {ACCENT_COLOR};
            color: white;
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
    """

    # Splitters
    SPLITTER = f"""
        QSplitter::handle {{
            background-color: {BORDER_COLOR};
            margin: 2px;
        }}
        QSplitter::handle:hover {{
            background-color: {ACCENT_COLOR};
        }}
    """

    # Scrollbars
    SCROLLBAR = f"""
        QScrollBar:vertical {{
            border: none;
            background-color: {BACKGROUND_SECONDARY};
            width: 8px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {TEXT_SECONDARY};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {ACCENT_COLOR};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """
