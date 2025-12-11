#!/usr/bin/env python3
"""
PixelTerm 图片显示模块
使用chafa命令行工具在终端中显示图片
"""

import os
import subprocess
import sys
from typing import Optional, Tuple
from PIL import Image


class ImageViewer:
    """终端图片显示器"""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    
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
    
    def display_image(self, filepath: str, scale: float = 1.0) -> bool:
        """使用chafa显示图片"""
        try:
            # 获取最优显示尺寸
            display_width, display_height = self.get_optimal_chafa_size(scale)
            
            # 构建chafa命令，让chafa自动选择最佳格式和尺寸
            cmd = [
                'chafa',
                '--color-space', 'rgb',
                '--dither', 'none',
                '--relative', 'off',     # 关闭相对定位，避免残留
                '--optimize', '9',       # 启用所有优化
                '--margin-right', '0',   # 右边距设为0
                '--work', '9',           # 最高质量处理
                filepath
            ]
            
            # 只有在需要缩放时才添加尺寸参数
            if display_width is not None and display_height is not None:
                cmd.extend(['--size', f'{display_width}x{display_height}'])
            
            # 执行chafa命令并直接输出到stdout
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # 直接输出，不进行额外处理
                print(result.stdout, end='')
                return True
            else:
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
        # 或者精确清除指定行数
        # for _ in range(term_height):
        #     print('\033[K')  # 清除从光标到行尾
    
    def display_image_with_info(self, filepath: str, scale: float = 1.0, clear_first: bool = True) -> bool:
        """显示图片"""
        if clear_first:
            # 清除显示区域
            self.clear_display_area()
        print('\033[?25l', end='')  # 隐藏光标
        
        # 显示图片
        result = self.display_image(filepath, scale)
        
        # 显示结束后显示光标
        print('\033[?25h', end='', flush=True)  # 显示光标
        
        return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python image_viewer.py <图片路径>")
        sys.exit(1)
    
    viewer = ImageViewer()
    viewer.display_image_with_info(sys.argv[1])