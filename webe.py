#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebE - Python IDE based on PyQt5
Main entry point for the application
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.mainwindow import MainWindow


def main():
    """Main function to launch the WebE IDE"""
    app = QApplication(sys.argv)
    app.setApplicationName("WebE")
    app.setOrganizationName("WebE IDE")
    app.setOrganizationDomain("webe-ide.org")
    
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
