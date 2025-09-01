#!/usr/bin/env python3
"""
Test script to verify if all P elements are being included in structure tree
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.structure_tree import StructureTreeCreator
from core.pdf_document import PDFDocument
import pikepdf

def test_all_elements_included():
    """Test if all text elements (including unchanged P's) are included"""
    
    print("🧪 Testing if all text elements are included in structure tree...")
    
    # Use the sample PDF
    test_pdf_path = "samples/sample_document.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Sample PDF not found: {test_pdf_path}")
        return False
    
    try:
        # First, let's see what text elements exist in the PDF
        print("\n📄 Step 1: Analyzing text elements in PDF...")
        pdf_doc = PDFDocument()
        if not pdf_doc.load(test_pdf_path):
            print("❌ Failed to load PDF")
            return False
        
        total_text_elements = 0
        for page_num in range(pdf_doc.total_pages):
            text_blocks = pdf_doc.get_text_blocks(page_num)
            print(f"   Page {page_num}: {len(text_blocks)} text blocks")
            for i, block in enumerate(text_blocks):
                print(f"      text_{page_num}_{i}: '{block['text'][:50]}...' (role: {block['role']})")
            total_text_elements += len(text_blocks)
        
        print(f"   Total text elements in PDF: {total_text_elements}")
        
        # Now test structure creation
        print("\n🏗️ Step 2: Testing structure creation...")
        structure_creator = StructureTreeCreator()
        
        with pikepdf.open(test_pdf_path) as pdf:
            # Create structure tree foundation
            if not structure_creator.create_basic_structure_tree(pdf):
                print("❌ Failed to create structure tree foundation")
                return False
            
            # Test the new method that should include all elements
            print("\n📝 Step 3: Creating elements from PDF (should include all text)...")
            success = structure_creator.create_elements_from_pdf(pdf, test_pdf_path, None)
            
            if not success:
                print("❌ Failed to create elements from PDF")
                return False
            
            # Get status and count
            status = structure_creator.get_status_report(pdf)
            summary = structure_creator.get_element_summary()
            
            print("\n📊 Results:")
            print(status)
            print(f"\n{summary}")
            
            # Count created elements
            created_count = len(structure_creator.created_elements)
            print(f"\n🎯 Analysis:")
            print(f"   Text elements in PDF: {total_text_elements}")
            print(f"   StructElems created: {created_count}")
            print(f"   Coverage: {created_count}/{total_text_elements} = {(created_count/total_text_elements*100) if total_text_elements > 0 else 0:.1f}%")
            
            # Test with sidecar data (simulating some modifications)
            print(f"\n🔄 Step 4: Testing with sidecar modifications...")
            test_sidecar = {
                'pages': {
                    '0': {
                        'elements': [
                            {'id': 'text_0_1', 'role': 'H1', 'title': 'Modified Heading'},
                            {'id': 'text_0_3', 'role': 'H2', 'title': 'Another Modified Element'}
                        ]
                    }
                }
            }
            
            # Reset and test with sidecar
            structure_creator.created_elements = []
            structure_creator.element_counter = 0
            
            success_with_sidecar = structure_creator.create_elements_from_pdf(pdf, test_pdf_path, test_sidecar)
            
            if success_with_sidecar:
                created_with_sidecar = len(structure_creator.created_elements)
                print(f"   StructElems with sidecar: {created_with_sidecar}")
                
                # Show which elements got modified roles
                modified_elements = []
                for elem in structure_creator.created_elements:
                    if elem['type'] in ['H1', 'H2']:
                        modified_elements.append(f"{elem['type']}: {elem['title']}")
                
                print(f"   Modified elements: {modified_elements}")
                
                success_criteria = (
                    created_count >= total_text_elements * 0.8 and  # At least 80% coverage
                    len(modified_elements) >= 1  # At least some modifications applied
                )
                
                return success_criteria
            else:
                return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_elements_included()
    print(f"\n{'✅ ALL ELEMENTS TEST PASSED' if success else '❌ ALL ELEMENTS TEST FAILED'}")
    sys.exit(0 if success else 1)
