#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project manager for WebE IDE
Supports creating and managing projects
"""

import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt


class ProjectManager:
    """Project manager for WebE IDE"""
    
    def __init__(self):
        self.current_project = None
    
    def get_current_project(self):
        """Get current project"""
        return self.current_project
    
    def set_current_project(self, project):
        """Set current project"""
        self.current_project = project
    
    def create_project(self, parent=None):
        """Create new project"""
        dialog = CreateProjectDialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            project_path = dialog.get_project_path()
            project_name = dialog.get_project_name()
            
            # Create project directory
            if not os.path.exists(project_path):
                os.makedirs(project_path)
            
            # Create project file
            project_file = os.path.join(project_path, f'{project_name}.webe.json')
            project_data = {
                'name': project_name,
                'path': project_path,
                'files': []
            }
            
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4)
            
            # Set current project
            self.current_project = project_data
            return project_data
        return None
    
    def open_project(self, parent=None):
        """Open existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "Open Project", "", "WebE Project Files (*.webe.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # Set current project
                self.current_project = project_data
                return project_data
            except Exception as e:
                QMessageBox.warning(parent, "Error", f"Failed to open project: {str(e)}")
        return None
    
    def add_file_to_project(self, file_path):
        """Add file to current project"""
        if self.current_project:
            project_file = os.path.join(
                self.current_project['path'], 
                f'{self.current_project["name"]}.webe.json'
            )
            
            # Add file to project data
            if file_path not in self.current_project['files']:
                self.current_project['files'].append(file_path)
                
                # Save project data
                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_project, f, indent=4)
    
    def remove_file_from_project(self, file_path):
        """Remove file from current project"""
        if self.current_project:
            project_file = os.path.join(
                self.current_project['path'], 
                f'{self.current_project["name"]}.webe.json'
            )
            
            # Remove file from project data
            if file_path in self.current_project['files']:
                self.current_project['files'].remove(file_path)
                
                # Save project data
                with open(project_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_project, f, indent=4)


class CreateProjectDialog(QDialog):
    """Dialog for creating new project"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setGeometry(200, 200, 500, 300)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Project name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Project path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Project Path:"))
        self.path_edit = QLineEdit()
        path_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)
        
        layout.addLayout(path_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.create_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def browse_path(self):
        """Browse for project path"""
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if path:
            self.path_edit.setText(path)
    
    def get_project_name(self):
        """Get project name"""
        return self.name_edit.text()
    
    def get_project_path(self):
        """Get project path"""
        return self.path_edit.text()
    
    def accept(self):
        """Accept dialog"""
        if not self.name_edit.text():
            QMessageBox.warning(self, "Error", "Project name is required")
            return
        
        if not self.path_edit.text():
            QMessageBox.warning(self, "Error", "Project path is required")
            return
        
        super().accept()


class ProjectFilesDialog(QDialog):
    """Dialog for managing project files"""
    
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.setWindowTitle(f"Project Files - {project_data['name']}")
        self.setGeometry(200, 200, 600, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Files list
        self.files_list = QListWidget()
        for file_path in self.project_data['files']:
            item = QListWidgetItem(file_path)
            self.files_list.addItem(item)
        layout.addWidget(self.files_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add File")
        add_button.clicked.connect(self.add_file)
        buttons_layout.addWidget(add_button)
        
        remove_button = QPushButton("Remove File")
        remove_button.clicked.connect(self.remove_file)
        buttons_layout.addWidget(remove_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def add_file(self):
        """Add file to project"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Add Files", self.project_data['path']
        )
        
        for file_path in file_paths:
            if file_path not in self.project_data['files']:
                self.project_data['files'].append(file_path)
                item = QListWidgetItem(file_path)
                self.files_list.addItem(item)
        
        # Save project data
        self.save_project()
    
    def remove_file(self):
        """Remove file from project"""
        selected_items = self.files_list.selectedItems()
        for item in selected_items:
            file_path = item.text()
            if file_path in self.project_data['files']:
                self.project_data['files'].remove(file_path)
            self.files_list.takeItem(self.files_list.row(item))
        
        # Save project data
        self.save_project()
    
    def save_project(self):
        """Save project data"""
        project_file = os.path.join(
            self.project_data['path'], 
            f'{self.project_data["name"]}.webe.json'
        )
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(self.project_data, f, indent=4)
