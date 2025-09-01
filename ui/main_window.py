"""
Main Window for PDF Accessibility Remediation Tool
Implements the primary UI layout with PDF viewer, properties panel, and metadata panel
Enhanced with professional UX improvements
"""
from PyQt6.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, 
                             QSplitter, QMenuBar, QStatusBar, QFileDialog, 
                             QMessageBox, QPushButton, QLabel, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap, QImage, QCloseEvent

from .pdf_viewer import PDFViewer
from .properties_panel import PropertiesPanel
from .metadata_panel import MetadataPanel
from .validation_panel import ValidationPanel
from .progress_dialog import ProgressDialog
from .feedback_dialogs import SuccessDialog, ErrorDialog
from core.pdf_document import PDFDocument
from core.pdf_exporter import PDFExporter
import os


class PDFExportWorker(QThread):
    """Worker thread for PDF export operations"""
    
    # Signals for communication with main thread
    progress_update = pyqtSignal(str, str, int)  # step_name, description, progress
    export_complete = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, source_path, output_path, metadata, sidecar_data):
        super().__init__()
        self.source_path = source_path
        self.output_path = output_path
        self.metadata = metadata
        self.sidecar_data = sidecar_data
        self.exporter = PDFExporter()
        
    def run(self):
        """Execute the export operation"""
        try:
            # Set up progress callback
            self.exporter.set_progress_callback(self.update_progress)
            
            # Perform the export
            success = self.exporter.export_pdf_with_metadata(
                self.source_path,
                self.output_path,
                self.metadata,
                self.sidecar_data
            )
            
            if success:
                self.export_complete.emit(True, f"PDF successfully exported to {os.path.basename(self.output_path)}")
            else:
                self.export_complete.emit(False, "Export failed due to processing errors")
                
        except Exception as e:
            self.export_complete.emit(False, f"Export failed: {str(e)}")
    
    def update_progress(self, step_name, description, progress):
        """Callback for progress updates"""
        self.progress_update.emit(step_name, description, progress)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_document = None
        self.current_page = 0
        
        self.setWindowTitle("PDF Accessibility Remediation Tool")
        self.setGeometry(100, 100, 1800, 1200)  # Even larger window
        self.setMinimumSize(1600, 1000)  # Larger minimum size
        
        self.setup_ui()
        self.create_menus()
        self.create_status_bar()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # PDF Viewer (left side)
        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.element_selected.connect(self.on_element_selected)
        self.pdf_viewer.element_created.connect(self.on_element_created)
        self.pdf_viewer.element_deleted.connect(self.on_element_deleted)
        self.pdf_viewer.element_resized.connect(self.on_element_resized)
        
        # Create the panels
        self.properties_panel = PropertiesPanel()
        self.properties_panel.properties_changed.connect(self.on_properties_changed)
        
        self.validation_panel = ValidationPanel()
        self.validation_panel.jump_to_page.connect(self.on_jump_to_page)
        self.validation_panel.validation_completed.connect(self.on_validation_completed)
        
        self.metadata_panel = MetadataPanel()
        self.metadata_panel.metadata_changed.connect(self.on_metadata_changed)
        
        # Right panel container with scroll area
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setMinimumWidth(500)  # Increased from 450
        right_scroll.setMaximumWidth(700)  # Increased from 650
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create widget to hold all right panels
        right_content = QWidget()
        right_content.setMinimumHeight(1900)  # Increased from 1700 to accommodate larger validation panel
        right_layout = QVBoxLayout(right_content)
        right_layout.setSpacing(20)  # More spacing between panels
        right_layout.setContentsMargins(15, 15, 15, 15)  # Larger margins
        
        # Add panels directly to layout with fixed sizes
        right_layout.addWidget(self.properties_panel)
        right_layout.addWidget(self.validation_panel) 
        right_layout.addWidget(self.metadata_panel)
        
        # Set minimum heights to ensure panels are readable - much larger since we have scrolling
        self.properties_panel.setMinimumHeight(600)  # Increased from 400 - plenty of room for all fields
        self.validation_panel.setMinimumHeight(700)  # Increased from 500 - more room for issues tree
        self.metadata_panel.setMinimumHeight(500)    # Increased from 300 - more room for document properties
        
        # Also set size policies to prevent excessive compression
        from PyQt6.QtWidgets import QSizePolicy
        self.properties_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.validation_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.metadata_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Set the content widget in the scroll area
        right_scroll.setWidget(right_content)
        
        # Add to main splitter
        main_splitter.addWidget(self.pdf_viewer)
        main_splitter.addWidget(right_scroll)
        main_splitter.setSizes([900, 700])  # More balanced split - more space for panels
        
        main_layout.addWidget(main_splitter)
        
    def create_menus(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open PDF', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_pdf)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_sidecar_action = QAction('Save Edits', self)
        save_sidecar_action.setShortcut('Ctrl+S')
        save_sidecar_action.triggered.connect(self.save_sidecar)
        file_menu.addAction(save_sidecar_action)
        
        export_action = QAction('Export PDF', self)
        export_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.pdf_viewer.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.pdf_viewer.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_width_action = QAction('Fit Width', self)
        fit_width_action.triggered.connect(self.pdf_viewer.fit_width)
        view_menu.addAction(fit_width_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        validate_action = QAction('Validate PDF/UA', self)
        validate_action.setShortcut('Ctrl+T')
        validate_action.triggered.connect(self.run_validation)
        tools_menu.addAction(validate_action)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def open_pdf(self):
        """Open PDF file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open PDF", 
            "", 
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.load_pdf(file_path)
            
    def load_pdf(self, file_path: str):
        """Load a PDF document"""
        try:
            # Close existing document
            if self.pdf_document:
                self.pdf_document.close()
            
            # Load new document
            self.pdf_document = PDFDocument(file_path)
            
            if self.pdf_document.doc:
                # Update UI components
                self.pdf_viewer.set_document(self.pdf_document)
                self.metadata_panel.set_document(self.pdf_document)
                self.validation_panel.set_pdf_path(file_path)
                
                # Update status
                self.status_bar.showMessage(f"Loaded: {file_path} ({self.pdf_document.total_pages} pages)")
                
                # Load first page
                self.current_page = 0
                self.pdf_viewer.show_page(0)
                
            else:
                QMessageBox.critical(self, "Error", "Failed to load PDF file")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading PDF: {str(e)}")
            
    def on_element_selected(self, element_data):
        """Handle element selection in PDF viewer"""
        self.properties_panel.set_element(element_data)
        
    def on_properties_changed(self, element_id, properties):
        """Handle property changes from properties panel"""
        if self.pdf_document:
            print(f"DEBUG: Updating element {element_id} with properties: {properties}")
            
            # Update the element in the sidecar
            success = self.pdf_document.update_element_properties(
                self.current_page, 
                element_id, 
                properties
            )
            
            print(f"DEBUG: Update success: {success}")
            
            if success:
                # Save sidecar immediately to persist changes
                save_success = self.pdf_document.save_sidecar()
                print(f"DEBUG: Sidecar save success: {save_success}")
                
                self.status_bar.showMessage(f"Updated and saved {element_id} properties", 2000)
                
                # If role changed, just update the display without reloading
                if 'role' in properties:
                    self.pdf_viewer.page_widget.update_display()
            else:
                self.status_bar.showMessage("Failed to update properties", 2000)
    
    def on_element_created(self, element_data):
        """Handle new element creation"""
        if self.pdf_document:
            # Add element to the PDF document's sidecar
            page_key = str(self.current_page)
            if page_key not in self.pdf_document.sidecar_data["pages"]:
                self.pdf_document.sidecar_data["pages"][page_key] = {"elements": []}
            
            # Create sidecar entry
            sidecar_element = {
                "id": element_data["id"],
                "properties": element_data.get("properties", {}),
                "role": element_data.get("role", "P"),
                "bbox": element_data.get("bbox", []),
                "text": element_data.get("text", "")
            }
            self.pdf_document.sidecar_data["pages"][page_key]["elements"].append(sidecar_element)
            
            # Auto-save
            self.pdf_document.save_sidecar()
            
            self.status_bar.showMessage(f"Created new {element_data.get('type', 'element')}: {element_data['id']}", 3000)
            
            # Select the new element in properties panel
            self.properties_panel.set_element(element_data)
    
    def on_element_deleted(self, element_id):
        """Handle element deletion"""
        if self.pdf_document:
            # Remove from sidecar
            page_key = str(self.current_page)
            if page_key in self.pdf_document.sidecar_data["pages"]:
                elements = self.pdf_document.sidecar_data["pages"][page_key]["elements"]
                self.pdf_document.sidecar_data["pages"][page_key]["elements"] = [
                    e for e in elements if e["id"] != element_id
                ]
            
            # Auto-save
            self.pdf_document.save_sidecar()
            
            self.status_bar.showMessage(f"Deleted element: {element_id}", 3000)
            
            # Clear properties panel
            self.properties_panel.set_element(None)
    
    def on_element_resized(self, element_id, new_bbox):
        """Handle element resizing"""
        if self.pdf_document:
            # Update bbox in sidecar
            success = self.pdf_document.update_element_properties(
                self.current_page,
                element_id,
                {"bbox": new_bbox}
            )
            
            if success:
                # Auto-save
                self.pdf_document.save_sidecar()
                self.status_bar.showMessage(f"Resized element: {element_id}", 2000)
            else:
                self.status_bar.showMessage("Failed to resize element", 2000)
            
    def on_metadata_changed(self, metadata):
        """Handle metadata changes"""
        if self.pdf_document:
            self.pdf_document.sidecar_data["document"].update(metadata)
            self.status_bar.showMessage("Metadata updated", 2000)
            
    def on_jump_to_page(self, page_number: int):
        """Handle jump to page request from validation panel"""
        if self.pdf_document and 0 <= page_number < self.pdf_document.total_pages:
            self.current_page = page_number
            self.pdf_viewer.show_page(page_number)
            self.status_bar.showMessage(f"Jumped to page {page_number + 1}", 2000)
            
    def run_validation(self):
        """Trigger PDF validation"""
        if self.pdf_document and hasattr(self.pdf_document, 'file_path'):
            self.validation_panel.start_validation()
        else:
            QMessageBox.warning(self, "Warning", "No PDF document loaded")
            
    def on_validation_completed(self, issues: list):
        """Handle validation completion - pass issues to metadata panel for reports"""
        self.metadata_panel.set_validation_issues(issues)
        self.status_bar.showMessage(f"Validation complete: {len(issues)} issues found", 3000)
            
    def save_sidecar(self):
        """Save sidecar JSON file"""
        if not self.pdf_document:
            QMessageBox.warning(self, "Warning", "No PDF document loaded")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Edits",
            self.pdf_document.file_path.replace('.pdf', '_sidecar.json'),
            "JSON Files (*.json)"
        )
        
        if file_path:
            if self.pdf_document.save_sidecar(file_path):
                QMessageBox.information(self, "Success", "Edits saved successfully")
                self.status_bar.showMessage(f"Saved: {file_path}", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to save edits")
                
    def export_pdf(self):
        """Export remediated PDF with professional progress tracking"""
        if not self.pdf_document:
            QMessageBox.warning(self, "Warning", "No PDF document loaded")
            return

        # Get output file path
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Accessible PDF",
            "",
            "PDF files (*.pdf)"
        )
        
        if not output_path:
            return  # User cancelled
            
        # Get metadata from metadata panel
        metadata = self.metadata_panel.get_metadata()
        
        # Get sidecar data (element modifications)
        sidecar_data = None
        if self.pdf_document:
            sidecar_data = self.pdf_document.get_sidecar_data()
        
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog(
            self, 
            "Exporting Accessible PDF",
            show_details=True
        )
        
        # Set up the export worker
        self.export_worker = PDFExportWorker(
            self.pdf_document.file_path,
            output_path,
            metadata,
            sidecar_data
        )
        
        # Connect worker signals
        self.export_worker.progress_update.connect(self.on_export_progress)
        self.export_worker.export_complete.connect(self.on_export_complete)
        
        # Connect cancel signal
        self.progress_dialog.cancel_requested.connect(self.export_worker.terminate)
        
        # Set up progress dialog
        self.progress_dialog.set_total_steps(8)  # Number of export steps
        
        # Start the export
        self.export_worker.start()
        self.progress_dialog.exec()
    
    def on_export_progress(self, step_name: str, description: str, progress: int):
        """Handle export progress updates"""
        if hasattr(self, 'progress_dialog'):
            if progress == 0:
                # New step starting
                self.progress_dialog.update_step(step_name, description, 0)
            else:
                # Progress within current step
                self.progress_dialog.update_step_progress(progress, description)
    
    def on_export_complete(self, success: bool, message: str):
        """Handle export completion"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.finish_processing(success, message)
            
        # Show enhanced completion dialogs
        if success:
            # Get the output file path from the worker
            output_path = self.export_worker.output_path if hasattr(self.export_worker, 'output_path') else None
            
            # Create success dialog with file information
            success_dialog = SuccessDialog(
                self,
                title="PDF Export Successful",
                main_message="Your PDF has been successfully enhanced with accessibility features!",
                details=[
                    "✅ Document metadata updated",
                    "✅ Structure tree created",
                    "✅ Accessibility elements added",
                    "✅ PDF/UA compliance improved",
                    "🎯 Ready for screen readers and assistive technology"
                ],
                file_path=output_path
            )
            success_dialog.exec()
        else:
            # Create error dialog with suggestions
            error_dialog = ErrorDialog(
                self,
                title="PDF Export Failed", 
                main_message="The PDF export process encountered an error.",
                error_details=[message],
                suggestions=[
                    "Check that the source PDF is not corrupted",
                    "Ensure you have write permissions to the output location",
                    "Try exporting to a different location",
                    "Check if the PDF is password protected",
                    "Verify there's enough disk space available"
                ]
            )
            result = error_dialog.exec()
            
            # Handle retry if user chose to retry
            if result == 2:  # Retry was clicked
                QTimer.singleShot(100, self.export_pdf)  # Retry after dialog closes
        
    def closeEvent(self, a0):
        """Handle window close event"""
        if self.pdf_document:
            self.pdf_document.close()
        a0.accept()
