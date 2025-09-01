"""
Professional Success and Error Dialogs
Enhanced user feedback for PDF accessibility operations
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import os


class SuccessDialog(QDialog):
    """Professional success dialog with detailed information"""
    
    def __init__(self, parent=None, title="Operation Successful", 
                 main_message="Operation completed successfully",
                 details=None, file_path=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 300)
        self.resize(600, 400)
        
        self.main_message = main_message
        self.details = details or []
        self.file_path = file_path
        
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Success header
        header_layout = QHBoxLayout()
        
        # Success icon
        success_icon = QLabel("🎉")
        success_icon.setFont(QFont("Arial", 48))
        success_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(success_icon)
        
        # Success message
        message_layout = QVBoxLayout()
        
        self.title_label = QLabel("Success!")
        self.title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #28a745;")
        
        self.message_label = QLabel(self.main_message)
        self.message_label.setFont(QFont("Arial", 12))
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #333; margin-top: 10px;")
        
        message_layout.addWidget(self.title_label)
        message_layout.addWidget(self.message_label)
        message_layout.addStretch()
        
        header_layout.addLayout(message_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # File information if provided
        if self.file_path:
            file_frame = QFrame()
            file_frame.setFrameStyle(QFrame.Shape.Box)
            file_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            file_layout = QVBoxLayout(file_frame)
            
            file_label = QLabel("📁 Output File:")
            file_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            file_layout.addWidget(file_label)
            
            file_path_label = QLabel(os.path.basename(self.file_path))
            file_path_label.setFont(QFont("Arial", 11))
            file_path_label.setStyleSheet("color: #007bff; margin-left: 20px;")
            file_layout.addWidget(file_path_label)
            
            file_dir_label = QLabel(f"Location: {os.path.dirname(self.file_path)}")
            file_dir_label.setFont(QFont("Arial", 9))
            file_dir_label.setStyleSheet("color: #666; margin-left: 20px;")
            file_layout.addWidget(file_dir_label)
            
            layout.addWidget(file_frame)
        
        # Details section if provided
        if self.details:
            details_label = QLabel("📋 Processing Summary:")
            details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            layout.addWidget(details_label)
            
            details_scroll = QScrollArea()
            details_scroll.setMaximumHeight(120)
            details_scroll.setWidgetResizable(True)
            details_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            details_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            details_content = QLabel("\\n".join(self.details))
            details_content.setFont(QFont("Arial", 9))
            details_content.setWordWrap(True)
            details_content.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 10px;
                    color: #495057;
                }
            """)
            
            details_scroll.setWidget(details_content)
            layout.addWidget(details_scroll)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        if self.file_path:
            open_folder_btn = QPushButton("📁 Open Folder")
            open_folder_btn.clicked.connect(self.open_folder)
            button_layout.addWidget(open_folder_btn)
            
            open_file_btn = QPushButton("📄 Open File")
            open_file_btn.clicked.connect(self.open_file)
            button_layout.addWidget(open_file_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumWidth(100)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
    def setup_styling(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton[text="📁 Open Folder"], QPushButton[text="📄 Open File"] {
                background-color: #28a745;
            }
            QPushButton[text="📁 Open Folder"]:hover, QPushButton[text="📄 Open File"]:hover {
                background-color: #218838;
            }
        """)
    
    def open_folder(self):
        """Open the folder containing the file"""
        if self.file_path:
            folder_path = os.path.dirname(self.file_path)
            os.system(f'open "{folder_path}"')  # macOS
            # For Windows: os.system(f'explorer "{folder_path}"')
            # For Linux: os.system(f'xdg-open "{folder_path}"')
    
    def open_file(self):
        """Open the file"""
        if self.file_path:
            os.system(f'open "{self.file_path}"')  # macOS
            # For Windows: os.system(f'start "" "{self.file_path}"')
            # For Linux: os.system(f'xdg-open "{self.file_path}"')


class ErrorDialog(QDialog):
    """Professional error dialog with detailed error information"""
    
    def __init__(self, parent=None, title="Operation Failed", 
                 main_message="An error occurred",
                 error_details=None, suggestions=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 350)
        self.resize(600, 450)
        
        self.main_message = main_message
        self.error_details = error_details or []
        self.suggestions = suggestions or []
        
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Error header
        header_layout = QHBoxLayout()
        
        # Error icon
        error_icon = QLabel("❌")
        error_icon.setFont(QFont("Arial", 48))
        error_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(error_icon)
        
        # Error message
        message_layout = QVBoxLayout()
        
        self.title_label = QLabel("Operation Failed")
        self.title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #dc3545;")
        
        self.message_label = QLabel(self.main_message)
        self.message_label.setFont(QFont("Arial", 12))
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: #333; margin-top: 10px;")
        
        message_layout.addWidget(self.title_label)
        message_layout.addWidget(self.message_label)
        message_layout.addStretch()
        
        header_layout.addLayout(message_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Error details if provided
        if self.error_details:
            details_label = QLabel("🔍 Error Details:")
            details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            layout.addWidget(details_label)
            
            details_text = QTextEdit()
            details_text.setMaximumHeight(100)
            details_text.setReadOnly(True)
            details_text.setFont(QFont("Courier", 9))
            details_text.setPlainText("\\n".join(self.error_details))
            details_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    padding: 8px;
                    color: #721c24;
                }
            """)
            layout.addWidget(details_text)
        
        # Suggestions if provided
        if self.suggestions:
            suggestions_label = QLabel("💡 Suggestions:")
            suggestions_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            layout.addWidget(suggestions_label)
            
            suggestions_content = QLabel("\\n".join([f"• {s}" for s in self.suggestions]))
            suggestions_content.setFont(QFont("Arial", 9))
            suggestions_content.setWordWrap(True)
            suggestions_content.setStyleSheet("""
                QLabel {
                    background-color: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 4px;
                    padding: 10px;
                    color: #0c5460;
                }
            """)
            layout.addWidget(suggestions_content)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        retry_btn = QPushButton("🔄 Retry")
        retry_btn.clicked.connect(lambda: self.done(2))  # Custom return code for retry
        button_layout.addWidget(retry_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumWidth(100)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
    def setup_styling(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
            QPushButton:pressed {
                background-color: #3d4043;
            }
            QPushButton[text="🔄 Retry"] {
                background-color: #007bff;
            }
            QPushButton[text="🔄 Retry"]:hover {
                background-color: #0056b3;
            }
        """)
