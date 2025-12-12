#!/usr/bin/env python3
"""
PixelTerm 异常定义
统一的异常处理机制
"""

from constants import ERR_CHAFA_NOT_FOUND, ERR_CHAFA_INSTALL_HINT, ERR_PATH_NOT_EXISTS, ERR_NOT_DIRECTORY, ERR_NOT_FILE, ERR_UNSUPPORTED_FORMAT


class PixelTermError(Exception):
    """PixelTerm基础异常类"""
    
    def __init__(self, message: str, hint: str = ""):
        super().__init__(message)
        self.message = message
        self.hint = hint


class ChafaNotFoundError(PixelTermError):
    """Chafa命令未找到异常"""
    
    def __init__(self):
        super().__init__(ERR_CHAFA_NOT_FOUND, ERR_CHAFA_INSTALL_HINT)


class PathNotFoundError(PixelTermError):
    """路径不存在异常"""
    
    def __init__(self, path: str):
        message = f"{ERR_PATH_NOT_EXISTS}: {path}"
        super().__init__(message)


class NotDirectoryError(PixelTermError):
    """不是目录异常"""
    
    def __init__(self, path: str):
        message = f"{ERR_NOT_DIRECTORY}: {path}"
        super().__init__(message)


class NotFileError(PixelTermError):
    """不是文件异常"""
    
    def __init__(self, path: str):
        message = f"{ERR_NOT_FILE}: {path}"
        super().__init__(message)


class UnsupportedFormatError(PixelTermError):
    """不支持的格式异常"""
    
    def __init__(self, path: str):
        message = f"{ERR_UNSUPPORTED_FORMAT}: {path}"
        super().__init__(message)


class ImageLoadError(PixelTermError):
    """图片加载异常"""
    
    def __init__(self, path: str, reason: str = ""):
        message = f"Cannot load image: {path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class RenderError(PixelTermError):
    """渲染异常"""
    
    def __init__(self, path: str, reason: str = ""):
        message = f"Render failed: {path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)