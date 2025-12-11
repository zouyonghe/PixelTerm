#!/usr/bin/env python3
"""
PixelTerm - 终端图片浏览器主程序
"""

import sys
import os
import signal
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_viewer import ImageViewer
from file_browser import FileBrowser
from interface import Interface, InputHandler
from config import Config, DisplayOptions


class PixelTerm:
    """主应用程序类"""
    
    def __init__(self, path: str = None):
        self.config = Config()
        self.display_options = DisplayOptions(self.config)
        self.interface = Interface()
        self.image_viewer = ImageViewer()
        self.file_browser = FileBrowser()
        self.input_handler = InputHandler(self.interface)
        
        # 按键序列缓冲区
        self.key_buffer = ""
        
        # 设置初始路径
        if path:
            path_obj = Path(path)
            if path_obj.is_file():
                # 如果是文件，设置为图片文件
                if not self.file_browser.set_image_file(path):
                    print(f"无法打开图片文件: {path}")
                    sys.exit(1)
            elif path_obj.is_dir():
                # 如果是目录，设置为目录
                if not self.file_browser.set_directory(path):
                    print(f"无法打开目录: {path}")
                    sys.exit(1)
            else:
                print(f"错误: 路径不存在 {path}")
                sys.exit(1)
        else:
            self.file_browser.set_directory('.')
        
        # 注册键盘事件处理器
        self.setup_key_handlers()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def setup_key_handlers(self):
        """设置键盘事件处理器"""
        self.input_handler.register_handler('q', self.quit)
        self.input_handler.register_handler('\x03', self.quit)  # Ctrl+C
        
        # 导航键
        self.input_handler.register_handler('\x1b[D', self.previous_image)  # 左箭头
        self.input_handler.register_handler('\x1b[C', self.next_image)     # 右箭头
        self.input_handler.register_handler('\x1bOD', self.previous_image) # 左箭头 (某些终端)
        self.input_handler.register_handler('\x1bOC', self.next_image)    # 右箭头 (某些终端)
        
        # 备用按键
        self.input_handler.register_handler('a', self.previous_image)  # a键代替左箭头
        self.input_handler.register_handler('d', self.next_image)     # d键代替右箭头
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        # 强制退出，跳过确认
        self.input_handler.stop()
    
    def run(self):
        """运行主循环"""
        self.interface.setup_terminal()
        
        # 记录上次的终端大小
        last_term_size = self.image_viewer.get_terminal_size()
        
        try:
            self.refresh_display()
            
            while self.input_handler.running:
                # 检查终端大小是否改变
                current_term_size = self.image_viewer.get_terminal_size()
                if current_term_size != last_term_size:
                    last_term_size = current_term_size
                    # 终端大小改变，重新绘制
                    self.refresh_display(clear_first=True)
                
                # 直接读取按键，不使用select检测
                key = self.interface.get_key()
                if key:
                    # 将按键添加到缓冲区
                    self.key_buffer += key
                    
                    # 尝试处理缓冲区中的按键序列
                    handled = self.input_handler.handle_input(self.key_buffer)
                    
                    if handled:
                        # 如果处理成功，清空缓冲区
                        self.key_buffer = ""
                    elif len(self.key_buffer) > 10:
                        # 如果缓冲区太长且没被处理，清空
                        self.key_buffer = ""
                    elif not self.key_buffer.startswith('\x1b'):
                        # 如果不是ESC序列开头，直接处理单个字符
                        self.input_handler.handle_input(key)
                        self.key_buffer = ""
                    elif len(self.key_buffer) >= 3 and not self.input_handler.handle_input(self.key_buffer):
                        # 如果是ESC序列且长度>=3但未被处理，可能是无效序列，清空
                        self.key_buffer = ""
        
        finally:
            self.interface.restore_terminal()
    
    def refresh_display(self, clear_first: bool = True):
        """刷新显示"""
        current_image = self.file_browser.get_current_image()
        if current_image:
            # 显示图片
            self.image_viewer.display_image_with_info(
                str(current_image), 
                self.display_options.get_scale(),
                clear_first
            )
        else:
            if clear_first:
                self.interface.clear_screen()
            print("No images found")
    
    def next_image(self):
        """下一张图片"""
        if self.file_browser.next_image():
            self.refresh_display(clear_first=True)
        return True
    
    def previous_image(self):
        """上一张图片"""
        if self.file_browser.previous_image():
            self.refresh_display(clear_first=True)
        return True
    
    def zoom_in(self):
        """放大"""
        if self.display_options.zoom_in():
            self.refresh_display()
        else:
            self.interface.show_info("已达到最大缩放")
        return True
    
    def zoom_out(self):
        """缩小"""
        if self.display_options.zoom_out():
            self.refresh_display()
        else:
            self.interface.show_info("已达到最小缩放")
        return True
    
    def reset_zoom(self):
        """重置缩放"""
        self.display_options.reset_zoom()
        self.refresh_display()
        return True
    
    def show_help(self):
        """显示帮助"""
        self.interface.show_help()
        self.refresh_display()
        return True
    
    def go_up_directory(self):
        """返回上级目录"""
        if self.file_browser.go_up_directory():
            self.refresh_display()
        else:
            self.interface.show_info("已经在根目录")
        return True
    
    def show_directory_list(self):
        """显示目录列表"""
        subdirs = self.file_browser.get_subdirectories()
        if subdirs:
            self.interface.show_directory_list(subdirs)
            dirname = self.interface.prompt_directory()
            if dirname and dirname in subdirs:
                if self.file_browser.enter_subdirectory(dirname):
                    self.refresh_display()
                else:
                    self.interface.show_error(f"无法进入目录: {dirname}")
            elif dirname:
                self.interface.show_error(f"目录不存在: {dirname}")
        else:
            self.interface.show_info("当前目录没有子目录")
        
        self.refresh_display()
        return True
    
    def handle_directory_selection(self, key: str):
        """处理目录选择"""
        subdirs = self.file_browser.get_subdirectories()
        if subdirs and key.isdigit():
            index = int(key) - 1
            if 0 <= index < len(subdirs):
                if self.file_browser.enter_subdirectory(subdirs[index]):
                    self.refresh_display()
        return True
    
    def move_up_in_list(self):
        """在文件列表中向上移动"""
        # 这里可以实现文件列表的选择逻辑
        return True
    
    def move_down_in_list(self):
        """在文件列表中向下移动"""
        # 这里可以实现文件列表的选择逻辑
        return True
    
    def refresh(self):
        """刷新"""
        self.file_browser.refresh_file_list()
        self.refresh_display()
        return True
    
    def quit(self):
        """退出"""
        self.input_handler.stop()
        return True


def main():
    """主函数"""
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    # 检查chafa是否可用
    import subprocess
    try:
        subprocess.run(['chafa', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到chafa命令")
        print("请安装chafa: sudo pacman -S chafa (Arch Linux)")
        sys.exit(1)
    
    # 启动应用
    app = PixelTerm(path)
    app.run()


if __name__ == "__main__":
    main()