#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File search functionality for WebE IDE
Supports searching text in files
"""

import os
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QCheckBox, QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt


class FileSearchDialog(QDialog):
    """File search dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Search")
        self.setGeometry(200, 200, 700, 500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search for:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter text to search")
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        
        self.case_sensitive_check = QCheckBox("Case Sensitive")
        options_layout.addWidget(self.case_sensitive_check)
        
        self.whole_word_check = QCheckBox("Whole Word")
        options_layout.addWidget(self.whole_word_check)
        
        self.regex_check = QCheckBox("Regular Expression")
        options_layout.addWidget(self.regex_check)
        
        layout.addLayout(options_layout)
        
        # File filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("File filter:"))
        self.file_filter = QComboBox()
        self.file_filter.addItems(["*.py", "*.txt", "*.md", "*.json", "All files (*.*)"])
        filter_layout.addWidget(self.file_filter)
        layout.addLayout(filter_layout)
        
        # Search results
        results_layout = QVBoxLayout()
        results_layout.addWidget(QLabel("Search Results:"))
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_file)
        results_layout.addWidget(self.results_list)
        layout.addLayout(results_layout)
        
        # Preview
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        preview_layout.addWidget(self.preview_edit)
        layout.addLayout(preview_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def perform_search(self):
        """Perform search"""
        search_text = self.search_input.text()
        if not search_text:
            QMessageBox.warning(self, "Error", "Please enter text to search")
            return
        
        # Get search options
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_word = self.whole_word_check.isChecked()
        use_regex = self.regex_check.isChecked()
        file_filter = self.file_filter.currentText()
        
        # Clear previous results
        self.results_list.clear()
        self.preview_edit.clear()
        
        # Start search from current directory
        current_dir = os.getcwd()
        matches = []
        
        # Convert file filter to glob pattern
        if file_filter == "All files (*.*)":
            glob_pattern = "*"
        else:
            glob_pattern = file_filter
        
        # Walk through directory
        for root, dirs, files in os.walk(current_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Check if file matches filter
                if self.matches_filter(file, glob_pattern):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line_num, line in enumerate(lines, 1):
                                if self.matches_search(line, search_text, case_sensitive, whole_word, use_regex):
                                    matches.append((file_path, line_num, line.strip()))
                    except:
                        # Skip files that can't be read
                        pass
        
        # Display results
        for file_path, line_num, line in matches:
            item = QListWidgetItem(f"{file_path}:{line_num} - {line[:100]}")
            item.setData(Qt.UserRole, (file_path, line_num, line))
            self.results_list.addItem(item)
        
        # Show message if no results
        if not matches:
            QMessageBox.information(self, "Info", "No matches found")
    
    def matches_filter(self, file_name, pattern):
        """Check if file matches filter"""
        if pattern == "*":
            return True
        
        # Simple pattern matching
        import fnmatch
        return fnmatch.fnmatch(file_name, pattern)
    
    def matches_search(self, line, search_text, case_sensitive, whole_word, use_regex):
        """Check if line matches search criteria"""
        if not case_sensitive:
            line = line.lower()
            search_text = search_text.lower()
        
        if use_regex:
            try:
                return bool(re.search(search_text, line))
            except:
                return search_text in line
        elif whole_word:
            return bool(re.search(rf'\b{re.escape(search_text)}\b', line))
        else:
            return search_text in line
    
    def open_file(self, item):
        """Open file from search result"""
        data = item.data(Qt.UserRole)
        if data:
            file_path, line_num, line = data
            # Preview the line and surrounding context
            self.preview_file(file_path, line_num)
            # Emit signal to open file in editor
            # For now, just show preview
    
    def preview_file(self, file_path, line_num):
        """Preview file at specific line"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start_line = max(0, line_num - 3)
                end_line = min(len(lines), line_num + 2)
                
                preview_text = f"File: {file_path}\nLine: {line_num}\n\n"
                for i in range(start_line, end_line):
                    if i == line_num - 1:
                        preview_text += f">> {i+1}: {lines[i]}"
                    else:
                        preview_text += f"   {i+1}: {lines[i]}"
                
                self.preview_edit.setPlainText(preview_text)
        except:
            self.preview_edit.setPlainText("Error reading file")
