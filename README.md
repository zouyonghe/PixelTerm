# PixelTerm - Terminal Image Viewer

*English | [中文](README_zh.md)*

> **⚠️ Experimental Project Warning**: This project is currently maintained as an experimental project only. Main feature development has been concentrated in the [PixelTerm-C](https://github.com/zouyonghe/PixelTerm-C) project. Users are recommended to prioritize the C language version for better performance and stability.

A modern terminal image viewer based on chafa, allowing you to browse and view images directly in your terminal.

> **⚡️ Looking for better performance?** Check out [PixelTerm-C](https://github.com/zouyonghe/PixelTerm-C) - a native C implementation with significantly faster image processing and lower memory usage! **This is now the primary focus of development.**

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

# Display specific image
python pixelterm.py image.jpg

# Disable preloading for faster startup
python pixelterm.py --no-preload

# Or run directly
./pixelterm.py /path/to/images
```

## 🎮 Controls

| Key | Function |
|-----|----------|
| ←/→ | Previous/Next image |
| a/d | Alternative left/right keys (compatibility mode) |
| i   | Show/hide image information |
| r   | Delete current image |
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
- **Preloading Feature** - Optional image preloading for better browsing experience (can be disabled with --no-preload)
- **Configuration System** - Supports custom configuration files `~/.pixelterm/config.json` with configurable display settings, chafa parameters, interface options and navigation settings
- **Image Management** - Press 'i' to show detailed image information, press 'r' to delete current image (with confirmation prompt), supports JPG, PNG, GIF, BMP, WebP, TIFF and other mainstream formats

## 🔧 Technical Implementation

### Core Architecture
```
PixelTerm/
├── 🖼️ Image Display (image_viewer.py)
├── 📁 File Browser (file_browser.py)  
├── 🎮️ User Interface (interface.py)
├── ⚙️ Configuration (config.py)
├── 🔧 Chafa Wrapper (chafa_wrapper.py)
├── ❌ Exception Handling (exceptions.py)
├── 🔢 Constants (constants.py)
└── 🚀 Main Program (pixelterm.py)
```

### Key Technologies
- **ESC Key Sequence Processing** - Correctly combines terminal arrow key sequences
- **Buffer Management** - Intelligently accumulates and processes key input
- **Protocol Auto Selection** - Selects optimal display method based on terminal capabilities
- **State Synchronization** - Real-time synchronization between file list and display state
- **Configuration System** - Supports user custom configuration files (~/.pixelterm/config.json)
- **Exception Handling** - Comprehensive error handling and user prompts
- **File Management** - Supports image deletion and file operations

## 📦 Project Information

- **Language**: Python 3.7+
- **Core Dependencies**: chafa, Pillow
- **Code Scale**: Multiple modules with structured design
- **License**: LGPL-3.0 or later
- **Repository**: https://github.com/zouyonghe/PixelTerm
- **Installation**: 
  - Via pip: `pip install pixelterm`
  - From source: `git clone https://github.com/zouyonghe/PixelTerm && cd PixelTerm && pip install -e .`

## 🎯 Design Philosophy

- **Minimalism** - Focus on core functionality, remove redundant information
- **User Friendly** - Intuitive operation with no learning curve
- **Performance First** - Fast response and smooth experience
- **Strong Compatibility** - Support for various terminal environments

## 🔧 Usage Tips

**Common Issues**:
- "chafa command not found": Install system chafa library (Ubuntu: `sudo apt-get install chafa`, Arch: `sudo pacman -S chafa`, macOS: `brew install chafa`)
- Image display is not clear: Adjust terminal window size for optimal display protocol selection
- Some keys don't respond: Try alternative keys (a/d instead of arrow keys)
- Slow startup: Use `--no-preload` parameter to disable preloading feature

**Configuration**: Create `~/.pixelterm/config.json` to customize display settings, interface options and navigation parameters

## 📄 License

LGPL-3.0 or later - See LICENSE file for details

This project is licensed under the same license as Chafa (LGPLv3+).

---

**PixelTerm** - Making terminals excellent image viewers! 🖼️