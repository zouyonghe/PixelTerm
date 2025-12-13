# PixelTerm - 终端图片浏览器

*English | [中文](README_zh.md)*

> **⚠️ 实验性项目警告**: 此项目目前仅作为试验性项目维护，主要功能开发已集中在 [PixelTerm-C](https://github.com/zouyonghe/PixelTerm-C) 项目中。建议用户优先使用 C 语言版本以获得更好的性能和稳定性。

一个基于chafa的现代化终端图片浏览器，支持在终端中浏览和查看图片。

> **⚡️ 追求更好性能？** 试试 [PixelTerm-C](https://github.com/zouyonghe/PixelTerm-C) - 原生 C 实现，图片处理速度显著更快，内存占用更低！**这是当前主要的开发重点。**

## 🌟 功能特性

- 🖼️ **多格式支持** - 支持JPG、PNG、GIF、BMP、WebP、TIFF等主流图片格式
- 📁 **智能浏览** - 自动检测目录中的图片文件，支持目录导航
- ⌨️ **键盘导航** - 左右键切换图片，支持多种终端环境
- 📏 **自适应显示** - 自动适配终端大小变化
- 🎨️ **极简界面** - 无冗余信息，专注图片浏览体验
- ⚡️ **高分辨率** - 自动选择最佳显示协议，支持sixel/iterm/kitty等
- 🔄 **自动刷新** - 终端大小改变时自动重新绘制

## 🚀 快速开始

### 安装依赖

```bash
# 1. 安装系统chafa库 (必须)
# Arch Linux
sudo pacman -S chafa

# Ubuntu/Debian  
sudo apt-get install chafa

# macOS
brew install chafa

# 2. 安装Python依赖
pip install -r requirements.txt
```

**依赖说明**:
- **系统chafa**: 必须先安装系统的chafa库，这是核心依赖
- **Python依赖**: 通过requirements.txt安装Pillow等Python包

### 基本使用

```bash
# 浏览当前目录的图片
python pixelterm.py

# 浏览指定目录的图片
python pixelterm.py /path/to/images

# 显示指定图片
python pixelterm.py image.jpg

# 禁用预加载功能（更快启动）
python pixelterm.py --no-preload

# 或者直接运行
./pixelterm.py /path/to/images
```

## 🎮 控制说明

| 按键 | 功能 |
|------|------|
| ←/→ | 上一张/下一张图片 |
| a/d  | 备用左/右键（兼容模式）|
| i    | 显示/隐藏图片信息 |
| r    | 删除当前图片 |
| q    | 退出程序 |
| Ctrl+C | 强制退出 |

## 📁 目录导航

- **自动扫描** - 启动时自动扫描当前目录的所有图片文件
- **智能排序** - 按文件名排序，便于浏览
- **循环切换** - 到达最后一张后自动回到第一张
- **文件支持** - 支持直接指定图片文件或目录

## ⚙️ 高级特性

### 显示协议支持
- **自动检测** - 自动选择最佳显示协议：
  - iTerm2/iTerm3 (最高分辨率)
  - Kitty (高分辨率)
  - Sixels (中等分辨率)  
  - Symbols (通用兼容)

### 终端适配
- **实时响应** - 终端窗口大小改变时自动重绘
- **尺寸优化** - 智能计算最佳显示尺寸
- **光标管理** - 浏览时隐藏光标，退出时恢复

### 性能优化
- **内存缓存** - 图片列表预加载，避免重复扫描
- **流式处理** - 高效的按键序列处理
- **快速响应** - 优化的输入处理逻辑
- **预加载功能** - 可选的图片预加载，提升浏览体验（可用--no-preload禁用）
- **配置系统** - 支持自定义配置文件 `~/.pixelterm/config.json`，可配置缩放比例、显示参数、界面选项和导航设置
- **图片管理** - 按i键显示图片详细信息，按r键删除当前图片（带确认提示），支持JPG、PNG、GIF、BMP、WebP、TIFF等主流格式

## 🔧 技术实现

### 核心架构
```
PixelTerm/
├── 🖼️ 图片显示 (image_viewer.py)
├── 📁 文件浏览 (file_browser.py)  
├── 🎮️ 用户界面 (interface.py)
├── ⚙️ 配置管理 (config.py)
├── 🔧 Chafa封装 (chafa_wrapper.py)
├── ❌ 异常处理 (exceptions.py)
├── 🔢 常量定义 (constants.py)
└── 🚀 主程序 (pixelterm.py)
```

### 关键技术
- **ESC键序列处理** - 正确组合终端箭头键序列
- **缓冲区管理** - 智能积累和处理按键输入
- **协议自动选择** - 根据终端能力选择最佳显示方式
- **状态同步** - 文件列表与显示状态实时同步
- **配置系统** - 支持用户自定义配置文件 (~/.pixelterm/config.json)
- **异常处理** - 完善的错误处理和用户提示
- **文件管理** - 支持图片删除和文件操作

## 📦 项目信息

- **开发语言**: Python 3.7+
- **核心依赖**: chafa, Pillow
- **代码规模**: 多个模块，结构化设计
- **开源协议**: LGPL-3.0 或更高版本
- **仓库地址**: https://github.com/zouyonghe/PixelTerm
- **安装方式**: 
  - 通过pip: `pip install pixelterm`
  - 从源码: `git clone https://github.com/zouyonghe/PixelTerm && cd PixelTerm && pip install -e .`

## 🎯 设计理念

- **极简主义** - 专注核心功能，去除冗余信息
- **用户友好** - 直观的操作方式，无学习成本
- **性能优先** - 快速响应，流畅体验
- **兼容性强** - 支持多种终端环境

## 🔧 使用提示

**常见问题**:
- 提示"chafa command not found": 需先安装系统chafa库（Ubuntu: `sudo apt-get install chafa`, Arch: `sudo pacman -S chafa`, macOS: `brew install chafa`）
- 图片显示不清晰: 调整终端窗口大小，程序会自动选择最佳显示协议
- 某些按键不响应: 尝试使用备用按键（a/d代替左右箭头）
- 启动速度慢: 使用`--no-preload`参数禁用预加载功能

**配置文件**: 可创建`~/.pixelterm/config.json`自定义显示设置、界面选项和导航参数

## 📄 许可证

LGPL-3.0 或更高版本 - 详见 LICENSE 文件

本项目采用与 Chafa 相同的许可证 (LGPLv3+)。

---

**PixelTerm** - 让终端也能成为出色的图片浏览器！ 🖼️