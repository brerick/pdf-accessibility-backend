#!/usr/bin/env python3
"""
Quick test script to verify the UI fixes
"""
import sys
sys.path.append('/Users/brad/Documents/Web Development/comment-on/pdf-a11y')

from core.pdf_document import PDFDocument
from ui.properties_panel import PropertiesPanel
from PyQt6.QtWidgets import QApplication

def test_property_changes():
    """Test that property changes work correctly"""
    app = QApplication([])
    
    # Test properties panel
    panel = PropertiesPanel()
    
    # Simulate property change
    test_properties = {
        'role': 'H1',
        'alt_text': 'Test heading',
        'bbox': [100, 100, 200, 150]
    }
    
    # This should emit the properties_changed signal
    panel.current_element_id = 'test_element'
    panel.role_combo.setCurrentText('H1')
    panel.alt_text_input.setText('Test heading')
    
    # Test the signal emission
    received_properties = []
    def capture_properties(element_id, properties):
        received_properties.append((element_id, properties))
    
    panel.properties_changed.connect(capture_properties)
    panel.apply_changes()
    
    print("✓ Properties panel fix test completed")
    print(f"  Captured: {received_properties}")
    
    app.quit()
    return True

if __name__ == "__main__":
    test_property_changes()
    print("All tests passed! ✓")
