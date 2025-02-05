import sys

from PySide6.QtWidgets import QApplication

from gui import OllamaGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OllamaGUI()
    window.show()
    sys.exit(app.exec())
