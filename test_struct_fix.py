#!/usr/bin/env python3
"""
Test script to verify StructElem creation fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.structure_tree import StructureTreeCreator
import pikepdf

def test_struct_elem_creation():
    """Test creating StructElems with the fixed code"""
    
    print("🧪 Testing StructElem creation...")
    
    # Create structure creator
    structure_creator = StructureTreeCreator()
    
    # Look for sample files
    sample_files = [
        "samples/sample_document.pdf",
        "test_simple.pdf"
    ]
    
    test_pdf_path = None
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            test_pdf_path = sample_file
            break
    
    if not test_pdf_path:
        print("❌ No sample PDF found for testing")
        print("   Creating a simple test PDF...")
        
        # Create a simple test PDF for testing
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            test_pdf_path = "test_simple.pdf"
            c = canvas.Canvas(test_pdf_path, pagesize=letter)
            c.drawString(100, 750, "Test Document")
            c.drawString(100, 700, "This is a test paragraph.")
            c.save()
            
            print(f"✅ Created test PDF: {test_pdf_path}")
        except ImportError:
            print("❌ Cannot create test PDF (reportlab not available)")
            return False
    
    try:
        # Load PDF with pikepdf
        print(f"📁 Loading PDF: {test_pdf_path}")
        with pikepdf.open(test_pdf_path) as pdf:
            
            # Create structure tree foundation (Phase 4 Step 1)
            print("🏗️ Creating structure tree foundation...")
            if not structure_creator.create_basic_structure_tree(pdf):
                print("❌ Failed to create structure tree foundation")
                return False
            
            # Test creating individual StructElems (Phase 4 Step 2)
            print("📝 Testing StructElem creation...")
            
            test_elements = [
                {'type': 'H1', 'title': 'Test Heading 1'},
                {'type': 'P', 'title': 'Test Paragraph'},
                {'type': 'Figure', 'alt_text': 'Test Figure'},
                {'type': 'H2', 'title': 'Test Heading 2'},
            ]
            
            created_count = 0
            for elem in test_elements:
                print(f"   Creating {elem['type']}...")
                struct_elem = structure_creator.create_struct_elem(
                    pdf, 
                    elem['type'],
                    title=elem.get('title'),
                    alt_text=elem.get('alt_text')
                )
                
                if struct_elem:
                    created_count += 1
                    print(f"   ✅ {elem['type']} created successfully")
                else:
                    print(f"   ❌ {elem['type']} creation failed")
            
            # Test with sample sidecar data
            print("\n🗂️ Testing with sample sidecar data...")
            sample_sidecar = {
                'pages': {
                    '0': {
                        'elements': [
                            {'id': 'text_0_1', 'role': 'H1', 'title': 'Sample Heading'},
                            {'id': 'text_0_2', 'role': 'P', 'title': 'Sample Paragraph'}
                        ]
                    }
                }
            }
            
            if structure_creator.create_sample_elements(pdf, sample_sidecar):
                print("✅ Sample elements created successfully")
            else:
                print("❌ Sample elements creation failed")
            
            # Get status report
            print("\n📊 Final Status:")
            status = structure_creator.get_status_report(pdf)
            print(status)
            
            summary = structure_creator.get_element_summary()
            print(f"\n📋 Elements Summary:")
            print(summary)
            
            print(f"\n🎯 Test Results: Created {created_count}/{len(test_elements)} individual elements")
            return created_count > 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_struct_elem_creation()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
    sys.exit(0 if success else 1)
