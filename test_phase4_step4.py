#!/usr/bin/env python3
"""
Test script for Phase 4 Step 4: Marked Content Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.structure_tree import StructureTreeCreator
import pikepdf

def test_phase4_step4():
    """Test Phase 4 Step 4: Marked Content Integration"""
    
    print("🧪 Testing Phase 4 Step 4: Marked Content Integration")
    
    # Use existing sample PDF
    test_pdf_path = "samples/sample_document.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Sample PDF not found: {test_pdf_path}")
        return False
    
    try:
        # Create structure creator
        structure_creator = StructureTreeCreator()
        
        # Create test sidecar data with some modifications
        test_sidecar = {
            'pages': {
                '0': {
                    'elements': [
                        {'id': 'text_0_0', 'role': 'Document', 'title': 'Main Document'},
                        {'id': 'text_0_1', 'role': 'H1', 'title': 'Chapter 1: Introduction'},
                        {'id': 'text_0_2', 'role': 'P', 'title': 'Introduction paragraph'},
                        {'id': 'text_0_3', 'role': 'H2', 'title': '1.1 Subheading'},
                        {'id': 'text_0_4', 'role': 'P', 'title': 'Content paragraph'},
                        {'id': 'text_0_5', 'role': 'Figure', 'title': 'Image placeholder'}
                    ]
                },
                '1': {
                    'elements': [
                        {'id': 'text_1_0', 'role': 'H1', 'title': 'Chapter 2'},
                        {'id': 'text_1_1', 'role': 'LI', 'title': 'List item 1'},
                        {'id': 'text_1_2', 'role': 'LI', 'title': 'List item 2'},
                        {'id': 'text_1_3', 'role': 'LI', 'title': 'List item 3'},
                        {'id': 'text_1_4', 'role': 'Caption', 'title': 'Table caption'},
                        {'id': 'text_1_5', 'role': 'TH', 'title': 'Table headers'},
                        {'id': 'text_1_6', 'role': 'TD', 'title': 'Table data 1'},
                        {'id': 'text_1_7', 'role': 'TD', 'title': 'Table data 2'}
                    ]
                }
            }
        }
        
        print(f"📁 Loading PDF: {test_pdf_path}")
        with pikepdf.open(test_pdf_path, allow_overwriting_input=True) as pdf:
            
            # Phase 4 Steps 1-3: Basic setup
            print("\n🏗️ Phase 4 Steps 1-3: Setting up structure...")
            
            # Create structure tree foundation
            if not structure_creator.create_basic_structure_tree(pdf):
                print("❌ Failed to create structure tree foundation")
                return False
            
            # Create elements from PDF with sidecar modifications
            if not structure_creator.create_elements_from_pdf(pdf, test_pdf_path, test_sidecar):
                print("❌ Failed to create elements")
                return False
            
            print(f"✅ Created {len(structure_creator.created_elements)} StructElems")
            
            # Phase 4 Step 4: Marked Content Integration
            print("\n🔗 Phase 4 Step 4: Marked Content Integration...")
            
            # Create element mappings
            element_mappings = {}
            for page_num, page_data in test_sidecar['pages'].items():
                for element in page_data['elements']:
                    element_mappings[element['id']] = {
                        'role': element['role'],
                        'title': element['title'],
                        'page': int(page_num),
                        'properties': element.get('properties', {})
                    }
            
            print(f"📋 Created {len(element_mappings)} element mappings")
            
            # Test 1: Inject marked content
            print("\n🔗 Test 1: Injecting marked content operators...")
            marked_content_success = structure_creator.inject_marked_content(
                pdf, test_pdf_path, element_mappings
            )
            
            if marked_content_success:
                print("✅ Marked content injection successful")
                
                # Test 2: Update StructElems with marked content references
                print("\n🔗 Test 2: Updating StructElems with marked content references...")
                struct_update_success = structure_creator.update_struct_elements_with_marked_content(pdf)
                
                if struct_update_success:
                    print("✅ StructElem updates successful")
                    
                    # Show final status
                    print("\n📊 Final Status:")
                    status = structure_creator.get_status_report(pdf)
                    print(status)
                    
                    summary = structure_creator.get_element_summary()
                    print(f"\n{summary}")
                    
                    # Show marked content summary
                    if structure_creator.marked_content_refs:
                        print(f"\n🔗 Marked Content References:")
                        for elem_id, mc_info in structure_creator.marked_content_refs.items():
                            print(f"   {elem_id} → MCID {mc_info['mcid']} ({mc_info['type']}) on page {mc_info['page']}")
                    
                    # Save test result
                    output_path = test_pdf_path.replace('.pdf', '_phase4_step4_test.pdf')
                    pdf.save(output_path)
                    print(f"\n💾 Phase 4 Step 4 test PDF saved to: {output_path}")
                    print("🔍 This PDF now has complete marked content integration!")
                    
                    return True
                else:
                    print("❌ StructElem updates failed")
                    return False
            else:
                print("❌ Marked content injection failed")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_marked_content_analysis():
    """Test marked content analysis capabilities"""
    
    print("\n🔍 Testing marked content analysis...")
    
    test_pdf_path = "samples/sample_document.pdf"
    
    try:
        import fitz
        
        with fitz.open(test_pdf_path) as doc:
            print(f"📄 Analyzing {doc.page_count} pages for text content...")
            
            total_text_items = 0
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                
                # Get detailed text information
                text_dict = page.get_text("dict")
                page_text_items = 0
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:  # Text block
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                if text:
                                    page_text_items += 1
                                    total_text_items += 1
                
                print(f"   Page {page_num}: {page_text_items} text spans")
            
            print(f"📊 Total text spans that could be marked: {total_text_items}")
            return True
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Phase 4 Step 4: Marked Content Integration Test Suite")
    print("=" * 60)
    
    # Test basic marked content functionality
    basic_success = test_phase4_step4()
    
    # Test content analysis
    analysis_success = test_marked_content_analysis()
    
    overall_success = basic_success and analysis_success
    
    print("\n" + "=" * 60)
    print(f"🎯 Phase 4 Step 4 Test Results:")
    print(f"   Marked Content Integration: {'✅' if basic_success else '❌'}")
    print(f"   Content Analysis: {'✅' if analysis_success else '❌'}")
    print(f"   Overall: {'🎉 PHASE 4 STEP 4 READY!' if overall_success else '🔧 NEEDS WORK'}")
    
    sys.exit(0 if overall_success else 1)
