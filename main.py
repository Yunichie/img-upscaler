#!/usr/bin/env python
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.gui.main_window import App


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    window = App()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()