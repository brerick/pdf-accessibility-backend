#!/usr/bin/env python3
"""
Test script for Phase 4 Step 3: Multiple Element Types & Batch Operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.structure_tree import StructureTreeCreator
import pikepdf

def test_phase4_step3():
    """Test Phase 4 Step 3 features"""
    
    print("🧪 Testing Phase 4 Step 3: Multiple Element Types & Batch Operations")
    
    # Create structure creator
    structure_creator = StructureTreeCreator()
    
    # Use existing sample PDF
    test_pdf_path = "samples/sample_document.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Sample PDF not found: {test_pdf_path}")
        return False
    
    try:
        # Load PDF with pikepdf
        print(f"📁 Loading PDF: {test_pdf_path}")
        with pikepdf.open(test_pdf_path) as pdf:
            
            # Create structure tree foundation
            print("🏗️ Creating structure tree foundation...")
            if not structure_creator.create_basic_structure_tree(pdf):
                print("❌ Failed to create structure tree foundation")
                return False
            
            # Test 1: Batch element creation
            print("\n🔄 Test 1: Batch Element Creation")
            batch_specs = [
                {'type': 'Document', 'title': 'Test Document'},
                {'type': 'H1', 'title': 'Chapter 1: Introduction'},
                {'type': 'P', 'title': 'Opening paragraph'},
                {'type': 'H2', 'title': 'Section 1.1: Overview'},
                {'type': 'P', 'title': 'Section content'},
                {'type': 'Figure', 'title': 'Diagram 1', 'alt_text': 'Process flow diagram'},
                {'type': 'Caption', 'title': 'Figure caption'},
            ]
            
            batch_results = structure_creator.create_batch_elements(pdf, batch_specs)
            batch_success = len([r for r in batch_results if r]) == len(batch_specs)
            print(f"   Result: {'✅ PASSED' if batch_success else '❌ FAILED'}")
            
            # Test 2: Table structure creation
            print("\n📊 Test 2: Table Structure Creation")
            table_spec = {
                'title': 'Employee Data',
                'rows': 4,
                'cols': 4,
                'headers': ['ID', 'Name', 'Department', 'Salary'],
                'has_header_row': True
            }
            
            table_result = structure_creator.create_table_structure(pdf, table_spec)
            table_success = table_result is not None
            print(f"   Result: {'✅ PASSED' if table_success else '❌ FAILED'}")
            
            # Test 3: List structure creation (ordered)
            print("\n📝 Test 3: Ordered List Creation")
            ordered_list_spec = {
                'title': 'Steps to Success',
                'items': [
                    'Plan your approach',
                    'Execute with precision',
                    'Monitor progress',
                    'Adjust as needed',
                    'Celebrate achievements'
                ],
                'list_type': 'ordered'
            }
            
            ordered_list_result = structure_creator.create_list_structure(pdf, ordered_list_spec)
            ordered_list_success = ordered_list_result is not None
            print(f"   Result: {'✅ PASSED' if ordered_list_success else '❌ FAILED'}")
            
            # Test 4: List structure creation (unordered)
            print("\n📝 Test 4: Unordered List Creation")
            unordered_list_spec = {
                'title': 'Key Features',
                'items': [
                    'User-friendly interface',
                    'High performance',
                    'Secure architecture',
                    'Scalable design'
                ],
                'list_type': 'unordered'
            }
            
            unordered_list_result = structure_creator.create_list_structure(pdf, unordered_list_spec)
            unordered_list_success = unordered_list_result is not None
            print(f"   Result: {'✅ PASSED' if unordered_list_success else '❌ FAILED'}")
            
            # Test 5: Complex element types
            print("\n🔧 Test 5: Complex Element Types")
            complex_specs = [
                {'type': 'BlockQuote', 'title': 'Important Quote', 'actual_text': 'Success is not final, failure is not fatal.'},
                {'type': 'Code', 'title': 'Code Example', 'actual_text': 'function example() { return true; }'},
                {'type': 'Formula', 'title': 'Mathematical Formula', 'actual_text': 'E = mc²'},
                {'type': 'Note', 'title': 'Footnote', 'actual_text': 'Additional information here'},
                {'type': 'Reference', 'title': 'Citation', 'actual_text': 'Smith, J. (2025). Example Paper.'},
            ]
            
            complex_results = structure_creator.create_batch_elements(pdf, complex_specs)
            complex_success = len([r for r in complex_results if r]) == len(complex_specs)
            print(f"   Result: {'✅ PASSED' if complex_success else '❌ FAILED'}")
            
            # Get final status
            print("\n📊 Final Structure Tree Status:")
            status = structure_creator.get_status_report(pdf)
            print(status)
            
            summary = structure_creator.get_element_summary()
            print(f"\n📋 Elements Summary:")
            print(summary)
            
            # Calculate overall success
            all_tests = [batch_success, table_success, ordered_list_success, unordered_list_success, complex_success]
            overall_success = all(all_tests)
            
            print(f"\n🎯 Phase 4 Step 3 Test Results:")
            print(f"   Batch Elements: {'✅' if batch_success else '❌'}")
            print(f"   Table Structure: {'✅' if table_success else '❌'}")
            print(f"   Ordered List: {'✅' if ordered_list_success else '❌'}")
            print(f"   Unordered List: {'✅' if unordered_list_success else '❌'}")
            print(f"   Complex Elements: {'✅' if complex_success else '❌'}")
            print(f"   Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
            
            return overall_success
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase4_step3()
    print(f"\n{'🎉 Phase 4 Step 3 READY' if success else '🔧 Phase 4 Step 3 NEEDS WORK'}")
    sys.exit(0 if success else 1)
