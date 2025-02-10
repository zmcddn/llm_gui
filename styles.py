from pygments.style import Style
from pygments.token import Comment, Generic, Keyword, Name, Number, Operator, String


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

    BUTTON = f"""
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
            background-color: {BACKGROUND_TERTIARY};
            width: 12px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {TEXT_SECONDARY}40;
            min-height: 20px;
            margin: 2px;
            border-radius: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {ACCENT_COLOR}80;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            border: none;
            background-color: {BACKGROUND_TERTIARY};
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
            background-color: {ACCENT_COLOR}80;
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

    # Code highlighting styles
    CODE_BLOCK = f"""
        pre.code-block {{
            background-color: {BACKGROUND_SECONDARY};
            padding: 1em;
            border-radius: 6px;
            margin: 1em 0;
            overflow-x: auto;
        }}
        .code-block code {{
            font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.4;
        }}

        /* Syntax highlighting */
        .highlight .k {{ color: {SYNTAX_KEYWORD}; }}  /* Keyword */
        .highlight .s {{ color: {SYNTAX_STRING}; }}   /* String */
        .highlight .n {{ color: {TEXT_PRIMARY}; }}    /* Name */
        .highlight .f {{ color: {SYNTAX_FUNCTION}; }} /* Function */
        .highlight .nb {{ color: {SYNTAX_FUNCTION}; }}/* Built-in */
        .highlight .nf {{ color: {SYNTAX_FUNCTION}; }}/* Function name */
        .highlight .mi {{ color: {SYNTAX_NUMBER}; }}  /* Number */
        .highlight .o {{ color: {TEXT_PRIMARY}; }}    /* Operator */
        .highlight .p {{ color: {TEXT_PRIMARY}; }}    /* Punctuation */

        /* Dark theme scrollbar for code blocks */
        pre.code-block::-webkit-scrollbar {{
            height: 8px;
            background-color: {BACKGROUND_SECONDARY};
        }}
        pre.code-block::-webkit-scrollbar-thumb {{
            background-color: {TEXT_SECONDARY};
            border-radius: 4px;
        }}
        pre.code-block::-webkit-scrollbar-thumb:hover {{
            background-color: {ACCENT_COLOR};
        }}
    """


class OneDarkStyle(Style):
    """VSCode One Dark inspired style for Pygments"""

    background_color = Styles.BACKGROUND_SECONDARY
    highlight_color = Styles.BACKGROUND_TERTIARY

    styles = {
        Keyword: Styles.SYNTAX_KEYWORD,
        Name.Function: Styles.SYNTAX_FUNCTION,
        Name.Class: Styles.SYNTAX_FUNCTION,
        String: Styles.SYNTAX_STRING,
        Number: Styles.SYNTAX_NUMBER,
        Operator: Styles.TEXT_PRIMARY,
        Name.Builtin: Styles.SYNTAX_FUNCTION,
        Comment: Styles.TEXT_SECONDARY,
        Generic: Styles.TEXT_PRIMARY,
    }
