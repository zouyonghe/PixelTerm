#!/usr/bin/env python3
"""
PixelTerm 常量定义
"""

# 支持的图片格式
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}

# 预加载配置
DEFAULT_PRELOAD_SIZE = 10
PRELOAD_SLEEP_TIME = 0.05

# Chafa命令配置
CHAFA_CMD = 'chafa'
DEFAULT_CHAFA_ARGS = [
    '--color-space', 'rgb',
    '--dither', 'none',
    '--relative', 'off',
    '--optimize', '9',
    '--margin-right', '0',
    '--work', '9'
]

# 显示配置
DEFAULT_SCALE = 1.0
SCALE_STEP = 0.1
MIN_SCALE = 0.1
MAX_SCALE = 3.0

# 键盘控制
KEY_LEFT = '\x1b[D'
KEY_RIGHT = '\x1b[C'
KEY_LEFT_ALT = '\x1bOD'
KEY_RIGHT_ALT = '\x1bOC'
KEY_CTRL_C = '\x03'

# 错误消息
ERR_CHAFA_NOT_FOUND = "Error: chafa command not found"
ERR_CHAFA_INSTALL_HINT = "Please install chafa: brew install chafa (macOS) or sudo apt-get install chafa (Ubuntu)"
ERR_PATH_NOT_EXISTS = "Error: Path does not exist"
ERR_NOT_DIRECTORY = "Error: Not a directory"
ERR_NOT_FILE = "Error: Not a file"
ERR_UNSUPPORTED_FORMAT = "Error: Unsupported image format"