#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code statistics functionality for WebE IDE
Supports displaying file statistics like line count, word count, etc.
"""

import os
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt


class CodeStatisticsDialog(QDialog):
    """Code statistics dialog"""
    
    def __init__(self, current_file=None, parent=None):
        super().__init__(parent)
        self.current_file = current_file
        self.setWindowTitle("Code Statistics")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Statistics table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.stats_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        analyze_button = QPushButton("Analyze Current File")
        analyze_button.clicked.connect(self.analyze_current_file)
        buttons_layout.addWidget(analyze_button)
        
        analyze_project_button = QPushButton("Analyze Project")
        analyze_project_button.clicked.connect(self.analyze_project)
        buttons_layout.addWidget(analyze_project_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Analyze current file if provided
        if self.current_file:
            self.analyze_current_file()
    
    def analyze_current_file(self):
        """Analyze current file"""
        if not self.current_file:
            QMessageBox.warning(self, "Error", "No file selected")
            return
        
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Calculate statistics
                stats = {
                    "File": os.path.basename(self.current_file),
                    "Total Lines": len(lines),
                    "Empty Lines": sum(1 for line in lines if line.strip() == ''),
                    "Code Lines": sum(1 for line in lines if line.strip() != '' and not line.strip().startswith('#')),
                    "Comment Lines": sum(1 for line in lines if line.strip().startswith('#')),
                    "Total Characters": len(content),
                    "Total Words": len(re.findall(r'\b\w+\b', content)),
                    "Average Line Length": round(len(content) / len(lines), 2) if lines else 0
                }
                
                self.display_statistics(stats)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to analyze file: {str(e)}")
    
    def analyze_project(self):
        """Analyze entire project"""
        project_dir = os.getcwd()
        
        # Collect all Python files
        python_files = []
        for root, dirs, files in os.walk(project_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        if not python_files:
            QMessageBox.warning(self, "Error", "No Python files found in project")
            return
        
        # Calculate project-wide statistics
        total_lines = 0
        empty_lines = 0
        code_lines = 0
        comment_lines = 0
        total_characters = 0
        total_words = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    total_lines += len(lines)
                    empty_lines += sum(1 for line in lines if line.strip() == '')
                    code_lines += sum(1 for line in lines if line.strip() != '' and not line.strip().startswith('#'))
                    comment_lines += sum(1 for line in lines if line.strip().startswith('#'))
                    total_characters += len(content)
                    total_words += len(re.findall(r'\b\w+\b', content))
            except:
                # Skip files that can't be read
                pass
        
        # Display project statistics
        stats = {
            "Project": os.path.basename(project_dir),
            "Python Files": len(python_files),
            "Total Lines": total_lines,
            "Empty Lines": empty_lines,
            "Code Lines": code_lines,
            "Comment Lines": comment_lines,
            "Total Characters": total_characters,
            "Total Words": total_words,
            "Average Line Length": round(total_characters / total_lines, 2) if total_lines else 0,
            "Code to Comment Ratio": round(code_lines / comment_lines, 2) if comment_lines else 0
        }
        
        self.display_statistics(stats)
    
    def display_statistics(self, stats):
        """Display statistics in table"""
        self.stats_table.setRowCount(len(stats))
        
        for row, (metric, value) in enumerate(stats.items()):
            metric_item = QTableWidgetItem(metric)
            metric_item.setFlags(Qt.ItemIsEnabled)
            self.stats_table.setItem(row, 0, metric_item)
            
            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(Qt.ItemIsEnabled)
            value_item.setTextAlignment(Qt.AlignRight)
            self.stats_table.setItem(row, 1, value_item)
        
        # Resize rows
        self.stats_table.resizeRowsToContents()
