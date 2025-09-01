#!/usr/bin/env python3
"""
Simple test to verify FastAPI backend setup
Phase 2 validation
"""
import sys
import os

# Add project root to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(backend_dir))
sys.path.append(project_root)

print(f"Backend dir: {backend_dir}")
print(f"Project root: {project_root}")
print(f"Python path includes: {project_root}")

try:
    from shared.pdf_engine import PDFAccessibilityEngine, FileManager
    print("✅ Successfully imported shared engine!")
    
    # Test engine creation
    engine = PDFAccessibilityEngine()
    print("✅ Engine created successfully!")
    
    # Test file manager
    temp_file = FileManager.create_temp_file()
    print(f"✅ Temp file created: {temp_file}")
    
    FileManager.cleanup_temp_files([temp_file])
    print("✅ Cleanup successful!")
    
    print("\n🎯 Phase 2 Backend Setup: ✅ READY")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    print("🔧 Debug info:")
    print(f"   Backend dir: {backend_dir}")
    print(f"   Project root: {project_root}")
    print(f"   Shared path: {os.path.join(project_root, 'shared')}")
    print(f"   Shared exists: {os.path.exists(os.path.join(project_root, 'shared'))}")
    
    import traceback
    traceback.print_exc()
