#!/bin/bash
# veraPDF Installation Script for macOS

echo "Installing veraPDF for PDF/UA validation..."

# Create applications directory if it doesn't exist
mkdir -p ~/Applications

# Download veraPDF (adjust version as needed)
VERAPDF_VERSION="1.25.145"
DOWNLOAD_URL="https://github.com/veraPDF/veraPDF-apps/releases/download/v${VERAPDF_VERSION}/veraPDF-installer-mac-${VERAPDF_VERSION}.zip"

echo "Downloading veraPDF installer..."
curl -L -o ~/Downloads/veraPDF-installer.zip "$DOWNLOAD_URL"

if [ $? -eq 0 ]; then
    echo "Downloaded veraPDF installer successfully"
    
    # Extract the installer
    cd ~/Downloads
    unzip -o veraPDF-installer.zip
    
    # Run the installer (this may require manual interaction)
    echo "Please run the veraPDF installer manually:"
    echo "1. Open ~/Downloads/veraPDF-installer-mac-${VERAPDF_VERSION}.dmg"
    echo "2. Drag veraPDF to your Applications folder"
    echo "3. Add veraPDF to your PATH or create a symlink:"
    echo "   sudo ln -s /Applications/veraPDF/verapdf /usr/local/bin/veraPDF"
    
    open ~/Downloads/veraPDF-installer-mac-${VERAPDF_VERSION}.dmg
else
    echo "Failed to download veraPDF installer"
    echo "Please download manually from: https://verapdf.org/home/"
fi

echo "After installation, restart the PDF accessibility tool."
