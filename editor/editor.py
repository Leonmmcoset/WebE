#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeEditor class for WebE IDE
Implements core editing functionality with syntax highlighting and line numbers
"""

from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QCompleter
from PyQt5.QtCore import Qt, QRect, QSize, QStringListModel
from PyQt5.QtGui import (
    QColor, QTextFormat, QPainter, QFont, QSyntaxHighlighter, QTextCharFormat,
    QFontDatabase
)


class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self):
        """Return size hint for line number area"""
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        """Paint line numbers"""
        self.code_editor.line_number_area_paint_event(event)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define syntax highlighting rules
        self.highlighting_rules = []
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(167, 109, 227))
        keyword_format.setFontWeight(QFont.Bold)
        
        # Python keywords
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]
        
        for keyword in keywords:
            self.highlighting_rules.append((f'\\b{keyword}\\b', keyword_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(103, 141, 25))
        
        # String rules
        self.highlighting_rules.append((r'"[^"]*"', string_format))
        self.highlighting_rules.append((r"'[^']*'", string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))
        
        # Comment rule
        self.highlighting_rules.append((r'#.*$', comment_format))
        
        # Function and class names format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(76, 175, 80))
        function_format.setFontWeight(QFont.Bold)
        
        # Function and class rules
        self.highlighting_rules.append((r'def\s+(\w+)\s*\(', function_format))
        self.highlighting_rules.append((r'class\s+(\w+)\s*\(', function_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            import re
            matches = re.finditer(pattern, text)
            for match in matches:
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers and syntax highlighting"""
    
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Set font
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(10)
        self.setFont(font)
        
        # Set tab width
        self.setTabStopWidth(4 * font.pointSize())
        
        # Enable syntax highlighting
        self.highlighter = PythonSyntaxHighlighter(self.document())
        
        # Highlight current line
        self.highlight_current_line()
        
        # Update line number area width
        self.update_line_number_area_width(0)
    

    
    def line_number_area_width(self):
        """Calculate width of line number area"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        
        space = 3 + self.fontMetrics().width('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Update line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update line number area"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Paint event for line number area"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        # Draw line numbers
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(128, 128, 128))
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 3, 
                    self.fontMetrics().height(), Qt.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlight_current_line(self):
        """Highlight current line"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(245, 245, 245)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def toggle_fold(self, block):
        """Toggle fold state of a block"""
        if block.isValid():
            # Use userState to track collapse state
            if block.userState() == 1:
                # Expand block
                block.setUserState(0)
                # Show all child blocks
                level = self.get_indent_level(block)
                next_block = block.next()
                while next_block.isValid() and self.get_indent_level(next_block) > level:
                    next_block.setVisible(True)
                    next_block = next_block.next()
            else:
                # Collapse block
                block.setUserState(1)
                # Hide child blocks
                level = self.get_indent_level(block)
                next_block = block.next()
                while next_block.isValid() and self.get_indent_level(next_block) > level:
                    next_block.setVisible(False)
                    next_block = next_block.next()
    
    def get_indent_level(self, block):
        """Get indentation level of a block"""
        text = block.text()
        return len(text) - len(text.lstrip())
    

    
    def line_number_area_paint_event(self, event):
        """Paint event for line number area"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        # Draw line numbers and fold indicators
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(128, 128, 128))
                painter.drawText(
                    0, int(top), self.line_number_area.width() - 15, 
                    self.fontMetrics().height(), Qt.AlignRight, number
                )
                
                # Draw fold indicator
                if self.can_fold(block):
                    fold_rect = QRect(
                        self.line_number_area.width() - 12, 
                        int(top) + 2, 
                        10, 
                        self.fontMetrics().height() - 4
                    )
                    painter.fillRect(fold_rect, QColor(200, 200, 200))
                    painter.setPen(QColor(100, 100, 100))
                    
                    if block.userState() == 1:
                        # Draw expand indicator
                        painter.drawText(fold_rect, Qt.AlignCenter, "+")
                    else:
                        # Draw collapse indicator
                        painter.drawText(fold_rect, Qt.AlignCenter, "-")
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def can_fold(self, block):
        """Check if a block can be folded"""
        if not block.isValid():
            return False
        
        level = self.get_indent_level(block)
        next_block = block.next()
        return next_block.isValid() and self.get_indent_level(next_block) > level
    
    def mousePressEvent(self, event):
        """Handle mouse press event for fold toggling"""
        if event.button() == Qt.LeftButton:
            # Check if click is in line number area
            if event.x() < self.line_number_area_width():
                # Calculate which line was clicked
                block = self.blockAtPosition(event.pos())
                if block.isValid():
                    # Check if click is on fold indicator
                    fold_rect = QRect(
                        self.line_number_area_width() - 12, 
                        0, 
                        10, 
                        self.fontMetrics().height()
                    )
                    if fold_rect.contains(event.pos() - self.line_number_area.pos()):
                        self.toggle_fold(block)
                        return
        
        super().mousePressEvent(event)
    
    def blockAtPosition(self, pos):
        """Get block at given position"""
        return self.document().findBlockByLineNumber(
            self.cursorForPosition(pos).blockNumber()
        )
