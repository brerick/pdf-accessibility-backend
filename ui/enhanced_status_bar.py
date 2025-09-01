"""
Enhanced Status Bar for PDF Accessibility Tool
Provides professional status updates and tool tips
"""
from PyQt6.QtWidgets import (QStatusBar, QLabel, QProgressBar, QPushButton, 
                             QHBoxLayout, QWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from typing import Optional


class EnhancedStatusBar(QStatusBar):
    """Professional status bar with multiple sections"""
    
    # Signals
    help_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Status tracking
        self.current_operation = None
        self.progress_timer = QTimer()
        self.message_timer = QTimer()
        
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Setup status bar components"""
        
        # Main status message (left side)
        self.status_label = QLabel("Ready")
        self.status_label.setMinimumWidth(200)
        self.addWidget(self.status_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        self.addWidget(separator1)
        
        # Document info section
        self.doc_info_label = QLabel("No document loaded")
        self.doc_info_label.setMinimumWidth(150)
        self.addWidget(self.doc_info_label)
        
        # Progress section (hidden by default)
        self.progress_widget = QWidget()
        progress_layout = QHBoxLayout(self.progress_widget)
        progress_layout.setContentsMargins(5, 2, 5, 2)
        
        self.progress_label = QLabel("Processing...")
        self.progress_label.setFont(QFont("Arial", 9))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setTextVisible(False)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        self.addWidget(self.progress_widget)
        self.progress_widget.hide()
        
        # Right side permanent widgets
        self.addPermanentWidget(QFrame())  # Spacer
        
        # Accessibility status
        self.accessibility_status = QLabel("🔍 Not Validated")
        self.accessibility_status.setToolTip("Document accessibility status")
        self.addPermanentWidget(self.accessibility_status)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        self.addPermanentWidget(separator2)
        
        # Help button
        help_btn = QPushButton("❓")
        help_btn.setToolTip("Help and Documentation")
        help_btn.setMaximumSize(24, 20)
        help_btn.clicked.connect(self.help_requested.emit)
        self.addPermanentWidget(help_btn)
        
    def setup_styling(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                color: #495057;
                font-size: 11px;
            }
            QStatusBar::item {
                border: none;
            }
            QLabel {
                color: #495057;
                padding: 2px 5px;
            }
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 2px;
            }
        """)
        
    def show_message(self, message: str, timeout: int = 5000):
        """Show a temporary message"""
        self.status_label.setText(message)
        if timeout > 0:
            self.message_timer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
            
    def show_permanent_message(self, message: str):
        """Show a permanent status message"""
        self.status_label.setText(message)
        
    def update_document_info(self, filename: Optional[str] = None, pages: Optional[int] = None, 
                           elements: Optional[int] = None):
        """Update document information display"""
        if filename:
            info_parts = [filename]
            if pages is not None:
                info_parts.append(f"{pages} pages")
            if elements is not None:
                info_parts.append(f"{elements} elements")
            
            self.doc_info_label.setText(" | ".join(info_parts))
        else:
            self.doc_info_label.setText("No document loaded")
            
    def update_accessibility_status(self, status: str, level: str = "unknown"):
        """Update accessibility validation status"""
        status_icons = {
            "unknown": "🔍",
            "validating": "⏳", 
            "passed": "✅",
            "warning": "⚠️",
            "failed": "❌",
            "improved": "🎯"
        }
        
        icon = status_icons.get(level, "🔍")
        self.accessibility_status.setText(f"{icon} {status}")
        
        # Update tooltip
        tooltips = {
            "unknown": "Accessibility status not checked",
            "validating": "Checking document accessibility...",
            "passed": "Document meets accessibility standards",
            "warning": "Document has accessibility warnings", 
            "failed": "Document has accessibility issues",
            "improved": "Document accessibility has been enhanced"
        }
        self.accessibility_status.setToolTip(tooltips.get(level, status))
        
    def start_progress(self, operation: str):
        """Start showing progress for an operation"""
        self.current_operation = operation
        self.progress_label.setText(f"{operation}...")
        self.progress_bar.setValue(0)
        self.progress_widget.show()
        
    def update_progress(self, value: int, detail: str = ""):
        """Update progress bar and detail text"""
        self.progress_bar.setValue(value)
        if detail and self.current_operation:
            self.progress_label.setText(f"{self.current_operation}: {detail}")
        elif self.current_operation:
            self.progress_label.setText(f"{self.current_operation}...")
            
    def finish_progress(self, success: bool = True, message: str = ""):
        """Complete the progress operation"""
        if success:
            self.progress_bar.setValue(100)
            if message:
                self.show_message(f"✅ {message}", 3000)
            else:
                self.show_message(f"✅ {self.current_operation} completed", 3000)
        else:
            if message:
                self.show_message(f"❌ {message}", 5000)
            else:
                self.show_message(f"❌ {self.current_operation} failed", 5000)
                
        # Hide progress after a short delay
        QTimer.singleShot(1000, self.progress_widget.hide)
        self.current_operation = None
        
    def show_tip(self, tip: str):
        """Show a helpful tip in the status bar"""
        self.show_message(f"💡 Tip: {tip}", 8000)
        
    def show_shortcut_hint(self, action: str, shortcut: str):
        """Show keyboard shortcut hint"""
        self.show_message(f"🔧 {action} ({shortcut})", 4000)
