#!/usr/bin/env python3
"""
PixelTerm - 终端图片浏览器主程序
"""

import sys
import os
import signal
from pathlib import Path
from constants import KEY_LEFT, KEY_RIGHT, KEY_LEFT_ALT, KEY_RIGHT_ALT, KEY_CTRL_C, ERR_CHAFA_NOT_FOUND, ERR_CHAFA_INSTALL_HINT
from exceptions import ChafaNotFoundError

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_viewer import ImageViewer
from file_browser import FileBrowser
from interface import Interface, InputHandler
from config import Config, DisplayOptions


class PixelTerm:
    """主应用程序类"""
    
    def __init__(self, path: str = None, preload_enabled: bool = True):
        self.config = Config()
        self.display_options = DisplayOptions(self.config)
        self.interface = Interface()
        self.image_viewer = ImageViewer()
        self.file_browser = FileBrowser()
        self.input_handler = InputHandler(self.interface)
        
        # 按键序列缓冲区
        self.key_buffer = ""
        
        # 设置预加载状态
        self.file_browser.preload_enabled = preload_enabled
        
        # 设置初始路径
        if path:
            path_obj = Path(path)
            if path_obj.is_file():
                # 如果是文件，设置为图片文件
                if not self.file_browser.set_image_file(path):
                    print(f"Cannot open image file: {path}")
                    sys.exit(1)
            elif path_obj.is_dir():
                # 如果是目录，设置为目录
                if not self.file_browser.set_directory(path):
                    print(f"Cannot open directory: {path}")
                    sys.exit(1)
            else:
                print(f"Error: Path does not exist {path}")
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
        self.input_handler.register_handler(KEY_CTRL_C, self.quit)  # Ctrl+C
        
        # 导航键
        self.input_handler.register_handler(KEY_LEFT, self.previous_image)  # 左箭头
        self.input_handler.register_handler(KEY_RIGHT, self.next_image)     # 右箭头
        self.input_handler.register_handler(KEY_LEFT_ALT, self.previous_image) # 左箭头 (某些终端)
        self.input_handler.register_handler(KEY_RIGHT_ALT, self.next_image)    # 右箭头 (某些终端)
        
        # 备用按键
        self.input_handler.register_handler('a', self.previous_image)  # a键代替左箭头
        self.input_handler.register_handler('d', self.next_image)     # d键代替右箭头
        
        # 信息显示
        self.input_handler.register_handler('i', self.show_image_info)
    
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
            # 显示图片，传递file_browser以支持预渲染
            self.image_viewer.display_image_with_info(
                str(current_image), 
                self.display_options.get_scale(),
                clear_first,
                self.file_browser
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
            self.interface.show_info("Maximum zoom level reached")
        return True
    
    def zoom_out(self):
        """缩小"""
        if self.display_options.zoom_out():
            self.refresh_display()
        else:
            self.interface.show_info("Minimum zoom level reached")
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
    
    def show_image_info(self):
        """显示图片信息"""
        current_image = self.file_browser.get_current_image()
        if current_image:
            self.interface.show_image_info(current_image, self.file_browser.get_image_count(), self.file_browser.current_index)
        return True
    
    def go_up_directory(self):
        """返回上级目录"""
        if self.file_browser.go_up_directory():
            self.refresh_display()
        else:
            self.interface.show_info("Already at root directory")
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
                    self.interface.show_error(f"Cannot enter directory: {dirname}")
            elif dirname:
                self.interface.show_error(f"Directory does not exist: {dirname}")
        else:
            self.interface.show_info("No subdirectories in current directory")
        
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
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PixelTerm - Terminal Image Viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                    # Browse images in current directory
  %(prog)s /path/to/images    # Browse images in specified directory
  %(prog)s image.jpg          # Display specified image directly
  %(prog)s --no-preload       # Disable preloading for faster startup
  %(prog)s --help             # Show help information

Shortcuts:
  ←/→     Previous/Next image
  a/d     Alternative left/right keys
  i       Show detailed image information
  q       Quit program
  Ctrl+C  Force exit
        """
    )
    
    parser.add_argument('path', nargs='?', help='Image file or directory path')
    parser.add_argument('--no-preload', action='store_false', dest='preload_enabled', 
                        help='Disable preloading feature (enabled by default)')
    
    args = parser.parse_args()
    
    # 检查chafa是否可用
    from chafa_wrapper import ChafaWrapper
    if not ChafaWrapper.check_chafa_available():
        print(ERR_CHAFA_NOT_FOUND)
        print(ERR_CHAFA_INSTALL_HINT)
        sys.exit(1)
    
    # 启动应用
    path = args.path if args.path else '.'
    app = PixelTerm(path, preload_enabled=args.preload_enabled)
    try:
        app.run()
    finally:
        # 清理资源
        app.file_browser.cleanup()


if __name__ == "__main__":
    main()