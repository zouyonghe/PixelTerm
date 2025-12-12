#!/usr/bin/env python3
"""
PixelTerm 图片显示模块
使用chafa命令行工具在终端中显示图片
"""

import os
import subprocess
import sys
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
from chafa_wrapper import ChafaWrapper


class ImageViewer:
    """终端图片显示器"""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        from constants import SUPPORTED_FORMATS
        self.supported_formats = SUPPORTED_FORMATS
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """获取终端大小"""
        try:
            import shutil
            size = shutil.get_terminal_size()
            return size.columns, size.lines
        except:
            return 80, 24
    
    def get_optimal_chafa_size(self, scale: float = 1.0) -> Tuple[int, int]:
        """获取最优的chafa显示尺寸"""
        term_width, term_height = self.get_terminal_size()
        
        # 默认不指定尺寸，让chafa自动选择最佳尺寸
        # 如果有缩放需求，才应用缩放
        if scale == 1.0:
            return None, None  # 让chafa自动决定
        else:
            display_width = int(term_width * scale)
            display_height = int(term_height * scale)
            return display_width, display_height
    
    def is_image_file(self, filepath: str) -> bool:
        """检查是否为支持的图片格式"""
        _, ext = os.path.splitext(filepath.lower())
        return ext in self.supported_formats
    
    def get_image_info(self, filepath: str) -> Optional[Tuple[int, int]]:
        """获取图片尺寸信息"""
        try:
            with Image.open(filepath) as img:
                return img.size
        except Exception:
            return None
    
    def display_image(self, filepath: str, scale: float = 1.0, file_browser=None) -> bool:
        """使用chafa显示图片"""
        try:
            # 尝试使用预渲染的数据
            rendered_output = None
            if file_browser:
                rendered_output = file_browser.get_rendered_image(Path(filepath))
            
            if rendered_output:
                # 使用预渲染的数据，直接输出
                print(rendered_output, end='')
                return True
            
            # 如果没有预渲染数据，使用ChafaWrapper实时渲染
            rendered = ChafaWrapper.render_image(filepath, scale)
            if rendered:
                print(rendered, end='')
                return True
            
            return False
                
        except Exception:
            return False
    
    def clear_display_area(self):
        """清除当前显示区域"""
        term_width, term_height = self.get_terminal_size()
        # 移动光标到左上角
        print('\033[H', end='', flush=True)
        # 清除整个屏幕
        print('\033[2J', end='', flush=True)
        # 立即刷新输出，确保清屏命令立即生效
        sys.stdout.flush()
    
    def display_filename(self, filepath: str):
        """在图片下方中心显示文件名"""
        try:
            # 获取终端宽度
            term_width, _ = self.get_terminal_size()
            
            # 获取文件名（不含路径）
            filename = Path(filepath).name
            
            # 计算居中位置
            filename_len = len(filename)
            if filename_len < term_width:
                # 计算左边距以居中显示
                left_padding = (term_width - filename_len) // 2
                centered_filename = ' ' * left_padding + filename
            else:
                # 如果文件名太长，截断并添加省略号
                max_len = term_width - 3  # 留出省略号的空间
                if max_len > 0:
                    centered_filename = filename[:max_len] + '...'
                else:
                    centered_filename = '...'
            
            # 移动到终端底部（倒数第二行）
            print(f'\033[{self.get_terminal_size()[1]-1};1H', end='')
            
            # 清除该行并显示文件名
            print('\033[K', end='')  # 清除当前行
            print(f'\033[36m{centered_filename}\033[0m', end='')  # 使用青色显示文件名
            
            # 立即刷新输出
            sys.stdout.flush()
        except Exception:
            # 如果显示文件名失败，静默忽略
            pass
    
    def display_image_with_info(self, filepath: str, scale: float = 1.0, clear_first: bool = True, file_browser=None) -> bool:
        """显示图片"""
        if clear_first:
            # 清除显示区域
            self.clear_display_area()
        print('\033[?25l', end='')  # 隐藏光标
        
        # 显示图片
        result = self.display_image(filepath, scale, file_browser)
        
        # 在图片下方中心显示文件名
        if result:
            self.display_filename(filepath)
        
        # 显示结束后显示光标
        print('\033[?25h', end='', flush=True)  # 显示光标
        
        return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python image_viewer.py <image_path>")
        sys.exit(1)
    
    viewer = ImageViewer()
    viewer.display_image_with_info(sys.argv[1])