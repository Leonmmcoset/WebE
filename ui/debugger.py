#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debugger for WebE IDE
Supports breakpoints, step execution, and variable inspection
"""

import sys
import pdb
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor


class DebuggerThread(QThread):
    """Debugger thread"""
    
    output_signal = pyqtSignal(str)
    breakpoint_signal = pyqtSignal(str, int)
    variables_signal = pyqtSignal(dict)
    stack_signal = pyqtSignal(list)
    finished_signal = pyqtSignal(int)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.debugger = None
        self.breakpoints = {}
        self.should_continue = False
        self.should_step = False
        self.should_step_in = False
        self.should_step_out = False
    
    def run(self):
        """Run debugger"""
        try:
            # Create custom debugger
            self.debugger = CustomDebugger(self)
            
            # Set breakpoints
            for file_path, lines in self.breakpoints.items():
                for line in lines:
                    self.debugger.set_break(file_path, line)
            
            # Run the script
            sys.argv = [self.file_path]
            self.debugger.run(self.file_path)
        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")
        finally:
            self.finished_signal.emit(0)
    
    def set_breakpoint(self, file_path, line):
        """Set breakpoint"""
        if file_path not in self.breakpoints:
            self.breakpoints[file_path] = []
        if line not in self.breakpoints[file_path]:
            self.breakpoints[file_path].append(line)
    
    def remove_breakpoint(self, file_path, line):
        """Remove breakpoint"""
        if file_path in self.breakpoints and line in self.breakpoints[file_path]:
            self.breakpoints[file_path].remove(line)
    
    def continue_execution(self):
        """Continue execution"""
        self.should_continue = True
    
    def step(self):
        """Step over"""
        self.should_step = True
    
    def step_in(self):
        """Step in"""
        self.should_step_in = True
    
    def step_out(self):
        """Step out"""
        self.should_step_out = True


class CustomDebugger(pdb.Pdb):
    """Custom debugger that integrates with WebE IDE"""
    
    def __init__(self, debugger_thread):
        super().__init__(stdin=self, stdout=self)
        self.debugger_thread = debugger_thread
        self.output_buffer = []
    
    def write(self, text):
        """Write output"""
        self.output_buffer.append(text)
        if text.endswith('\n'):
            output = ''.join(self.output_buffer)
            self.debugger_thread.output_signal.emit(output)
            self.output_buffer = []
    
    def readline(self):
        """Read input"""
        # Wait for user command
        while True:
            if self.debugger_thread.should_continue:
                self.debugger_thread.should_continue = False
                return 'c'
            elif self.debugger_thread.should_step:
                self.debugger_thread.should_step = False
                return 'n'
            elif self.debugger_thread.should_step_in:
                self.debugger_thread.should_step_in = False
                return 's'
            elif self.debugger_thread.should_step_out:
                self.debugger_thread.should_step_out = False
                return 'r'
            self.msleep(100)
    
    def user_line(self, frame):
        """Called when reaching a user line"""
        super().user_line(frame)
        file_path = frame.f_code.co_filename
        line_no = frame.f_lineno
        self.debugger_thread.breakpoint_signal.emit(file_path, line_no)
        
        # Get variables
        variables = {}
        variables['Locals'] = frame.f_locals
        variables['Globals'] = frame.f_globals
        self.debugger_thread.variables_signal.emit(variables)
        
        # Get stack
        stack = []
        current_frame = frame
        while current_frame:
            stack.append((
                current_frame.f_code.co_filename,
                current_frame.f_lineno,
                current_frame.f_code.co_name
            ))
            current_frame = current_frame.f_back
        self.debugger_thread.stack_signal.emit(stack)


class DebuggerDialog(QDialog):
    """Debugger dialog"""
    
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(f"Debug - {file_path}")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()
        self.debugger_thread = None
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Top splitter (output and variables)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Output area
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        output_layout.addWidget(self.output_area)
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        top_splitter.addWidget(output_widget)
        
        # Variables and stack
        right_layout = QVBoxLayout()
        
        # Variables
        variables_layout = QVBoxLayout()
        variables_layout.addWidget(QLabel("Variables:"))
        self.variables_tree = QTreeWidget()
        self.variables_tree.setHeaderLabels(["Name", "Value"])
        variables_layout.addWidget(self.variables_tree)
        right_layout.addLayout(variables_layout)
        
        # Stack
        stack_layout = QVBoxLayout()
        stack_layout.addWidget(QLabel("Stack:"))
        self.stack_list = QListWidget()
        stack_layout.addWidget(self.stack_list)
        right_layout.addLayout(stack_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        top_splitter.addWidget(right_widget)
        
        top_splitter.setSizes([400, 400])
        layout.addWidget(top_splitter)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_execution)
        buttons_layout.addWidget(self.continue_button)
        
        self.step_button = QPushButton("Step Over")
        self.step_button.clicked.connect(self.step)
        buttons_layout.addWidget(self.step_button)
        
        self.step_in_button = QPushButton("Step In")
        self.step_in_button.clicked.connect(self.step_in)
        buttons_layout.addWidget(self.step_in_button)
        
        self.step_out_button = QPushButton("Step Out")
        self.step_out_button.clicked.connect(self.step_out)
        buttons_layout.addWidget(self.step_out_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        buttons_layout.addWidget(self.stop_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def start_debugging(self):
        """Start debugging"""
        # Create and start debugger thread
        self.debugger_thread = DebuggerThread(self.file_path)
        
        # Connect signals
        self.debugger_thread.output_signal.connect(self.append_output)
        self.debugger_thread.breakpoint_signal.connect(self.on_breakpoint)
        self.debugger_thread.variables_signal.connect(self.update_variables)
        self.debugger_thread.stack_signal.connect(self.update_stack)
        self.debugger_thread.finished_signal.connect(self.on_finished)
        
        # Start thread
        self.debugger_thread.start()
    
    def append_output(self, text):
        """Append output to output area"""
        self.output_area.append(text)
        cursor = self.output_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_area.setTextCursor(cursor)
    
    def on_breakpoint(self, file_path, line):
        """Handle breakpoint hit"""
        self.append_output(f"Breakpoint hit at {file_path}:{line}")
    
    def update_variables(self, variables):
        """Update variables tree"""
        self.variables_tree.clear()
        
        for scope, vars_dict in variables.items():
            scope_item = QTreeWidgetItem([scope])
            self.variables_tree.addTopLevelItem(scope_item)
            
            for name, value in vars_dict.items():
                # Skip private variables
                if name.startswith('_'):
                    continue
                
                try:
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + '...'
                except:
                    value_str = '[Error displaying value]'
                
                var_item = QTreeWidgetItem([name, value_str])
                scope_item.addChild(var_item)
        
        self.variables_tree.expandAll()
    
    def update_stack(self, stack):
        """Update stack list"""
        self.stack_list.clear()
        
        for i, (file_path, line, func_name) in enumerate(stack):
            item = QListWidgetItem(f"[{i}] {func_name} at {file_path}:{line}")
            if i == 0:
                item.setBackground(QColor(240, 240, 240))
            self.stack_list.addItem(item)
    
    def continue_execution(self):
        """Continue execution"""
        if self.debugger_thread:
            self.debugger_thread.continue_execution()
    
    def step(self):
        """Step over"""
        if self.debugger_thread:
            self.debugger_thread.step()
    
    def step_in(self):
        """Step in"""
        if self.debugger_thread:
            self.debugger_thread.step_in()
    
    def step_out(self):
        """Step out"""
        if self.debugger_thread:
            self.debugger_thread.step_out()
    
    def stop(self):
        """Stop debugging"""
        if self.debugger_thread:
            self.debugger_thread.terminate()
        self.reject()
    
    def on_finished(self, exit_code):
        """Handle debugger finished"""
        self.append_output(f"Debugging finished with exit code {exit_code}")
        self.continue_button.setEnabled(False)
        self.step_button.setEnabled(False)
        self.step_in_button.setEnabled(False)
        self.step_out_button.setEnabled(False)
