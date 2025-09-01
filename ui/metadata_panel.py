"""
Metadata Panel
Allows editing of document-level metadata and PDF export
Phase 3 implementation with export functionality
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QCheckBox, QComboBox, QLabel, QPushButton, QGroupBox,
                             QFileDialog, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal
from typing import Dict, Any, Optional
import os

from core.pdf_exporter import PDFExporter


class MetadataPanel(QWidget):
    """Panel for editing document metadata and exporting PDFs"""
    metadata_changed = pyqtSignal(dict)
    export_requested = pyqtSignal(str, dict)  # New signal for export requests
    
    def __init__(self):
        super().__init__()
        self.pdf_document = None
        self.pdf_exporter = PDFExporter()
        self.validation_issues = []  # Store validation issues for reports
        self.setup_ui()
        
    def setup_ui(self):
        """Setup metadata panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Document Metadata")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)
        
        # Document properties group
        doc_group = QGroupBox("Document Properties")
        doc_layout = QFormLayout(doc_group)
        
        # Document title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter document title")
        self.title_edit.textChanged.connect(self.on_title_changed)
        doc_layout.addRow("Title:", self.title_edit)
        
        # Document language
        self.language_combo = QComboBox()
        self.language_combo.setEditable(True)
        self.language_combo.addItems([
            "en-US",  # English (US)
            "en-GB",  # English (UK)
            "es-ES",  # Spanish (Spain)
            "es-MX",  # Spanish (Mexico)
            "fr-FR",  # French (France)
            "fr-CA",  # French (Canada)
            "de-DE",  # German
            "it-IT",  # Italian
            "pt-BR",  # Portuguese (Brazil)
            "pt-PT",  # Portuguese (Portugal)
            "zh-CN",  # Chinese (Simplified)
            "zh-TW",  # Chinese (Traditional)
            "ja-JP",  # Japanese
            "ko-KR",  # Korean
            "ar-SA",  # Arabic
            "ru-RU",  # Russian
            "hi-IN",  # Hindi
        ])
        self.language_combo.setCurrentText("en-US")
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        doc_layout.addRow("Language:", self.language_combo)
        
        layout.addWidget(doc_group)
        
        # Accessibility properties group
        a11y_group = QGroupBox("Accessibility Properties")
        a11y_layout = QFormLayout(a11y_group)
        
        # Tagged PDF flag
        self.tagged_checkbox = QCheckBox("Document is tagged for accessibility")
        self.tagged_checkbox.stateChanged.connect(self.on_tagged_changed)
        a11y_layout.addRow("Tagged:", self.tagged_checkbox)
        
        # Structure tree status
        self.structure_label = QLabel("Not analyzed")
        a11y_layout.addRow("Structure Tree:", self.structure_label)
        
        # Page count
        self.page_count_label = QLabel("0")
        a11y_layout.addRow("Total Pages:", self.page_count_label)
        
        layout.addWidget(a11y_group)
        
        # PDF/UA compliance group
        compliance_group = QGroupBox("PDF/UA Compliance")
        compliance_layout = QVBoxLayout(compliance_group)
        
        self.compliance_status = QLabel("Not validated")
        self.compliance_status.setStyleSheet("color: gray;")
        compliance_layout.addWidget(self.compliance_status)
        
        self.validate_button = QPushButton("Validate with veraPDF")
        self.validate_button.clicked.connect(self.validate_document)
        compliance_layout.addWidget(self.validate_button)
        
        layout.addWidget(compliance_group)
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        self.apply_metadata_button = QPushButton("Apply Metadata Changes")
        self.apply_metadata_button.clicked.connect(self.apply_metadata)
        button_layout.addWidget(self.apply_metadata_button)
        
        # Export section
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout(export_group)
        
        # Add explanatory label
        export_info = QLabel("Choose what to export:")
        export_info.setStyleSheet("font-style: italic; color: #666; margin-bottom: 5px;")
        export_layout.addWidget(export_info)
        
        # Export PDF with metadata
        export_pdf_layout = QHBoxLayout()
        self.export_pdf_button = QPushButton("Export PDF with Metadata")
        self.export_pdf_button.setToolTip("Export PDF with accessibility metadata (title, language, tagged flag)")
        self.export_pdf_button.clicked.connect(self.export_pdf)
        export_pdf_layout.addWidget(self.export_pdf_button)
        export_layout.addLayout(export_pdf_layout)
        
        # Separator
        export_layout.addWidget(QLabel("— OR —"))
        
        # Export report options
        report_info = QLabel("Generate remediation reports:")
        report_info.setStyleSheet("font-weight: bold; margin-top: 5px;")
        export_layout.addWidget(report_info)
        
        report_layout = QHBoxLayout()
        self.export_json_button = QPushButton("Export Report (JSON)")
        self.export_json_button.setToolTip("Generate detailed remediation report in JSON format")
        self.export_json_button.clicked.connect(lambda: self.export_report('json'))
        report_layout.addWidget(self.export_json_button)
        
        self.export_html_button = QPushButton("Export Report (HTML)")
        self.export_html_button.setToolTip("Generate formatted remediation report in HTML format")
        self.export_html_button.clicked.connect(lambda: self.export_report('html'))
        report_layout.addWidget(self.export_html_button)
        
        export_layout.addLayout(report_layout)
        
        button_layout.addWidget(export_group)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Initially disable controls
        self.set_enabled(False)
        
    def set_document(self, pdf_document):
        """Set the PDF document"""
        self.pdf_document = pdf_document
        
        if pdf_document:
            self.set_enabled(True)
            self.load_document_metadata()
        else:
            self.set_enabled(False)
            self.clear_fields()
            
    def load_document_metadata(self):
        """Load document metadata from PDF"""
        if not self.pdf_document:
            return
            
        doc_data = self.pdf_document.sidecar_data.get("document", {})
        
        # Load title
        title = doc_data.get("title", "")
        if not title and self.pdf_document.doc:
            # Try to get title from PDF metadata
            metadata = self.pdf_document.doc.metadata
            title = metadata.get("title", "")
        self.title_edit.setText(title)
        
        # Load language
        language = doc_data.get("language", "en-US")
        self.language_combo.setCurrentText(language)
        
        # Load tagged status
        tagged = doc_data.get("tagged", False)
        self.tagged_checkbox.setChecked(tagged)
        
        # Update page count
        self.page_count_label.setText(str(self.pdf_document.total_pages))
        
        # Check structure tree (simplified check)
        self.check_structure_tree()
        
    def check_structure_tree(self):
        """Check if document has structure tree"""
        if not self.pdf_document or not self.pdf_document.doc:
            self.structure_label.setText("Not analyzed")
            return
            
        try:
            # Simple check for structure tree
            catalog = self.pdf_document.doc[1].get_object()  # Document catalog
            if "/StructTreeRoot" in catalog:
                self.structure_label.setText("Present")
                self.structure_label.setStyleSheet("color: green;")
            else:
                self.structure_label.setText("Missing")
                self.structure_label.setStyleSheet("color: red;")
        except:
            self.structure_label.setText("Unknown")
            self.structure_label.setStyleSheet("color: gray;")
            
    def clear_fields(self):
        """Clear all metadata fields"""
        self.title_edit.clear()
        self.language_combo.setCurrentText("en-US")
        self.tagged_checkbox.setChecked(False)
        self.page_count_label.setText("0")
        self.structure_label.setText("Not analyzed")
        self.compliance_status.setText("Not validated")
        self.compliance_status.setStyleSheet("color: gray;")
        
    def set_enabled(self, enabled: bool):
        """Enable/disable all controls"""
        self.title_edit.setEnabled(enabled)
        self.language_combo.setEnabled(enabled)
        self.tagged_checkbox.setEnabled(enabled)
        self.validate_button.setEnabled(enabled)
        self.apply_metadata_button.setEnabled(enabled)
        self.export_pdf_button.setEnabled(enabled)
        self.export_json_button.setEnabled(enabled)
        self.export_html_button.setEnabled(enabled)
        
    def on_title_changed(self, title: str):
        """Handle title change"""
        if self.pdf_document:
            self.pdf_document.sidecar_data["document"]["title"] = title
            
    def on_language_changed(self, language: str):
        """Handle language change"""
        if self.pdf_document:
            self.pdf_document.sidecar_data["document"]["language"] = language
            
    def on_tagged_changed(self, state: int):
        """Handle tagged checkbox change"""
        if self.pdf_document:
            self.pdf_document.sidecar_data["document"]["tagged"] = bool(state)
            
    def apply_metadata(self):
        """Apply metadata changes"""
        if not self.pdf_document:
            return
            
        metadata = {
            "title": self.title_edit.text().strip(),
            "language": self.language_combo.currentText(),
            "tagged": self.tagged_checkbox.isChecked()
        }
        
        self.metadata_changed.emit(metadata)
        
    def validate_document(self):
        """Validate document with veraPDF (placeholder)"""
        # This will be implemented in Phase 2
        self.compliance_status.setText("Validation not yet implemented")
        self.compliance_status.setStyleSheet("color: orange;")
        
    def set_validation_issues(self, issues: list):
        """Set validation issues for report generation"""
        self.validation_issues = issues
        
    def export_pdf(self):
        """Export PDF with updated metadata"""
        if not self.pdf_document:
            QMessageBox.warning(self, "No Document", "Please load a PDF document first.")
            return
            
        # Get output file path
        source_path = self.pdf_document.file_path
        suggested_name = os.path.splitext(os.path.basename(source_path))[0] + "_accessible.pdf"
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF with Accessibility Metadata",
            suggested_name,
            "PDF Files (*.pdf)"
        )
        
        if not output_path:
            return
            
        # Prepare metadata
        metadata = {
            "title": self.title_edit.text().strip(),
            "language": self.language_combo.currentText(),
            "marked": self.tagged_checkbox.isChecked()
        }
        
        # Export the PDF
        try:
            success = self.pdf_exporter.export_pdf_with_metadata(
                source_path, output_path, metadata, self.pdf_document.sidecar_data
            )
            
            if success:
                reply = QMessageBox.question(
                    self,
                    "Export Successful",
                    f"PDF exported successfully to:\n{output_path}\n\n"
                    "The exported PDF includes:\n"
                    "• Updated document metadata\n"
                    "• Accessibility flags (/MarkInfo)\n"
                    "• Document language setting\n"
                    "• PDF/UA structure tree with role mappings\n"
                    "• Sample StructElem objects (Phase 4 Step 2)\n\n"
                    "Would you like to generate a remediation report as well?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                # If user wants a report, show format selection
                if reply == QMessageBox.StandardButton.Yes:
                    # Create custom dialog for format selection
                    format_box = QMessageBox(self)
                    format_box.setWindowTitle("Report Format")
                    format_box.setText("Which format would you like for the remediation report?")
                    format_box.setIcon(QMessageBox.Icon.Question)
                    
                    json_button = format_box.addButton("JSON", QMessageBox.ButtonRole.AcceptRole)
                    html_button = format_box.addButton("HTML", QMessageBox.ButtonRole.AcceptRole) 
                    cancel_button = format_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                    
                    format_box.exec()
                    
                    if format_box.clickedButton() == json_button:
                        self.export_report('json')
                    elif format_box.clickedButton() == html_button:
                        self.export_report('html')
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    "Failed to export PDF. Please check the file path and try again."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export:\n{str(e)}"
            )
    
    def export_report(self, format_type: str):
        """Export accessibility remediation report"""
        if not self.pdf_document:
            QMessageBox.warning(self, "No Document", "Please load a PDF document first.")
            return
            
        # Get output file path
        if format_type == 'json':
            file_filter = "JSON Files (*.json)"
            extension = ".json"
        else:
            file_filter = "HTML Files (*.html)"
            extension = ".html"
            
        source_path = self.pdf_document.file_path
        suggested_name = os.path.splitext(os.path.basename(source_path))[0] + f"_report{extension}"
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Remediation Report ({format_type.upper()})",
            suggested_name,
            file_filter
        )
        
        if not output_path:
            return
            
        # Prepare metadata
        metadata = {
            "title": self.title_edit.text().strip(),
            "language": self.language_combo.currentText(),
            "marked": self.tagged_checkbox.isChecked()
        }
        
        # Generate report
        try:
            success = self.pdf_exporter.generate_remediation_report(
                source_path, output_path, metadata, 
                self.pdf_document.sidecar_data, self.validation_issues, format_type
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Report Generated",
                    f"Remediation report generated successfully:\n{output_path}"
                )
                
                # Ask if user wants to open the report
                if format_type == 'html':
                    reply = QMessageBox.question(
                        self,
                        "Open Report",
                        "Would you like to open the HTML report in your browser?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        import webbrowser
                        webbrowser.open(f"file://{output_path}")
            else:
                QMessageBox.critical(
                    self,
                    "Report Generation Failed",
                    "Failed to generate report. Please check the file path and try again."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Report Error",
                f"An error occurred during report generation:\n{str(e)}"
            )
