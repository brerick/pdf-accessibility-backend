#!/bin/bash
# Complete Installation Script for PDF Accessibility Tool

set -e

echo "🚀 Installing PDF Accessibility Tool..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_DIR="$HOME/Applications/PDFAccessibilityTool"

# Create installation directory
mkdir -p "$INSTALL_DIR"

echo "📁 Creating installation directory: $INSTALL_DIR"

# Copy application files
echo "📋 Copying application files..."
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

# Install Python dependencies if needed
if command -v python3 &> /dev/null; then
    echo "🐍 Installing Python dependencies..."
    cd "$INSTALL_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "⚠️  Python 3 not found. Please install Python 3 first."
    exit 1
fi

# Install Java if needed
echo "☕ Checking Java installation..."
if ! command -v java &> /dev/null; then
    echo "📥 Installing Java 11..."
    if command -v brew &> /dev/null; then
        brew install openjdk@11
        echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
        export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
    else
        echo "⚠️  Homebrew not found. Please install Java manually:"
        echo "   Visit: https://adoptium.net/temurin/releases/"
        read -p "Press Enter after installing Java..."
    fi
else
    echo "✅ Java already installed: $(java -version 2>&1 | head -1)"
fi

# Install veraPDF
echo "🔧 Installing veraPDF..."

# Check if veraPDF is already installed
if command -v veraPDF &> /dev/null; then
    echo "✅ veraPDF already installed"
else
    # Download and install veraPDF
    VERAPDF_VERSION="1.25.145"
    TEMP_DIR=$(mktemp -d)
    
    echo "📥 Downloading veraPDF..."
    curl -L -o "$TEMP_DIR/verapdf.zip" \
        "https://github.com/veraPDF/veraPDF-apps/releases/download/v${VERAPDF_VERSION}/veraPDF-installer-mac-${VERAPDF_VERSION}.zip"
    
    cd "$TEMP_DIR"
    unzip -q verapdf.zip
    
    # Mount DMG and install
    hdiutil attach "veraPDF-installer-mac-${VERAPDF_VERSION}.dmg" -quiet
    
    # Copy veraPDF to Applications
    cp -r "/Volumes/veraPDF ${VERAPDF_VERSION}/veraPDF.app" /Applications/
    
    # Unmount DMG
    hdiutil detach "/Volumes/veraPDF ${VERAPDF_VERSION}" -quiet
    
    # Create symlink
    sudo ln -sf "/Applications/veraPDF.app/Contents/MacOS/veraPDF" /usr/local/bin/veraPDF
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    echo "✅ veraPDF installed successfully"
fi

# Create desktop shortcut
echo "🖥️  Creating desktop shortcut..."
cat > "$HOME/Desktop/PDF Accessibility Tool.command" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python app.py
EOF

chmod +x "$HOME/Desktop/PDF Accessibility Tool.command"

# Create Applications menu entry (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    cat > "$HOME/Applications/PDF Accessibility Tool.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch.sh</string>
    <key>CFBundleName</key>
    <string>PDF Accessibility Tool</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.pdfaccessibility</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

    mkdir -p "$HOME/Applications/PDF Accessibility Tool.app/Contents/MacOS"
    cat > "$HOME/Applications/PDF Accessibility Tool.app/Contents/MacOS/launch.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python app.py
EOF
    chmod +x "$HOME/Applications/PDF Accessibility Tool.app/Contents/MacOS/launch.sh"
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📍 Installation Location: $INSTALL_DIR"
echo "🚀 Launch from: Desktop shortcut or Applications folder"
echo "📚 Documentation: $INSTALL_DIR/docs/"
echo ""
echo "To uninstall: rm -rf '$INSTALL_DIR'"
echo ""
