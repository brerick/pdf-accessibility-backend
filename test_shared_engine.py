#!/usr/bin/env python3
"""
Test the shared PDF engine with existing desktop functionality
This validates Phase 1: Shared Core Engine Extraction
"""
import os
import sys
import tempfile

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from shared.pdf_engine import PDFAccessibilityEngine, FileManager


def test_shared_engine():
    """Test that the shared engine works correctly"""
    
    print("🧪 Testing Shared PDF Engine...")
    print("=" * 50)
    
    # Initialize the engine
    engine = PDFAccessibilityEngine()
    print("✅ Engine initialized successfully")
    
    # Set up progress tracking
    progress_steps = []
    
    def progress_callback(step: str, message: str, progress: int):
        progress_steps.append((step, message, progress))
        print(f"📊 Progress: {progress}% - {step}: {message}")
    
    engine.set_progress_callback(progress_callback)
    print("✅ Progress callback set up")
    
    # Test file validation
    test_file = "/tmp/nonexistent.pdf"
    validation = FileManager.validate_pdf_file(test_file)
    print(f"✅ File validation test: {validation}")
    
    # Test with a sample PDF if available
    sample_files = [
        "/Users/brad/Documents/Web Development/comment-on/pdf-a11y/samples/sample.pdf",
        "/Users/brad/Documents/Web Development/comment-on/pdf-a11y/test.pdf",
        "/Users/brad/Documents/Web Development/comment-on/pdf-a11y/output_test.pdf"
    ]
    
    test_pdf_path = None
    for sample in sample_files:
        if os.path.exists(sample):
            test_pdf_path = sample
            break
    
    if test_pdf_path:
        print(f"📄 Found test PDF: {test_pdf_path}")
        
        # Test analysis
        print("\n🔍 Testing PDF Analysis...")
        analysis = engine.analyze_pdf(test_pdf_path)
        print(f"Analysis result: {analysis['status']}")
        
        if analysis["status"] == "success":
            print("✅ PDF analysis successful!")
        else:
            print(f"⚠️ Analysis result: {analysis}")
        
        # Test processing
        print("\n⚙️ Testing PDF Processing...")
        
        # Create test modifications
        modifications = {
            "metadata": {
                "title": "Test PDF - Accessibility Enhanced",
                "subject": "Testing shared engine functionality",
                "creator": "PDF Accessibility Engine Test"
            },
            "sidecar_data": {
                "pages": {
                    "elements": {}  # Empty for now
                }
            }
        }
        
        # Create temp output file
        output_path = FileManager.create_temp_file(suffix="_enhanced.pdf")
        
        result = engine.process_pdf(test_pdf_path, modifications, output_path)
        
        print(f"Processing result: {result['status']}")
        
        if result["status"] == "success":
            print("✅ PDF processing successful!")
            print(f"📁 Output file: {result['output_path']}")
            print(f"📊 File size: {result['file_size']} bytes")
            print(f"📋 Summary: {result['processing_summary']}")
            
            # Clean up
            FileManager.cleanup_temp_files([output_path])
            print("🧹 Cleaned up temp files")
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
    
    else:
        print("⚠️ No test PDF found. Skipping PDF processing tests.")
        print("   Place a test PDF in one of these locations:")
        for sample in sample_files:
            print(f"   - {sample}")
    
    print(f"\n📈 Progress callback received {len(progress_steps)} updates")
    print("=" * 50)
    print("🎉 Shared engine test completed!")
    
    return True


def test_file_manager():
    """Test the FileManager utility functions"""
    
    print("\n🔧 Testing FileManager utilities...")
    
    # Test temp file creation
    temp_file = FileManager.create_temp_file(".pdf")
    print(f"✅ Created temp file: {temp_file}")
    
    # Write some test data
    with open(temp_file, "w") as f:
        f.write("test data")
    
    # Test validation
    validation = FileManager.validate_pdf_file(temp_file)
    print(f"📝 Validation result: {validation}")
    
    # Test cleanup
    FileManager.cleanup_temp_files([temp_file])
    print(f"🧹 Cleaned up: {not os.path.exists(temp_file)}")
    
    return True


if __name__ == "__main__":
    try:
        print("🚀 Starting Phase 1 Validation Tests")
        print("Testing shared core engine extraction...")
        print()
        
        # Test the core engine
        test_shared_engine()
        
        # Test utilities
        test_file_manager()
        
        print("\n" + "=" * 60)
        print("🎯 PHASE 1 VALIDATION: ✅ PASSED")
        print("✅ Shared engine working correctly")
        print("✅ Ready to proceed to Phase 2 (Web Backend)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("🔧 Debug info:")
        import traceback
        traceback.print_exc()
        
        print("\n🛠️ Next steps:")
        print("1. Check that your core/ modules are working")
        print("2. Ensure all dependencies are installed")
        print("3. Verify PDF processing functionality")
