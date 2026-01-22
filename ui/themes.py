#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Theme management for WebE IDE
Supports light and dark themes
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


class ThemeManager:
    """Theme manager for WebE IDE"""
    
    def __init__(self):
        self.current_theme = 'light'
    
    def get_theme(self):
        """Get current theme"""
        return self.current_theme
    
    def set_theme(self, theme):
        """Set current theme"""
        self.current_theme = theme
    
    def apply_theme(self, app, main_window):
        """Apply theme to application"""
        if self.current_theme == 'dark':
            self.apply_dark_theme(app, main_window)
        else:
            self.apply_light_theme(app, main_window)
    
    def apply_light_theme(self, app, main_window):
        """Apply light theme"""
        # Set application palette
        palette = app.palette()
        
        # Window background
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        
        # Base (editors, etc.)
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        
        # Buttons
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        
        # Highlight
        palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
        
        # Apply to specific widgets
        if main_window:
            # Editor
            for editor in main_window.editors:
                editor.setStyleSheet('')
                editor.highlight_current_line()
            
            # Terminal
            if hasattr(main_window, 'terminal'):
                main_window.terminal.output_area.setStyleSheet('background-color: #ffffff; color: #000000;')
                main_window.terminal.input_line.setStyleSheet('background-color: #ffffff; color: #000000; border: none;')
                main_window.terminal.prompt_label.setStyleSheet('background-color: #ffffff; color: #000000;')
    
    def apply_dark_theme(self, app, main_window):
        """Apply dark theme"""
        # Set application palette
        palette = app.palette()
        
        # Window background
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
        
        # Base (editors, etc.)
        palette.setColor(QPalette.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        
        # Buttons
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
        
        # Highlight
        palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
        
        # Apply to specific widgets
        if main_window:
            # Editor
            for editor in main_window.editors:
                editor.setStyleSheet('background-color: #2d2d2d; color: #cccccc;')
                editor.highlight_current_line()
            
            # Terminal
            if hasattr(main_window, 'terminal'):
                main_window.terminal.output_area.setStyleSheet('background-color: #2d2d2d; color: #cccccc;')
                main_window.terminal.input_line.setStyleSheet('background-color: #2d2d2d; color: #cccccc; border: none;')
                main_window.terminal.prompt_label.setStyleSheet('background-color: #2d2d2d; color: #cccccc;')
