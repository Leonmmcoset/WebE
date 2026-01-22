#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git integration for WebE IDE
Supports basic Git operations
"""

import os
import subprocess
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QLineEdit, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt


class GitManager:
    """Git manager for WebE IDE"""
    
    def __init__(self):
        self.current_repo = None
    
    def get_current_repo(self):
        """Get current repository path"""
        return self.current_repo
    
    def set_current_repo(self, repo_path):
        """Set current repository path"""
        self.current_repo = repo_path
    
    def run_git_command(self, command, repo_path=None):
        """Run Git command"""
        if not repo_path:
            repo_path = self.current_repo
        
        if not repo_path:
            return None, "No repository selected"
        
        try:
            result = subprocess.run(
                command, 
                cwd=repo_path, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            return result.returncode, result.stdout + result.stderr
        except Exception as e:
            return 1, str(e)
    
    def init_repo(self, repo_path):
        """Initialize Git repository"""
        return self.run_git_command("git init", repo_path)
    
    def git_status(self, repo_path=None):
        """Get Git status"""
        return self.run_git_command("git status", repo_path)
    
    def git_add(self, files=None, repo_path=None):
        """Add files to Git"""
        if files:
            files_str = ' '.join(files)
            return self.run_git_command(f"git add {files_str}", repo_path)
        else:
            return self.run_git_command("git add .", repo_path)
    
    def git_commit(self, message, repo_path=None):
        """Commit changes"""
        return self.run_git_command(f"git commit -m \"{message}\"", repo_path)
    
    def git_push(self, remote="origin", branch="main", repo_path=None):
        """Push changes"""
        return self.run_git_command(f"git push {remote} {branch}", repo_path)
    
    def git_pull(self, remote="origin", branch="main", repo_path=None):
        """Pull changes"""
        return self.run_git_command(f"git pull {remote} {branch}", repo_path)
    
    def git_branch(self, repo_path=None):
        """List branches"""
        return self.run_git_command("git branch", repo_path)
    
    def git_checkout(self, branch, repo_path=None):
        """Checkout branch"""
        return self.run_git_command(f"git checkout {branch}", repo_path)
    
    def git_merge(self, branch, repo_path=None):
        """Merge branch"""
        return self.run_git_command(f"git merge {branch}", repo_path)


class GitDialog(QDialog):
    """Git operations dialog"""
    
    def __init__(self, git_manager, parent=None):
        super().__init__(parent)
        self.git_manager = git_manager
        self.setWindowTitle("Git Operations")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Output area
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Git Output:"))
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        output_layout.addWidget(self.output_area)
        layout.addLayout(output_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        status_button = QPushButton("Status")
        status_button.clicked.connect(self.git_status)
        buttons_layout.addWidget(status_button)
        
        add_button = QPushButton("Add All")
        add_button.clicked.connect(self.git_add_all)
        buttons_layout.addWidget(add_button)
        
        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(self.git_commit)
        buttons_layout.addWidget(commit_button)
        
        push_button = QPushButton("Push")
        push_button.clicked.connect(self.git_push)
        buttons_layout.addWidget(push_button)
        
        pull_button = QPushButton("Pull")
        pull_button.clicked.connect(self.git_pull)
        buttons_layout.addWidget(pull_button)
        
        branch_button = QPushButton("Branches")
        branch_button.clicked.connect(self.git_branch)
        buttons_layout.addWidget(branch_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def git_status(self):
        """Show Git status"""
        self.output_area.clear()
        code, output = self.git_manager.git_status()
        self.output_area.append(f"Exit code: {code}")
        self.output_area.append(output)
    
    def git_add_all(self):
        """Add all files"""
        self.output_area.clear()
        code, output = self.git_manager.git_add()
        self.output_area.append(f"Exit code: {code}")
        self.output_area.append(output)
    
    def git_commit(self):
        """Commit changes"""
        message, ok = QInputDialog.getText(self, "Commit Message", "Enter commit message:")
        if ok and message:
            self.output_area.clear()
            code, output = self.git_manager.git_commit(message)
            self.output_area.append(f"Exit code: {code}")
            self.output_area.append(output)
    
    def git_push(self):
        """Push changes"""
        self.output_area.clear()
        code, output = self.git_manager.git_push()
        self.output_area.append(f"Exit code: {code}")
        self.output_area.append(output)
    
    def git_pull(self):
        """Pull changes"""
        self.output_area.clear()
        code, output = self.git_manager.git_pull()
        self.output_area.append(f"Exit code: {code}")
        self.output_area.append(output)
    
    def git_branch(self):
        """Show branches"""
        self.output_area.clear()
        code, output = self.git_manager.git_branch()
        self.output_area.append(f"Exit code: {code}")
        self.output_area.append(output)


class GitInitDialog(QDialog):
    """Git initialization dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initialize Git Repository")
        self.setGeometry(200, 200, 500, 200)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Repository path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Repository Path:"))
        self.path_edit = QLineEdit()
        path_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_button)
        
        layout.addLayout(path_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.init_button = QPushButton("Initialize")
        self.init_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.init_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def browse_path(self):
        """Browse for repository path"""
        from PyQt5.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Select Repository Directory")
        if path:
            self.path_edit.setText(path)
    
    def get_repo_path(self):
        """Get repository path"""
        return self.path_edit.text()
