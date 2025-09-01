"""
Validation Panel
Shows veraPDF validation results and allows navigation to issues
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QPushButton, QLabel, QProgressBar,
                             QGroupBox, QTextEdit, QSplitter, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QIcon, QColor, QFont
from typing import List, Dict, Any, Optional

from core.verapdf_validator import VeraPDFValidator, ValidationIssue


class ValidationWorker(QThread):
    """Worker thread for running veraPDF validation"""
    validation_complete = pyqtSignal(list)
    validation_error = pyqtSignal(str)
    
    def __init__(self, pdf_path: str, profile: str = "ua1"):
        super().__init__()
        self.pdf_path = pdf_path
        self.profile = profile
        self.validator = VeraPDFValidator()
    
    def run(self):
        """Run validation in background thread"""
        try:
            issues = self.validator.validate_pdf(self.pdf_path, self.profile)
            self.validation_complete.emit(issues)
        except Exception as e:
            self.validation_error.emit(str(e))


class ValidationPanel(QWidget):
    """Panel for displaying PDF validation results"""
    issue_selected = pyqtSignal(dict)
    jump_to_page = pyqtSignal(int)
    validation_completed = pyqtSignal(list)  # New signal to emit validation results
    
    def __init__(self):
        super().__init__()
        self.validator = VeraPDFValidator()
        self.current_issues = []
        self.validation_worker = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup validation panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("PDF/UA Validation")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)
        
        # Validation controls
        controls_group = QGroupBox("Validation Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Profile selection
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profile:"))
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems([
            "ua1 - PDF/UA-1",
            "ua2 - PDF/UA-2", 
            "1a - PDF/A-1a",
            "1b - PDF/A-1b",
            "2a - PDF/A-2a",
            "2b - PDF/A-2b",
            "3a - PDF/A-3a",
            "3b - PDF/A-3b"
        ])
        profile_layout.addWidget(self.profile_combo)
        profile_layout.addStretch()
        
        controls_layout.addLayout(profile_layout)
        
        # Validation button and progress
        button_layout = QHBoxLayout()
        
        self.validate_button = QPushButton("Run Validation")
        self.validate_button.clicked.connect(self.start_validation)
        button_layout.addWidget(self.validate_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)
        
        controls_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("No validation performed")
        self.status_label.setStyleSheet("color: gray;")
        controls_layout.addWidget(self.status_label)
        
        layout.addWidget(controls_group)
        
        # Results splitter
        results_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Issues tree
        issues_group = QGroupBox("Validation Issues")
        issues_layout = QVBoxLayout(issues_group)
        
        self.issues_tree = QTreeWidget()
        self.issues_tree.setHeaderLabels(["Issue", "Severity", "Rule ID"])
        self.issues_tree.itemClicked.connect(self.on_issue_selected)
        self.issues_tree.itemDoubleClicked.connect(self.on_issue_double_clicked)
        issues_layout.addWidget(self.issues_tree)
        
        # Issue counts
        self.counts_label = QLabel("Issues: 0 Errors, 0 Warnings")
        issues_layout.addWidget(self.counts_label)
        
        results_splitter.addWidget(issues_group)
        
        # Issue details
        details_group = QGroupBox("Issue Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumHeight(120)  # Set minimum instead of maximum for better flexibility
        details_layout.addWidget(self.details_text)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.jump_button = QPushButton("Jump to Issue")
        self.jump_button.clicked.connect(self.jump_to_issue)
        self.jump_button.setEnabled(False)
        action_layout.addWidget(self.jump_button)
        
        self.fix_button = QPushButton("Suggest Fix")
        self.fix_button.clicked.connect(self.show_fix_suggestion)
        self.fix_button.setEnabled(False)
        action_layout.addWidget(self.fix_button)
        
        action_layout.addStretch()
        details_layout.addLayout(action_layout)
        
        results_splitter.addWidget(details_group)
        results_splitter.setSizes([400, 180])  # Increased from [300, 150] - more space for issues tree
        
        layout.addWidget(results_splitter)
        
        # Initially disable if veraPDF not available
        if not self.validator.is_available:
            self.show_installation_info()
        
    def show_installation_info(self):
        """Show veraPDF installation information"""
        info = self.validator.get_installation_info()
        self.status_label.setText("veraPDF not found - Click to install")
        self.status_label.setStyleSheet("color: red;")
        self.validate_button.setText("Install veraPDF")
        self.validate_button.clicked.disconnect()
        self.validate_button.clicked.connect(self.show_install_instructions)
        
    def show_install_instructions(self):
        """Show veraPDF installation instructions"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Install veraPDF")
        msg.setText("veraPDF is required for PDF validation.")
        msg.setInformativeText(
            "Please download and install veraPDF from:\n"
            "https://verapdf.org/home/\n\n"
            "After installation, restart the application."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
    def set_pdf_path(self, pdf_path: str):
        """Set the PDF file to validate"""
        self.pdf_path = pdf_path
        self.validate_button.setEnabled(self.validator.is_available)
        
    def start_validation(self):
        """Start PDF validation in background thread"""
        if not hasattr(self, 'pdf_path') or not self.pdf_path:
            self.status_label.setText("No PDF loaded")
            return
            
        # Get selected profile
        profile_text = self.profile_combo.currentText()
        profile = profile_text.split(" - ")[0]
        
        # Update UI
        self.validate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Running validation...")
        self.status_label.setStyleSheet("color: blue;")
        
        # Start worker thread
        self.validation_worker = ValidationWorker(self.pdf_path, profile)
        self.validation_worker.validation_complete.connect(self.on_validation_complete)
        self.validation_worker.validation_error.connect(self.on_validation_error)
        self.validation_worker.start()
        
    def on_validation_complete(self, issues: List[ValidationIssue]):
        """Handle validation completion"""
        self.current_issues = issues
        self.populate_issues_tree(issues)
        self.update_status(issues)
        
        # Reset UI
        self.validate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Emit signal with validation results
        self.validation_completed.emit(issues)
        
    def on_validation_error(self, error_message: str):
        """Handle validation error"""
        self.status_label.setText(f"Validation failed: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        
        # Reset UI
        self.validate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def populate_issues_tree(self, issues: List[ValidationIssue]):
        """Populate the issues tree widget"""
        self.issues_tree.clear()
        
        # Group issues by severity
        errors = [issue for issue in issues if issue.severity == "ERROR"]
        warnings = [issue for issue in issues if issue.severity == "WARNING"]
        info = [issue for issue in issues if issue.severity == "INFO"]
        
        # Add error group
        if errors:
            error_item = QTreeWidgetItem(["Errors", "", ""])
            error_item.setBackground(0, QColor(255, 200, 200))
            font = error_item.font(0)
            font.setBold(True)
            error_item.setFont(0, font)
            self.issues_tree.addTopLevelItem(error_item)
            
            for issue in errors:
                item = QTreeWidgetItem([issue.description, issue.severity, issue.rule_id])
                item.setData(0, Qt.ItemDataRole.UserRole, issue)
                error_item.addChild(item)
            
            error_item.setExpanded(True)
        
        # Add warning group
        if warnings:
            warning_item = QTreeWidgetItem(["Warnings", "", ""])
            warning_item.setBackground(0, QColor(255, 255, 200))
            font = warning_item.font(0)
            font.setBold(True)
            warning_item.setFont(0, font)
            self.issues_tree.addTopLevelItem(warning_item)
            
            for issue in warnings:
                item = QTreeWidgetItem([issue.description, issue.severity, issue.rule_id])
                item.setData(0, Qt.ItemDataRole.UserRole, issue)
                warning_item.addChild(item)
        
        # Add info group
        if info:
            info_item = QTreeWidgetItem(["Information", "", ""])
            info_item.setBackground(0, QColor(200, 200, 255))
            font = info_item.font(0)
            font.setBold(True)
            info_item.setFont(0, font)
            self.issues_tree.addTopLevelItem(info_item)
            
            for issue in info:
                item = QTreeWidgetItem([issue.description, issue.severity, issue.rule_id])
                item.setData(0, Qt.ItemDataRole.UserRole, issue)
                info_item.addChild(item)
        
        # Update counts
        self.counts_label.setText(f"Issues: {len(errors)} Errors, {len(warnings)} Warnings")
        
    def update_status(self, issues: List[ValidationIssue]):
        """Update validation status"""
        error_count = len([i for i in issues if i.severity == "ERROR"])
        
        if error_count == 0:
            self.status_label.setText("✅ PDF/UA compliant")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(f"❌ {error_count} compliance issues found")
            self.status_label.setStyleSheet("color: red;")
            
    def on_issue_selected(self, item: QTreeWidgetItem, column: int):
        """Handle issue selection in tree"""
        issue = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(issue, ValidationIssue):
            self.show_issue_details(issue)
            self.jump_button.setEnabled(True)
            self.fix_button.setEnabled(True)
        else:
            self.jump_button.setEnabled(False)
            self.fix_button.setEnabled(False)
            
    def show_issue_details(self, issue: ValidationIssue):
        """Show detailed information about an issue"""
        details = f"Rule ID: {issue.rule_id}\n"
        details += f"Severity: {issue.severity}\n"
        details += f"Description: {issue.description}\n"
        
        if issue.location:
            details += f"Location: {issue.location}\n"
        if issue.page_number:
            details += f"Page: {issue.page_number}\n"
        if issue.suggested_fix:
            details += f"\nSuggested Fix:\n{issue.suggested_fix}"
            
        self.details_text.setPlainText(details)
        
    def on_issue_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on issue"""
        self.jump_to_issue()
        
    def jump_to_issue(self):
        """Jump to the selected issue location"""
        current_item = self.issues_tree.currentItem()
        if current_item:
            issue = current_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(issue, ValidationIssue):
                # For now, emit signal to main window
                # Later, we can implement more sophisticated mapping
                if issue.page_number:
                    self.jump_to_page.emit(issue.page_number - 1)
                else:
                    # Try to guess page based on rule type
                    self.jump_to_page.emit(0)  # Default to first page
                    
    def show_fix_suggestion(self):
        """Show fix suggestion for selected issue"""
        current_item = self.issues_tree.currentItem()
        if current_item:
            issue = current_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(issue, ValidationIssue) and issue.suggested_fix:
                from PyQt6.QtWidgets import QMessageBox
                
                msg = QMessageBox(self)
                msg.setWindowTitle(f"Fix Suggestion - {issue.rule_id}")
                msg.setText(issue.suggested_fix)
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
