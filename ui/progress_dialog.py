"""
Progress Dialog for PDF Export Operations
Provides professional progress feedback during lengthy operations
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QIcon
from typing import Optional, Callable


class ProgressDialog(QDialog):
    """Professional progress dialog with detailed feedback"""
    
    # Signals for communication
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None, title="Processing PDF", show_details=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 300)
        self.resize(600, 400)
        
        # Progress tracking
        self.current_step = 0
        self.total_steps = 0
        self.show_details = show_details
        self.is_cancelled = False
        
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Status icon (could add icons later)
        self.status_label = QLabel("🔄")
        self.status_label.setFont(QFont("Arial", 24))
        header_layout.addWidget(self.status_label)
        
        # Main status text
        status_layout = QVBoxLayout()
        self.main_status = QLabel("Preparing PDF accessibility processing...")
        self.main_status.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.main_status.setWordWrap(True)
        
        self.sub_status = QLabel("Initializing components...")
        self.sub_status.setFont(QFont("Arial", 10))
        self.sub_status.setStyleSheet("color: #666;")
        
        status_layout.addWidget(self.main_status)
        status_layout.addWidget(self.sub_status)
        header_layout.addLayout(status_layout)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Progress bars
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("Overall Progress: %p%")
        layout.addWidget(QLabel("Overall Progress:"))
        layout.addWidget(self.overall_progress)
        
        self.step_progress = QProgressBar()
        self.step_progress.setMinimum(0)
        self.step_progress.setMaximum(100)
        self.step_progress.setValue(0)
        self.step_progress.setTextVisible(True)
        self.step_progress.setFormat("Current Step: %p%")
        layout.addWidget(QLabel("Current Step:"))
        layout.addWidget(self.step_progress)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Details section (expandable)
        if self.show_details:
            details_label = QLabel("Processing Details:")
            details_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            layout.addWidget(details_label)
            
            self.details_text = QTextEdit()
            self.details_text.setMaximumHeight(150)
            self.details_text.setReadOnly(True)
            self.details_text.setFont(QFont("Courier", 9))
            self.details_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 8px;
                }
            """)
            layout.addWidget(self.details_text)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.clicked.connect(self.cancel_operation)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.setMinimumWidth(100)
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def setup_styling(self):
        """Apply professional styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #333;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                color: #6c757d;
            }
        """)
    
    def set_total_steps(self, total: int):
        """Set the total number of processing steps"""
        self.total_steps = total
        self.current_step = 0
        self.overall_progress.setMaximum(total)
        self.overall_progress.setValue(0)
        
    def update_step(self, step_name: str, step_description: str = "", step_progress: int = 0):
        """Update the current processing step"""
        self.current_step += 1
        
        # Update main status
        self.main_status.setText(f"Step {self.current_step}/{self.total_steps}: {step_name}")
        self.sub_status.setText(step_description)
        
        # Update progress bars
        self.overall_progress.setValue(self.current_step)
        self.step_progress.setValue(step_progress)
        
        # Update details if available
        if self.show_details and hasattr(self, 'details_text'):
            timestamp = QTimer()
            self.details_text.append(f"[Step {self.current_step}] {step_name}")
            if step_description:
                self.details_text.append(f"  → {step_description}")
            self.details_text.append("")  # Blank line for readability
            
            # Auto-scroll to bottom
            cursor = self.details_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.details_text.setTextCursor(cursor)
        
        # Process events to update UI
        self.repaint()
        
    def update_step_progress(self, progress: int, detail: str = ""):
        """Update progress within the current step"""
        self.step_progress.setValue(progress)
        if detail:
            self.sub_status.setText(detail)
            
        # Add detail to log if available
        if self.show_details and hasattr(self, 'details_text') and detail:
            self.details_text.append(f"    {detail}")
            
            # Auto-scroll to bottom
            cursor = self.details_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.details_text.setTextCursor(cursor)
        
        self.repaint()
        
    def complete_step(self, success: bool = True, message: str = ""):
        """Mark current step as complete"""
        self.step_progress.setValue(100)
        
        if success:
            self.status_label.setText("✅")
            if not message:
                message = "Step completed successfully"
        else:
            self.status_label.setText("❌")
            if not message:
                message = "Step failed"
                
        self.sub_status.setText(message)
        
        if self.show_details and hasattr(self, 'details_text'):
            status_icon = "✅" if success else "❌"
            self.details_text.append(f"    {status_icon} {message}")
            self.details_text.append("")
            
        self.repaint()
        
    def finish_processing(self, success: bool = True, final_message: str = ""):
        """Complete the entire processing operation"""
        if success:
            self.status_label.setText("🎉")
            self.main_status.setText("Processing Complete!")
            if not final_message:
                final_message = "PDF accessibility processing completed successfully"
        else:
            self.status_label.setText("❌")
            self.main_status.setText("Processing Failed")
            if not final_message:
                final_message = "PDF accessibility processing encountered errors"
                
        self.sub_status.setText(final_message)
        self.overall_progress.setValue(self.total_steps)
        self.step_progress.setValue(100)
        
        # Enable close button, disable cancel
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.close_button.setDefault(True)
        
        if self.show_details and hasattr(self, 'details_text'):
            self.details_text.append("=" * 50)
            status_icon = "🎉" if success else "❌"
            self.details_text.append(f"{status_icon} {final_message}")
            
        self.repaint()
        
    def cancel_operation(self):
        """Handle cancel request"""
        self.is_cancelled = True
        self.cancel_requested.emit()
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")
        
        self.status_label.setText("⏹️")
        self.main_status.setText("Cancelling operation...")
        self.sub_status.setText("Please wait while we safely stop the process...")
        
    def add_log_message(self, message: str, level: str = "INFO"):
        """Add a message to the details log"""
        if self.show_details and hasattr(self, 'details_text'):
            level_icons = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍"
            }
            icon = level_icons.get(level, "📝")
            self.details_text.append(f"    {icon} {message}")
            
            # Auto-scroll to bottom
            cursor = self.details_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.details_text.setTextCursor(cursor)
            
        self.repaint()
