"""
Properties Panel
Allows editing of element properties like role, alt text, etc.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                             QLineEdit, QTextEdit, QLabel, QPushButton, QGroupBox)
from PyQt6.QtCore import pyqtSignal
from typing import Dict, Any, Optional


class PropertiesPanel(QWidget):
    """Panel for editing element properties"""
    properties_changed = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.current_element = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup properties panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Element Properties")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)
        
        # Element info group
        info_group = QGroupBox("Element Information")
        info_layout = QFormLayout(info_group)
        
        self.element_id_label = QLabel("None")
        info_layout.addRow("ID:", self.element_id_label)
        
        self.element_type_label = QLabel("None")
        info_layout.addRow("Type:", self.element_type_label)
        
        layout.addWidget(info_group)
        
        # Role selection group
        role_group = QGroupBox("Accessibility Role")
        role_layout = QFormLayout(role_group)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "P",  # Paragraph
            "H1", "H2", "H3", "H4", "H5", "H6",  # Headings
            "Figure",  # Figure/Image
            "Link",  # Link
            "L",  # List
            "LI",  # List Item
            "LBody",  # List Body
            "Table",  # Table
            "TH",  # Table Header
            "TD",  # Table Data
            "Caption",  # Caption
            "Span",  # Span
            "Div",  # Division
            "Document"  # Document
        ])
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        role_layout.addRow("Role:", self.role_combo)
        
        layout.addWidget(role_group)
        
        # Properties group
        props_group = QGroupBox("Properties")
        props_layout = QFormLayout(props_group)
        
        # Alt text for images
        self.alt_text_edit = QTextEdit()
        self.alt_text_edit.setMaximumHeight(80)
        self.alt_text_edit.textChanged.connect(self.on_alt_text_changed)
        props_layout.addRow("Alt Text:", self.alt_text_edit)
        
        # Language override
        self.language_edit = QLineEdit()
        self.language_edit.setPlaceholderText("e.g., en-US, fr-FR")
        self.language_edit.textChanged.connect(self.on_language_changed)
        props_layout.addRow("Language:", self.language_edit)
        
        # Table header scope (for TH elements)
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(["", "Row", "Column", "Both", "RowGroup", "ColGroup"])
        self.scope_combo.currentTextChanged.connect(self.on_scope_changed)
        props_layout.addRow("TH Scope:", self.scope_combo)
        
        # Actual text override
        self.actual_text_edit = QLineEdit()
        self.actual_text_edit.setPlaceholderText("Override display text")
        self.actual_text_edit.textChanged.connect(self.on_actual_text_changed)
        props_layout.addRow("Actual Text:", self.actual_text_edit)
        
        layout.addWidget(props_group)
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_button)
        
        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.clear_selection)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Initially disable all controls
        self.set_enabled(False)
        
    def set_element(self, element_data: Optional[Dict[str, Any]]):
        """Set the current element to edit"""
        self.current_element = element_data
        
        if element_data:
            self.set_enabled(True)
            self.load_element_data(element_data)
        else:
            self.set_enabled(False)
            self.clear_fields()
            
    def load_element_data(self, element_data: Dict[str, Any]):
        """Load element data into form fields"""
        # Element info
        self.element_id_label.setText(element_data.get('id', 'Unknown'))
        self.element_type_label.setText(element_data.get('type', 'Unknown'))
        
        # Role
        role = element_data.get('role', 'P')
        index = self.role_combo.findText(role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
        
        # Properties
        properties = element_data.get('properties', {})
        
        self.alt_text_edit.setPlainText(properties.get('alt_text', ''))
        self.language_edit.setText(properties.get('language', ''))
        self.scope_combo.setCurrentText(properties.get('scope', ''))
        self.actual_text_edit.setText(properties.get('actual_text', ''))
        
        # Show/hide relevant fields based on element type and role
        self.update_field_visibility(element_data.get('type'), role)
        
    def update_field_visibility(self, element_type: str, role: str):
        """Show/hide fields based on element type and role"""
        # Alt text is mainly for images and figures
        show_alt = element_type == 'image' or role == 'Figure'
        self.alt_text_edit.setVisible(show_alt)
        self.alt_text_edit.parent().layout().labelForField(self.alt_text_edit).setVisible(show_alt)
        
        # Scope is only for table headers
        show_scope = role == 'TH'
        self.scope_combo.setVisible(show_scope)
        self.scope_combo.parent().layout().labelForField(self.scope_combo).setVisible(show_scope)
        
    def clear_fields(self):
        """Clear all form fields"""
        self.element_id_label.setText("None")
        self.element_type_label.setText("None")
        self.role_combo.setCurrentIndex(0)
        self.alt_text_edit.clear()
        self.language_edit.clear()
        self.scope_combo.setCurrentIndex(0)
        self.actual_text_edit.clear()
        
    def set_enabled(self, enabled: bool):
        """Enable/disable all form controls"""
        self.role_combo.setEnabled(enabled)
        self.alt_text_edit.setEnabled(enabled)
        self.language_edit.setEnabled(enabled)
        self.scope_combo.setEnabled(enabled)
        self.actual_text_edit.setEnabled(enabled)
        self.apply_button.setEnabled(enabled)
        
    def on_role_changed(self, role: str):
        """Handle role change"""
        if self.current_element:
            self.update_field_visibility(self.current_element.get('type'), role)
            
    def on_alt_text_changed(self):
        """Handle alt text change"""
        pass  # Real-time updates can be added here
        
    def on_language_changed(self, language: str):
        """Handle language change"""
        pass  # Real-time updates can be added here
        
    def on_scope_changed(self, scope: str):
        """Handle scope change"""
        pass  # Real-time updates can be added here
        
    def on_actual_text_changed(self, text: str):
        """Handle actual text change"""
        pass  # Real-time updates can be added here
        
    def apply_changes(self):
        """Apply changes to current element"""
        if not self.current_element:
            return
            
        # Collect properties including the role change
        properties = {
            'role': self.role_combo.currentText(),
            'alt_text': self.alt_text_edit.toPlainText().strip(),
            'language': self.language_edit.text().strip(),
            'scope': self.scope_combo.currentText(),
            'actual_text': self.actual_text_edit.text().strip()
        }
        
        # Remove empty properties except for role (always keep role)
        filtered_properties = {'role': properties['role']}
        for k, v in properties.items():
            if k != 'role' and v:  # Keep non-empty values
                filtered_properties[k] = v
        
        # Emit signal with element ID and all properties
        self.properties_changed.emit(self.current_element['id'], filtered_properties)
        
        # Update the current element's role locally for UI consistency
        self.current_element['role'] = properties['role']
        
    def clear_selection(self):
        """Clear current element selection"""
        self.set_element(None)
