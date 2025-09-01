"""
Automated veraPDF Download and Setup
Downloads veraPDF automatically when the application starts
"""
import os
import sys
import urllib.request
import zipfile
import tempfile
import platform
import shutil
from pathlib import Path


class VeraPDFInstaller:
    """Handles automatic veraPDF download and installation"""
    
    def __init__(self):
        self.system = platform.system()
        self.app_dir = Path(__file__).parent.parent
        self.verapdf_dir = self.app_dir / "verapdf"
        
    def get_download_info(self):
        """Get download URL and filename for current platform"""
        version = "1.25.145"
        
        if self.system == "Darwin":  # macOS
            return {
                "url": f"https://github.com/veraPDF/veraPDF-apps/releases/download/v{version}/veraPDF-installer-mac-{version}.zip",
                "filename": f"veraPDF-installer-mac-{version}.zip",
                "executable": "veraPDF"
            }
        elif self.system == "Windows":
            return {
                "url": f"https://github.com/veraPDF/veraPDF-apps/releases/download/v{version}/veraPDF-installer-win-{version}.zip", 
                "filename": f"veraPDF-installer-win-{version}.zip",
                "executable": "veraPDF.exe"
            }
        else:  # Linux
            return {
                "url": f"https://github.com/veraPDF/veraPDF-apps/releases/download/v{version}/veraPDF-installer-linux-{version}.zip",
                "filename": f"veraPDF-installer-linux-{version}.zip", 
                "executable": "veraPDF"
            }
    
    def is_installed(self) -> bool:
        """Check if veraPDF is already available"""
        download_info = self.get_download_info()
        verapdf_path = self.verapdf_dir / download_info["executable"]
        return verapdf_path.exists() and verapdf_path.is_file()
    
    def install(self, progress_callback=None) -> bool:
        """Download and install veraPDF"""
        try:
            download_info = self.get_download_info()
            
            # Create verapdf directory
            self.verapdf_dir.mkdir(exist_ok=True)
            
            # Download veraPDF
            if progress_callback:
                progress_callback("Downloading veraPDF...")
                
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_path = temp_path / download_info["filename"]
                
                # Download
                urllib.request.urlretrieve(download_info["url"], zip_path)
                
                if progress_callback:
                    progress_callback("Extracting veraPDF...")
                
                # Extract
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find and copy veraPDF executable
                self._extract_executable(temp_path, download_info["executable"])
                
                if progress_callback:
                    progress_callback("Installation complete!")
                
                return True
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"Installation failed: {str(e)}")
            return False
    
    def _extract_executable(self, extract_path: Path, executable_name: str):
        """Find and copy the veraPDF executable from extracted files"""
        # Search for veraPDF executable in extracted files
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file == executable_name or file.startswith("veraPDF"):
                    source = Path(root) / file
                    if source.is_file() and os.access(source, os.X_OK):
                        destination = self.verapdf_dir / executable_name
                        shutil.copy2(source, destination)
                        os.chmod(destination, 0o755)  # Make executable
                        return
        
        # If not found, look for batch/shell scripts
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if "verapdf" in file.lower() and (file.endswith(".sh") or file.endswith(".bat")):
                    source = Path(root) / file
                    destination = self.verapdf_dir / executable_name
                    shutil.copy2(source, destination)
                    os.chmod(destination, 0o755)
                    return
    
    def get_executable_path(self) -> Path:
        """Get path to veraPDF executable"""
        download_info = self.get_download_info()
        return self.verapdf_dir / download_info["executable"]


# Auto-install on import (optional)
def auto_install_verapdf():
    """Automatically install veraPDF if not present"""
    installer = VeraPDFInstaller()
    if not installer.is_installed():
        print("veraPDF not found. Downloading...")
        success = installer.install(print)
        if success:
            print("veraPDF installed successfully!")
        else:
            print("Failed to install veraPDF automatically.")
    return installer.get_executable_path() if installer.is_installed() else None


if __name__ == "__main__":
    # Test installation
    installer = VeraPDFInstaller()
    if not installer.is_installed():
        print("Installing veraPDF...")
        installer.install(print)
    else:
        print("veraPDF already installed!")
    
    print(f"veraPDF path: {installer.get_executable_path()}")
