#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal widget for WebE IDE
Provides a terminal emulator for running commands
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QScrollBar
)
from PyQt5.QtCore import Qt, QProcess, QByteArray
from PyQt5.QtGui import QFont, QTextCursor


class Terminal(QWidget):
    """Terminal widget for running commands"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.process = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont('Consolas', 10))
        self.output_area.setStyleSheet('background-color: #2d2d2d; color: #cccccc;')
        layout.addWidget(self.output_area)
        
        # Create input area
        input_layout = QHBoxLayout()
        
        self.prompt_label = QPushButton('>')
        self.prompt_label.setFixedWidth(30)
        self.prompt_label.setStyleSheet('background-color: #2d2d2d; color: #cccccc;')
        input_layout.addWidget(self.prompt_label)
        
        self.input_line = QLineEdit()
        self.input_line.setFont(QFont('Consolas', 10))
        self.input_line.setStyleSheet('background-color: #2d2d2d; color: #cccccc; border: none;')
        self.input_line.returnPressed.connect(self.execute_command)
        input_layout.addWidget(self.input_line)
        
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Start shell process
        self.start_shell()
    
    def start_shell(self):
        """Start shell process"""
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        
        # Start appropriate shell based on OS
        import sys
        if sys.platform == 'win32':
            self.process.start('cmd.exe')
        else:
            self.process.start('/bin/bash')
        
        # Connect signals
        self.process.readyRead.connect(self.read_output)
        self.process.finished.connect(self.shell_finished)
        
        # Show initial prompt
        self.output_area.append('WebE Terminal')
        self.output_area.append('==============')
        self.output_area.append('')
    
    def execute_command(self):
        """Execute command"""
        command = self.input_line.text()
        if not command:
            return
        
        # Add command to output
        self.output_area.append(f'> {command}')
        
        # Write command to process
        if self.process and self.process.state() == QProcess.Running:
            self.process.write((command + '\n').encode())
        
        # Clear input line
        self.input_line.clear()
    
    def read_output(self):
        """Read output from process"""
        if self.process:
            output = self.process.readAll().data().decode('utf-8', errors='replace')
            self.output_area.append(output)
            
            # Scroll to bottom
            cursor = self.output_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.output_area.setTextCursor(cursor)
    
    def shell_finished(self, exit_code, exit_status):
        """Handle shell finished"""
        self.output_area.append(f'Shell exited with code {exit_code}')
        self.prompt_label.setEnabled(False)
        self.input_line.setEnabled(False)
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            self.process.waitForFinished(1000)
        super().closeEvent(event)
