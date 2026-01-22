#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileBrowser class for WebE IDE
Provides a file system browser dock widget
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QPushButton, QLineEdit, QFileSystemModel,
    QHBoxLayout
)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon


class FileBrowser(QWidget):
    """File browser widget for navigating file system"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create navigation bar
        nav_bar = QHBoxLayout()
        
        # Back button
        back_button = QPushButton("Back")
        nav_bar.addWidget(back_button)
        
        # Forward button
        forward_button = QPushButton("Forward")
        nav_bar.addWidget(forward_button)
        
        # Path line edit
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        nav_bar.addWidget(self.path_edit)
        
        # Home button
        home_button = QPushButton("Home")
        home_button.clicked.connect(self.go_home)
        nav_bar.addWidget(home_button)
        
        layout.addLayout(nav_bar)
        
        # Create file system model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.model.setReadOnly(True)
        self.model.setNameFilterDisables(False)
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(QDir.currentPath()))
        self.tree_view.setSortingEnabled(True)
        
        # Hide unnecessary columns
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        
        layout.addWidget(self.tree_view)
        
        # Update path edit
        self.update_path_edit()
        
        # Connect signals
        self.tree_view.clicked.connect(self.on_item_clicked)
        
        self.setLayout(layout)
    
    def go_home(self):
        """Go to home directory"""
        home_path = QDir.homePath()
        self.tree_view.setRootIndex(self.model.index(home_path))
        self.update_path_edit()
    
    def update_path_edit(self):
        """Update path line edit with current directory"""
        current_index = self.tree_view.rootIndex()
        current_path = self.model.filePath(current_index)
        self.path_edit.setText(current_path)
    
    def on_item_clicked(self, index):
        """Handle item click event"""
        if self.model.isDir(index):
            # If directory, expand/collapse
            if self.tree_view.isExpanded(index):
                self.tree_view.collapse(index)
            else:
                self.tree_view.expand(index)
        else:
            # If file, emit signal or handle opening
            file_path = self.model.filePath(index)
            print(f"File clicked: {file_path}")
            # TODO: Add signal to open file in editor
