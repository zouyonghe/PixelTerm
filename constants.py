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
ERR_CHAFA_NOT_FOUND = "错误: 未找到chafa命令"
ERR_CHAFA_INSTALL_HINT = "请安装chafa: brew install chafa (macOS) 或 sudo apt-get install chafa (Ubuntu)"
ERR_PATH_NOT_EXISTS = "错误: 路径不存在"
ERR_NOT_DIRECTORY = "错误: 不是目录"
ERR_NOT_FILE = "错误: 不是文件"
ERR_UNSUPPORTED_FORMAT = "错误: 不支持的图片格式"