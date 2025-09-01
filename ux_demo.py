"""
UX Improvements Demonstration
Test script to showcase the enhanced user experience features
"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer, pyqtSignal, QThread
from ui.progress_dialog import ProgressDialog
from ui.feedback_dialogs import SuccessDialog, ErrorDialog
from ui.enhanced_status_bar import EnhancedStatusBar
import sys
import time


class UXDemoWindow(QMainWindow):
    """Demo window to showcase UX improvements"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Accessibility Tool - UX Improvements Demo")
        self.setGeometry(200, 200, 800, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup demo interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🎨 PDF Accessibility Tool - UX Improvements")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #007bff; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Demo buttons
        progress_btn = QPushButton("📊 Show Progress Dialog")
        progress_btn.clicked.connect(self.demo_progress_dialog)
        layout.addWidget(progress_btn)
        
        success_btn = QPushButton("🎉 Show Success Dialog")
        success_btn.clicked.connect(self.demo_success_dialog)
        layout.addWidget(success_btn)
        
        error_btn = QPushButton("❌ Show Error Dialog")
        error_btn.clicked.connect(self.demo_error_dialog)
        layout.addWidget(error_btn)
        
        status_btn = QPushButton("📱 Demo Status Bar")
        status_btn.clicked.connect(self.demo_status_bar)
        layout.addWidget(status_btn)
        
        export_btn = QPushButton("🚀 Simulate PDF Export")
        export_btn.clicked.connect(self.demo_export_process)
        layout.addWidget(export_btn)
        
        # Enhanced status bar
        self.status_bar = EnhancedStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Initialize status
        self.status_bar.show_message("🎨 UX Demo Ready - Click buttons to see improvements!")
        self.status_bar.update_accessibility_status("Demo Mode", "unknown")
        
    def demo_progress_dialog(self):
        """Demonstrate progress dialog"""
        dialog = ProgressDialog(self, "Processing Demo", show_details=True)
        dialog.set_total_steps(4)
        
        # Show the dialog
        dialog.show()
        
        # Simulate processing steps
        QTimer.singleShot(500, lambda: dialog.update_step("Loading", "Initializing components...", 0))
        QTimer.singleShot(1000, lambda: dialog.update_step_progress(50, "Loading PDF document"))
        QTimer.singleShot(1500, lambda: dialog.complete_step(True, "Components loaded"))
        
        QTimer.singleShot(2000, lambda: dialog.update_step("Analyzing", "Scanning document structure...", 0))
        QTimer.singleShot(2500, lambda: dialog.update_step_progress(75, "Processing page 2 of 5"))
        QTimer.singleShot(3000, lambda: dialog.complete_step(True, "Analysis complete"))
        
        QTimer.singleShot(3500, lambda: dialog.update_step("Processing", "Creating accessibility elements...", 0))
        QTimer.singleShot(4000, lambda: dialog.update_step_progress(90, "Generating structure tree"))
        QTimer.singleShot(4500, lambda: dialog.complete_step(True, "Processing complete"))
        
        QTimer.singleShot(5000, lambda: dialog.update_step("Finalizing", "Saving enhanced PDF...", 0))
        QTimer.singleShot(5500, lambda: dialog.update_step_progress(100, "Writing to disk"))
        QTimer.singleShot(6000, lambda: dialog.finish_processing(True, "PDF export completed successfully!"))
        
    def demo_success_dialog(self):
        """Demonstrate success dialog"""
        dialog = SuccessDialog(
            self,
            title="PDF Export Successful",
            main_message="Your PDF has been successfully enhanced with accessibility features!",
            details=[
                "✅ Document metadata updated",
                "✅ Structure tree created with 47 elements",
                "✅ PDF/UA compliance tags added",
                "✅ Reading order optimized",
                "✅ Alternative text applied to 12 images",
                "🎯 Ready for screen readers and assistive technology"
            ],
            file_path="/Users/demo/Documents/accessible_document.pdf"
        )
        dialog.exec()
        
    def demo_error_dialog(self):
        """Demonstrate error dialog"""
        dialog = ErrorDialog(
            self,
            title="PDF Processing Failed",
            main_message="The PDF processing encountered an error and could not complete.",
            error_details=[
                "Failed to parse PDF structure",
                "pikepdf.PdfError: Invalid PDF object reference",
                "Error occurred at page 5 of 12"
            ],
            suggestions=[
                "Check that the PDF file is not corrupted",
                "Ensure the PDF is not password protected",
                "Try processing a smaller section of the document first",
                "Update to the latest version of the PDF processing library",
                "Contact support if the issue persists"
            ]
        )
        result = dialog.exec()
        
        if result == 2:  # Retry was clicked
            self.status_bar.show_message("🔄 User requested retry", 3000)
            
    def demo_status_bar(self):
        """Demonstrate status bar features"""
        self.status_bar.show_message("📱 Status bar demo starting...", 2000)
        
        QTimer.singleShot(2000, lambda: self.status_bar.update_document_info("sample_document.pdf", 8, 144))
        QTimer.singleShot(3000, lambda: self.status_bar.update_accessibility_status("Validating", "validating"))
        QTimer.singleShot(4000, lambda: self.status_bar.show_tip("Use Ctrl+O to open a PDF document"))
        QTimer.singleShot(6000, lambda: self.status_bar.update_accessibility_status("Enhanced", "improved"))
        QTimer.singleShot(7000, lambda: self.status_bar.show_shortcut_hint("Export PDF", "Ctrl+E"))
        
    def demo_export_process(self):
        """Demonstrate complete export process with progress"""
        # Start progress in status bar
        self.status_bar.start_progress("Exporting PDF")
        
        # Show progress dialog
        dialog = ProgressDialog(self, "Exporting Accessible PDF", show_details=True)
        dialog.set_total_steps(7)
        dialog.show()
        
        # Simulate export steps
        steps = [
            (500, "Initializing Export", "Opening source PDF file...", 0),
            (1000, None, None, 20),
            (1500, "Updating Metadata", "Setting document properties...", 0),
            (2000, None, None, 40),
            (2500, "Creating Structure Tree", "Building accessibility structure...", 0),
            (3000, None, None, 60),
            (3500, "Creating Elements", "Generating 144 accessibility elements...", 0),
            (4000, None, None, 80),
            (4500, "Advanced Features", "Applying marked content integration...", 0),
            (5000, None, None, 90),
            (5500, "Generating Report", "Creating status report...", 0),
            (6000, None, None, 95),
            (6500, "Saving PDF", "Writing accessible PDF to disk...", 0),
            (7000, None, None, 100)
        ]
        
        for delay, step_name, description, progress in steps:
            if step_name:
                QTimer.singleShot(delay, lambda s=step_name, d=description, p=progress: (
                    dialog.update_step(s, d, p),
                    self.status_bar.update_progress(p, d)
                ))
            else:
                QTimer.singleShot(delay, lambda p=progress: (
                    dialog.update_step_progress(p),
                    self.status_bar.update_progress(p)
                ))
        
        # Complete the process
        QTimer.singleShot(7500, lambda: (
            dialog.finish_processing(True, "PDF export completed successfully!"),
            self.status_bar.finish_progress(True, "PDF exported successfully")
        ))
        
        # Show success dialog after progress completes
        QTimer.singleShot(8000, self.demo_success_dialog)


def main():
    """Run the UX improvements demo"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    window = UXDemoWindow()
    window.show()
    
    # Show welcome message
    window.status_bar.show_message("🎨 Welcome to the UX Improvements Demo!", 5000)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
