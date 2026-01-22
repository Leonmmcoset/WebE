#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MainWindow class for WebE IDE
"""

from PyQt5.QtWidgets import (
    QMainWindow, QAction, QMenu, QToolBar, QFileDialog, QMessageBox,
    QDockWidget, QTreeView, QSplitter, QTabWidget
)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QIcon
from editor.editor import CodeEditor
from ui.filebrowser import FileBrowser
from ui.terminal import Terminal
from ui.themes import ThemeManager
from ui.projectmanager import ProjectManager, ProjectFilesDialog
from ui.debugger import DebuggerDialog
from ui.gitintegration import GitManager, GitDialog, GitInitDialog
from ui.snippets import SnippetManager, SnippetDialog


class MainWindow(QMainWindow):
    """Main window class for WebE IDE"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.editors = []
        self.theme_manager = ThemeManager()
        self.project_manager = ProjectManager()
        self.git_manager = GitManager()
        self.snippet_manager = SnippetManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle("WebE - Untitled")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget (tabbed editor)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)
        
        # Create initial empty editor
        self.new_file()
        
        # Create file browser dock
        self.file_browser = FileBrowser()
        self.file_browser.tree_view.doubleClicked.connect(self.on_file_double_clicked)
        self.file_dock = QDockWidget("File Browser", self)
        self.file_dock.setWidget(self.file_browser)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_dock)
        
        # Create terminal dock
        self.terminal = Terminal()
        self.terminal_dock = QDockWidget("Terminal", self)
        self.terminal_dock.setWidget(self.terminal)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminal_dock)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tool bar
        self.create_tool_bar()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("Replace", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.replace)
        edit_menu.addAction(replace_action)
        
        edit_menu.addSeparator()
        
        format_action = QAction("Format Code", self)
        format_action.setShortcut("Ctrl+Shift+F")
        format_action.triggered.connect(self.format_code)
        edit_menu.addAction(format_action)
        
        edit_menu.addSeparator()
        
        # Snippets submenu
        snippets_menu = QMenu("Snippets", self)
        edit_menu.addMenu(snippets_menu)
        
        manage_snippets_action = QAction("Manage Snippets", self)
        manage_snippets_action.triggered.connect(self.manage_snippets)
        snippets_menu.addAction(manage_snippets_action)
        
        insert_snippet_action = QAction("Insert Snippet", self)
        insert_snippet_action.setShortcut("Ctrl+Shift+S")
        insert_snippet_action.triggered.connect(self.insert_snippet)
        snippets_menu.addAction(insert_snippet_action)
        
        # Run menu
        run_menu = menu_bar.addMenu("Run")
        
        run_action = QAction("Run File", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_file)
        run_menu.addAction(run_action)
        
        run_in_terminal_action = QAction("Run in Terminal", self)
        run_in_terminal_action.setShortcut("Ctrl+F5")
        run_in_terminal_action.triggered.connect(self.run_in_terminal)
        run_menu.addAction(run_in_terminal_action)
        
        run_menu.addSeparator()
        
        debug_action = QAction("Debug File", self)
        debug_action.setShortcut("F9")
        debug_action.triggered.connect(self.debug_file)
        run_menu.addAction(debug_action)
        
        # Project menu
        project_menu = menu_bar.addMenu("Project")
        
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self.new_project)
        project_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self.open_project)
        project_menu.addAction(open_project_action)
        
        project_menu.addSeparator()
        
        project_files_action = QAction("Project Files", self)
        project_files_action.triggered.connect(self.manage_project_files)
        project_menu.addAction(project_files_action)
        
        # Git menu
        git_menu = menu_bar.addMenu("Git")
        
        init_action = QAction("Initialize Repository", self)
        init_action.triggered.connect(self.git_init)
        git_menu.addAction(init_action)
        
        open_repo_action = QAction("Open Repository", self)
        open_repo_action.triggered.connect(self.git_open_repo)
        git_menu.addAction(open_repo_action)
        
        git_menu.addSeparator()
        
        git_ops_action = QAction("Git Operations", self)
        git_ops_action.triggered.connect(self.git_operations)
        git_menu.addAction(git_ops_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        toggle_file_browser = QAction("Toggle File Browser", self)
        toggle_file_browser.setCheckable(True)
        toggle_file_browser.setChecked(True)
        toggle_file_browser.triggered.connect(self.toggle_file_browser)
        view_menu.addAction(toggle_file_browser)
        
        toggle_terminal = QAction("Toggle Terminal", self)
        toggle_terminal.setCheckable(True)
        toggle_terminal.setChecked(True)
        toggle_terminal.triggered.connect(self.toggle_terminal)
        view_menu.addAction(toggle_terminal)
        
        # Theme submenu
        theme_menu = QMenu("Theme", self)
        view_menu.addMenu(theme_menu)
        
        light_theme_action = QAction("Light", self)
        light_theme_action.setCheckable(True)
        light_theme_action.setChecked(self.theme_manager.get_theme() == 'light')
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("Dark", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.setChecked(self.theme_manager.get_theme() == 'dark')
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(dark_theme_action)
    
    def create_tool_bar(self):
        """Create tool bar"""
        tool_bar = self.addToolBar("Main Toolbar")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        tool_bar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        tool_bar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        tool_bar.addAction(save_action)
        
        tool_bar.addSeparator()
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        tool_bar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        tool_bar.addAction(redo_action)
    
    def new_file(self):
        """Create a new file"""
        editor = CodeEditor()
        index = self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        self.editors.append(editor)
        self.current_file = None
        self.setWindowTitle("WebE - Untitled")
    
    def open_file(self):
        """Open a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                editor = CodeEditor()
                editor.setPlainText(content)
                index = self.tab_widget.addTab(editor, file_path.split('/')[-1])
                self.tab_widget.setCurrentIndex(index)
                self.editors.append(editor)
                self.current_file = file_path
                self.setWindowTitle(f"WebE - {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                editor = self.tab_widget.currentWidget()
                content = editor.toPlainText()
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", "File saved successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the current file as a new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                editor = self.tab_widget.currentWidget()
                content = editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = file_path
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])
                self.setWindowTitle(f"WebE - {file_path}")
                QMessageBox.information(self, "Success", "File saved successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save file: {str(e)}")
    
    def close_tab(self, index):
        """Close a tab"""
        self.tab_widget.removeTab(index)
        if index < len(self.editors):
            self.editors.pop(index)
    
    def undo(self):
        """Undo last action"""
        editor = self.tab_widget.currentWidget()
        if editor:
            editor.undo()
    
    def redo(self):
        """Redo last action"""
        editor = self.tab_widget.currentWidget()
        if editor:
            editor.redo()
    
    def cut(self):
        """Cut selected text"""
        editor = self.tab_widget.currentWidget()
        if editor:
            editor.cut()
    
    def copy(self):
        """Copy selected text"""
        editor = self.tab_widget.currentWidget()
        if editor:
            editor.copy()
    
    def paste(self):
        """Paste text"""
        editor = self.tab_widget.currentWidget()
        if editor:
            editor.paste()
    
    def find(self):
        """Find text"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
        
        class FindDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Find")
                self.parent = parent
                
                layout = QVBoxLayout()
                
                # Find what
                find_layout = QHBoxLayout()
                find_layout.addWidget(QLabel("Find what:"))
                self.find_input = QLineEdit()
                find_layout.addWidget(self.find_input)
                layout.addLayout(find_layout)
                
                # Options
                options_layout = QHBoxLayout()
                self.case_check = QCheckBox("Match case")
                options_layout.addWidget(self.case_check)
                self.whole_check = QCheckBox("Whole words only")
                options_layout.addWidget(self.whole_check)
                layout.addLayout(options_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                self.find_button = QPushButton("Find Next")
                self.find_button.clicked.connect(self.find_next)
                buttons_layout.addWidget(self.find_button)
                self.cancel_button = QPushButton("Cancel")
                self.cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(self.cancel_button)
                layout.addLayout(buttons_layout)
                
                self.setLayout(layout)
            
            def find_next(self):
                text = self.find_input.text()
                if not text:
                    return
                
                editor = self.parent.tab_widget.currentWidget()
                if not editor:
                    return
                
                flags = 0
                if not self.case_check.isChecked():
                    flags |= Qt.CaseInsensitive
                if self.whole_check.isChecked():
                    flags |= Qt.MatchWholeWord
                
                cursor = editor.textCursor()
                found = cursor.find(text, flags)
                
                if found:
                    editor.setTextCursor(cursor)
                else:
                    # Start from beginning
                    cursor.movePosition(cursor.Start)
                    found = cursor.find(text, flags)
                    if found:
                        editor.setTextCursor(cursor)
                    else:
                        QMessageBox.information(self, "Find", "Text not found")
        
        dialog = FindDialog(self)
        dialog.exec_()
    
    def replace(self):
        """Replace text"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
        
        class ReplaceDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Replace")
                self.parent = parent
                
                layout = QVBoxLayout()
                
                # Find what
                find_layout = QHBoxLayout()
                find_layout.addWidget(QLabel("Find what:"))
                self.find_input = QLineEdit()
                find_layout.addWidget(self.find_input)
                layout.addLayout(find_layout)
                
                # Replace with
                replace_layout = QHBoxLayout()
                replace_layout.addWidget(QLabel("Replace with:"))
                self.replace_input = QLineEdit()
                replace_layout.addWidget(self.replace_input)
                layout.addLayout(replace_layout)
                
                # Options
                options_layout = QHBoxLayout()
                self.case_check = QCheckBox("Match case")
                options_layout.addWidget(self.case_check)
                self.whole_check = QCheckBox("Whole words only")
                options_layout.addWidget(self.whole_check)
                layout.addLayout(options_layout)
                
                # Buttons
                buttons_layout = QHBoxLayout()
                self.find_button = QPushButton("Find Next")
                self.find_button.clicked.connect(self.find_next)
                buttons_layout.addWidget(self.find_button)
                self.replace_button = QPushButton("Replace")
                self.replace_button.clicked.connect(self.replace)
                buttons_layout.addWidget(self.replace_button)
                self.replace_all_button = QPushButton("Replace All")
                self.replace_all_button.clicked.connect(self.replace_all)
                buttons_layout.addWidget(self.replace_all_button)
                self.cancel_button = QPushButton("Cancel")
                self.cancel_button.clicked.connect(self.reject)
                buttons_layout.addWidget(self.cancel_button)
                layout.addLayout(buttons_layout)
                
                self.setLayout(layout)
            
            def find_next(self):
                text = self.find_input.text()
                if not text:
                    return
                
                editor = self.parent.tab_widget.currentWidget()
                if not editor:
                    return
                
                flags = 0
                if not self.case_check.isChecked():
                    flags |= Qt.CaseInsensitive
                if self.whole_check.isChecked():
                    flags |= Qt.MatchWholeWord
                
                cursor = editor.textCursor()
                found = cursor.find(text, flags)
                
                if found:
                    editor.setTextCursor(cursor)
                else:
                    # Start from beginning
                    cursor.movePosition(cursor.Start)
                    found = cursor.find(text, flags)
                    if found:
                        editor.setTextCursor(cursor)
                    else:
                        QMessageBox.information(self, "Find", "Text not found")
            
            def replace(self):
                text = self.find_input.text()
                replacement = self.replace_input.text()
                
                editor = self.parent.tab_widget.currentWidget()
                if not editor:
                    return
                
                cursor = editor.textCursor()
                if cursor.hasSelection():
                    cursor.insertText(replacement)
                    editor.setTextCursor(cursor)
                    self.find_next()
            
            def replace_all(self):
                text = self.find_input.text()
                replacement = self.replace_input.text()
                
                editor = self.parent.tab_widget.currentWidget()
                if not editor:
                    return
                
                content = editor.toPlainText()
                flags = 0
                if not self.case_check.isChecked():
                    import re
                    new_content = re.sub(re.escape(text), replacement, content, flags=re.IGNORECASE)
                else:
                    new_content = content.replace(text, replacement)
                
                editor.setPlainText(new_content)
                QMessageBox.information(self, "Replace", "All occurrences replaced")
        
        dialog = ReplaceDialog(self)
        dialog.exec_()
    
    def toggle_file_browser(self, checked):
        """Toggle file browser visibility"""
        if checked:
            self.file_dock.show()
        else:
            self.file_dock.hide()
    
    def toggle_terminal(self, checked):
        """Toggle terminal visibility"""
        if checked:
            self.terminal_dock.show()
        else:
            self.terminal_dock.hide()
    
    def on_file_double_clicked(self, index):
        """Handle file double click event"""
        model = self.file_browser.model
        if not model.isDir(index):
            file_path = model.filePath(index)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                editor = CodeEditor()
                editor.setPlainText(content)
                index = self.tab_widget.addTab(editor, file_path.split('\\')[-1])
                self.tab_widget.setCurrentIndex(index)
                self.editors.append(editor)
                self.current_file = file_path
                self.setWindowTitle(f"WebE - {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")
    
    def run_file(self):
        """Run current Python file"""
        if not self.current_file:
            QMessageBox.warning(self, "Error", "No file open to run")
            return
        
        # Check if file is a Python file
        if not self.current_file.endswith('.py'):
            QMessageBox.warning(self, "Error", "Only Python files can be run")
            return
        
        # Save file first
        self.save_file()
        
        # Run file in a new process
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        from PyQt5.QtCore import QProcess
        
        class RunDialog(QDialog):
            def __init__(self, parent=None, file_path=None):
                super().__init__(parent)
                self.setWindowTitle(f"Running: {file_path}")
                self.setGeometry(200, 200, 600, 400)
                
                layout = QVBoxLayout()
                
                self.output_area = QTextEdit()
                self.output_area.setReadOnly(True)
                layout.addWidget(self.output_area)
                
                self.close_button = QPushButton("Close")
                self.close_button.clicked.connect(self.reject)
                layout.addWidget(self.close_button)
                
                self.setLayout(layout)
                
                # Run process
                self.process = QProcess(self)
                self.process.setProcessChannelMode(QProcess.MergedChannels)
                self.process.readyRead.connect(self.read_output)
                self.process.finished.connect(self.process_finished)
                
                # Start Python process
                self.process.start('python', [file_path])
            
            def read_output(self):
                """Read output from process"""
                output = self.process.readAll().data().decode('utf-8', errors='replace')
                self.output_area.append(output)
            
            def process_finished(self, exit_code, exit_status):
                """Handle process finished"""
                self.output_area.append(f"\nProcess finished with exit code {exit_code}")
        
        dialog = RunDialog(self, self.current_file)
        dialog.exec_()
    
    def run_in_terminal(self):
        """Run current Python file in terminal"""
        if not self.current_file:
            QMessageBox.warning(self, "Error", "No file open to run")
            return
        
        # Check if file is a Python file
        if not self.current_file.endswith('.py'):
            QMessageBox.warning(self, "Error", "Only Python files can be run")
            return
        
        # Save file first
        self.save_file()
        
        # Run in terminal
        command = f'python "{self.current_file}"'
        self.terminal.input_line.setText(command)
        self.terminal.execute_command()
        
        # Show terminal if hidden
        if not self.terminal_dock.isVisible():
            self.terminal_dock.show()
    
    def set_theme(self, theme):
        """Set application theme"""
        self.theme_manager.set_theme(theme)
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        self.theme_manager.apply_theme(app, self)
    
    def new_project(self):
        """Create new project"""
        project = self.project_manager.create_project(self)
        if project:
            QMessageBox.information(self, "Success", f"Project '{project['name']}' created successfully")
            # Update window title
            self.setWindowTitle(f"WebE - {project['name']}")
    
    def open_project(self):
        """Open existing project"""
        project = self.project_manager.open_project(self)
        if project:
            QMessageBox.information(self, "Success", f"Project '{project['name']}' opened successfully")
            # Update window title
            self.setWindowTitle(f"WebE - {project['name']}")
    
    def manage_project_files(self):
        """Manage project files"""
        project = self.project_manager.get_current_project()
        if project:
            dialog = ProjectFilesDialog(project, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No project open")
    
    def debug_file(self):
        """Debug current Python file"""
        if not self.current_file:
            QMessageBox.warning(self, "Error", "No file open to debug")
            return
        
        # Check if file is a Python file
        if not self.current_file.endswith('.py'):
            QMessageBox.warning(self, "Error", "Only Python files can be debugged")
            return
        
        # Save file first
        self.save_file()
        
        # Start debugger
        dialog = DebuggerDialog(self.current_file, self)
        dialog.start_debugging()
        dialog.exec_()
    
    def format_code(self):
        """Format current Python file"""
        editor = self.tab_widget.currentWidget()
        if not editor:
            return
        
        # Get current code
        code = editor.toPlainText()
        if not code:
            return
        
        try:
            # Use ast and pprint to format code
            import ast
            import pprint
            
            # Parse code
            tree = ast.parse(code)
            
            # Convert back to string with proper formatting
            formatted_code = ast.unparse(tree)
            
            # Set formatted code back to editor
            editor.setPlainText(formatted_code)
            QMessageBox.information(self, "Success", "Code formatted successfully")
        except SyntaxError as e:
            QMessageBox.warning(self, "Error", f"Syntax error in code: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to format code: {str(e)}")
    
    def git_init(self):
        """Initialize Git repository"""
        dialog = GitInitDialog(self)
        if dialog.exec_() == dialog.Accepted:
            repo_path = dialog.get_repo_path()
            if repo_path:
                code, output = self.git_manager.init_repo(repo_path)
                if code == 0:
                    self.git_manager.set_current_repo(repo_path)
                    QMessageBox.information(self, "Success", f"Repository initialized at {repo_path}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to initialize repository: {output}")
    
    def git_open_repo(self):
        """Open Git repository"""
        from PyQt5.QtWidgets import QFileDialog
        repo_path = QFileDialog.getExistingDirectory(self, "Open Git Repository")
        if repo_path:
            # Check if it's a Git repository
            code, output = self.git_manager.git_status(repo_path)
            if code == 0:
                self.git_manager.set_current_repo(repo_path)
                QMessageBox.information(self, "Success", f"Repository opened at {repo_path}")
            else:
                QMessageBox.warning(self, "Error", f"Not a Git repository: {output}")
    
    def git_operations(self):
        """Open Git operations dialog"""
        if self.git_manager.get_current_repo():
            dialog = GitDialog(self.git_manager, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No Git repository open")
    
    def manage_snippets(self):
        """Manage code snippets"""
        dialog = SnippetDialog(self.snippet_manager, self)
        dialog.exec_()
    
    def insert_snippet(self):
        """Insert code snippet"""
        editor = self.tab_widget.currentWidget()
        if not editor:
            return
        
        # Get all snippets
        snippets = self.snippet_manager.get_snippets()
        if not snippets:
            QMessageBox.warning(self, "Error", "No snippets available")
            return
        
        # Create snippet names list
        snippet_names = [snippet['name'] for snippet in snippets]
        
        # Show snippet selection dialog
        from PyQt5.QtWidgets import QInputDialog
        snippet_name, ok = QInputDialog.getItem(self, "Insert Snippet", "Select snippet:", snippet_names, 0, False)
        
        if ok and snippet_name:
            # Find the selected snippet
            for snippet in snippets:
                if snippet['name'] == snippet_name:
                    # Insert snippet into editor
                    editor.insertPlainText(snippet['body'])
                    break
