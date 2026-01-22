#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code snippets manager for WebE IDE
Supports storing and inserting code snippets
"""

import json
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
    QTextEdit, QLineEdit, QLabel, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt


class SnippetManager:
    """Code snippet manager"""
    
    def __init__(self):
        self.snippets = self.load_snippets()
    
    def load_snippets(self):
        """Load snippets from file"""
        snippet_file = os.path.join(os.path.dirname(__file__), '..', 'snippets.json')
        
        # Default snippets
        default_snippets = [
            {
                "name": "For Loop",
                "prefix": "for",
                "body": "for item in iterable:\n    # TODO: Process item\n    pass"
            },
            {
                "name": "While Loop",
                "prefix": "while",
                "body": "while condition:\n    # TODO: Process\n    pass"
            },
            {
                "name": "If Statement",
                "prefix": "if",
                "body": "if condition:\n    # TODO: Process\n    pass\nelif another_condition:\n    # TODO: Process\n    pass\nelse:\n    # TODO: Process\n    pass"
            },
            {
                "name": "Function Definition",
                "prefix": "def",
                "body": "def function_name(parameters):\n    \"\"\"Function docstring\"\"\"\n    # TODO: Implement function\n    return result"
            },
            {
                "name": "Class Definition",
                "prefix": "class",
                "body": "class ClassName:\n    \"\"\"Class docstring\"\"\"\n    \n    def __init__(self, parameters):\n        self.parameters = parameters\n    \n    def method(self):\n        \"\"\"Method docstring\"\"\"\n        # TODO: Implement method\n        pass"
            },
            {
                "name": "Try-Except Block",
                "prefix": "try",
                "body": "try:\n    # TODO: Risky operation\n    pass\nexcept Exception as e:\n    # TODO: Handle exception\n    print(f'Error: {e}')\nfinally:\n    # TODO: Cleanup\n    pass"
            },
            {
                "name": "Import Statements",
                "prefix": "import",
                "body": "import os\nimport sys\nimport json\nfrom datetime import datetime"
            },
            {
                "name": "Main Block",
                "prefix": "main",
                "body": "if __name__ == \"__main__\":\n    # TODO: Main execution\n    pass"
            }
        ]
        
        # Load from file if exists
        if os.path.exists(snippet_file):
            try:
                with open(snippet_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_snippets
        else:
            # Save default snippets
            self.save_snippets(default_snippets)
            return default_snippets
    
    def save_snippets(self, snippets):
        """Save snippets to file"""
        snippet_file = os.path.join(os.path.dirname(__file__), '..', 'snippets.json')
        try:
            with open(snippet_file, 'w', encoding='utf-8') as f:
                json.dump(snippets, f, indent=4)
            return True
        except:
            return False
    
    def get_snippets(self):
        """Get all snippets"""
        return self.snippets
    
    def add_snippet(self, name, prefix, body):
        """Add new snippet"""
        snippet = {
            "name": name,
            "prefix": prefix,
            "body": body
        }
        self.snippets.append(snippet)
        self.save_snippets(self.snippets)
    
    def update_snippet(self, index, name, prefix, body):
        """Update existing snippet"""
        if 0 <= index < len(self.snippets):
            self.snippets[index] = {
                "name": name,
                "prefix": prefix,
                "body": body
            }
            self.save_snippets(self.snippets)
    
    def delete_snippet(self, index):
        """Delete snippet"""
        if 0 <= index < len(self.snippets):
            self.snippets.pop(index)
            self.save_snippets(self.snippets)
    
    def get_snippet_by_prefix(self, prefix):
        """Get snippet by prefix"""
        for snippet in self.snippets:
            if snippet['prefix'] == prefix:
                return snippet
        return None


class SnippetDialog(QDialog):
    """Snippet management dialog"""
    
    def __init__(self, snippet_manager, parent=None):
        super().__init__(parent)
        self.snippet_manager = snippet_manager
        self.setWindowTitle("Code Snippets")
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Snippets list
        self.snippets_list = QListWidget()
        self.update_snippets_list()
        self.snippets_list.itemClicked.connect(self.on_snippet_selected)
        layout.addWidget(self.snippets_list)
        
        # Snippet details
        details_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        details_layout.addLayout(name_layout)
        
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("Prefix:"))
        self.prefix_edit = QLineEdit()
        prefix_layout.addWidget(self.prefix_edit)
        details_layout.addLayout(prefix_layout)
        
        body_layout = QVBoxLayout()
        body_layout.addWidget(QLabel("Body:"))
        self.body_edit = QTextEdit()
        body_layout.addWidget(self.body_edit)
        details_layout.addLayout(body_layout)
        
        layout.addLayout(details_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_snippet)
        buttons_layout.addWidget(add_button)
        
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_snippet)
        buttons_layout.addWidget(update_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_snippet)
        buttons_layout.addWidget(delete_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def update_snippets_list(self):
        """Update snippets list"""
        self.snippets_list.clear()
        for snippet in self.snippet_manager.get_snippets():
            item = QListWidgetItem(f"{snippet['name']} (prefix: {snippet['prefix']})")
            self.snippets_list.addItem(item)
    
    def on_snippet_selected(self, item):
        """Handle snippet selection"""
        index = self.snippets_list.row(item)
        snippet = self.snippet_manager.get_snippets()[index]
        self.name_edit.setText(snippet['name'])
        self.prefix_edit.setText(snippet['prefix'])
        self.body_edit.setPlainText(snippet['body'])
    
    def add_snippet(self):
        """Add new snippet"""
        name = self.name_edit.text()
        prefix = self.prefix_edit.text()
        body = self.body_edit.toPlainText()
        
        if not name or not prefix or not body:
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        self.snippet_manager.add_snippet(name, prefix, body)
        self.update_snippets_list()
        QMessageBox.information(self, "Success", "Snippet added successfully")
    
    def update_snippet(self):
        """Update snippet"""
        selected_item = self.snippets_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "No snippet selected")
            return
        
        index = self.snippets_list.row(selected_item)
        name = self.name_edit.text()
        prefix = self.prefix_edit.text()
        body = self.body_edit.toPlainText()
        
        if not name or not prefix or not body:
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        self.snippet_manager.update_snippet(index, name, prefix, body)
        self.update_snippets_list()
        QMessageBox.information(self, "Success", "Snippet updated successfully")
    
    def delete_snippet(self):
        """Delete snippet"""
        selected_item = self.snippets_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "No snippet selected")
            return
        
        if QMessageBox.question(self, "Confirm", "Are you sure you want to delete this snippet?") == QMessageBox.Yes:
            index = self.snippets_list.row(selected_item)
            self.snippet_manager.delete_snippet(index)
            self.update_snippets_list()
            QMessageBox.information(self, "Success", "Snippet deleted successfully")
