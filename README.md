# PixelTerm - Terminal Image Viewer

*English | [中文](README_zh.md)*

A modern terminal image viewer based on chafa, allowing you to browse and view images directly in your terminal.

> **⚡️ Looking for better performance?** Check out [PixelTerm-C](https://github.com/zouyonghe/PixelTerm-C) - a native C implementation with significantly faster image processing and lower memory usage!

## 🌟 Features

- 🖼️ **Multi-format Support** - Supports JPG, PNG, GIF, BMP, WebP, TIFF and other mainstream image formats
- 📁 **Smart Browsing** - Automatically detects image files in directories with directory navigation support
- ⌨️ **Keyboard Navigation** - Switch between images with arrow keys, supporting various terminal environments
- 📏 **Adaptive Display** - Automatically adapts to terminal size changes
- 🎨️ **Minimal Interface** - No redundant information, focused on image browsing experience
- ⚡️ **High Resolution** - Automatically selects optimal display protocols, supporting sixel/iterm/kitty and more
- 🔄 **Auto Refresh** - Automatically redraws when terminal size changes

## 🚀 Quick Start

### Install Dependencies

```bash
# 1. Install system chafa library (required)
# Arch Linux
sudo pacman -S chafa

# Ubuntu/Debian  
sudo apt-get install chafa

# macOS
brew install chafa

# 2. Install Python dependencies
pip install -r requirements.txt
```

**Dependency Notes**:
- **System chafa**: Must install the system chafa library first, this is the core dependency
- **Python dependencies**: Install Pillow and other Python packages via requirements.txt

### Basic Usage

```bash
# Browse images in current directory
python pixelterm.py

# Browse images in specified directory
python pixelterm.py /path/to/images

# Or run directly
./pixelterm.py /path/to/images
```

## 🎮 Controls

| Key | Function |
|-----|----------|
| ←/→ | Previous/Next image |
| a/d | Alternative left/right keys (compatibility mode) |
| q   | Exit program |
| Ctrl+C | Force exit |

## 📁 Directory Navigation

- **Auto Scan** - Automatically scans all image files in current directory on startup
- **Smart Sorting** - Sorts by filename for easy browsing
- **Loop Navigation** - Automatically returns to first image after reaching the last one
- **File Support** - Supports specifying image files or directories directly

## ⚙️ Advanced Features

### Display Protocol Support
- **Auto Detection** - Automatically selects optimal display protocol:
  - iTerm2/iTerm3 (highest resolution)
  - Kitty (high resolution)
  - Sixels (medium resolution)  
  - Symbols (universal compatibility)

### Terminal Adaptation
- **Real-time Response** - Automatically redraws when terminal window size changes
- **Size Optimization** - Intelligently calculates optimal display size
- **Cursor Management** - Hides cursor during browsing, restores on exit

### Performance Optimization
- **Memory Cache** - Preloads image list to avoid repeated scanning
- **Stream Processing** - Efficient key sequence processing
- **Fast Response** - Optimized input processing logic

## 🔧 Technical Implementation

### Core Architecture
```
PixelTerm/
├── 🖼️ Image Display (image_viewer.py)
├── 📁 File Browser (file_browser.py)  
├── 🎮️ User Interface (interface.py)
├── ⚙️ Configuration (config.py)
└── 🚀 Main Program (pixelterm.py)
```

### Key Technologies
- **ESC Key Sequence Processing** - Correctly combines terminal arrow key sequences
- **Buffer Management** - Intelligently accumulates and processes key input
- **Protocol Auto Selection** - Selects optimal display method based on terminal capabilities
- **State Synchronization** - Real-time synchronization between file list and display state

## 📦 Project Information

- **Language**: Python 3.7+
- **Core Dependencies**: chafa, Pillow
- **Code Scale**: 14 files, 1000+ lines of code
- **License**: MIT License
- **Repository**: https://github.com/zouyonghe/PixelTerm

## 🔗 Related Projects

### PixelTerm-C
A C implementation of PixelTerm with better performance and lower resource usage. 

- **Repository**: https://github.com/zouyonghe/PixelTerm-C
- **Features**: Native C implementation, faster image processing, smaller memory footprint
- **Ideal for**: Systems with limited resources or users seeking maximum performance

## 🎯 Design Philosophy

- **Minimalism** - Focus on core functionality, remove redundant information
- **User Friendly** - Intuitive operation with no learning curve
- **Performance First** - Fast response and smooth experience
- **Strong Compatibility** - Support for various terminal environments

## 📄 License

MIT License - See LICENSE file for details

---

**PixelTerm** - Making terminals excellent image viewers! 🖼️