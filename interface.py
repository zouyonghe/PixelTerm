#!/usr/bin/env python3
"""
PixelTerm 用户界面模块
处理键盘输入和用户交互
"""

import os
import sys
import termios
import tty
from contextlib import contextmanager
from typing import Optional, Callable


class Interface:
    """终端用户界面"""
    
    def __init__(self):
        self.old_settings = None
        self.help_text = """
🖼️  PixelTerm - 终端图片浏览器

📋 快捷键:
  ←/→     上一张/下一张图片
  ↑/↓     选择文件
  Enter   打开选中的文件
  +/-     放大/缩小
  r       重置缩放
  h/?     显示帮助
  q       退出
  u       返回上级目录
  d       显示目录列表
  
📁 目录导航:
  使用 d 查看子目录，然后输入目录名进入
  使用 u 返回上级目录
        """
    
    def setup_terminal(self):
        """设置终端为原始模式"""
        try:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except:
            # 如果无法设置终端模式，使用普通输入
            pass
    
    def restore_terminal(self):
        """恢复终端设置"""
        if self.old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except:
                pass
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def get_key(self) -> Optional[str]:
        """获取键盘输入"""
        try:
            if self.old_settings:
                # 原始模式 - 无超时，直接等待
                return sys.stdin.read(1)
            else:
                # 普通模式
                return input().strip()
        except:
            return None
    
    def show_help(self):
        """显示帮助信息"""
        self.clear_screen()
        print(self.help_text)
        print("\nPress any key to continue...")
        self.wait_for_key()
    
    def wait_for_key(self):
        """等待按键"""
        if self.old_settings:
            self.get_key()
        else:
            input()
    
    def show_status_bar(self, current: int, total: int, scale: float, directory: str):
        """显示状态栏"""
        print(f"\n{'='*60}")
        print(f"📁 {directory}")
        print(f"🖼️  {current+1}/{total} | 🔍 {scale:.1f}x | Press h for help")
        print(f"{'='*60}")
    
    def show_file_list(self, files: list, current_index: int):
        """显示文件列表"""
        print("\n📋 File list:")
        for i, file_info in enumerate(files):
            print(file_info)
    
    @contextmanager
    def _terminal_mode_switch(self):
        """终端模式切换上下文管理器"""
        temp_settings = self.old_settings
        try:
            if self.old_settings:
                self.restore_terminal()
            yield
        finally:
            if temp_settings:
                try:
                    self.old_settings = temp_settings
                    tty.setraw(sys.stdin.fileno())
                except:
                    self.old_settings = None
    
    def show_image_info(self, image_path, total_count: int, current_index: int):
        """显示图片详细信息"""
        import os
        from PIL import Image
        
        with self._terminal_mode_switch():
            try:
                print(f"\n{'='*60}")
                print(f"📸 Image Details")
                print(f"{'='*60}")
                
                # Basic information
                print(f"📁 Filename: {image_path.name}")
                print(f"📂 Path: {image_path.parent}")
                print(f"📄 Index: {current_index + 1}/{total_count}")
                
                # 文件大小
                file_size = os.path.getsize(image_path)
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                print(f"💾 File size: {size_str}")
                
                # Image dimensions and format information
                try:
                    with Image.open(image_path) as img:
                        width, height = img.size
                        print(f"📐 Dimensions: {width} x {height} pixels")
                        print(f"🎨 Format: {img.format}")
                        print(f"🎭 Color mode: {img.mode}")
                        
                        # Calculate aspect ratio
                        if height > 0:
                            aspect_ratio = width / height
                            print(f"📏 Aspect ratio: {aspect_ratio:.2f}")
                        
                        # If EXIF information exists, display basic info
                        if hasattr(img, '_getexif') and img._getexif():
                            exif = img._getexif()
                            if exif:
                                print(f"📷 Contains EXIF information")
                except Exception as e:
                    print(f"❌ Unable to read image information: {e}")
                
                print(f"{'='*60}")
                
            except Exception as e:
                print(f"\n❌ Error displaying information: {e}")
    
    def show_directory_list(self, directories: list):
        """显示目录列表"""
        if not directories:
            print("\n📁 No subdirectories in current directory")
            return
        
        print("\n📁 Subdirectory list:")
        for i, dirname in enumerate(directories):
            print(f"  {i+1}. {dirname}")
        print("\nEnter directory name to enter, or press Esc to cancel:")
    
    def prompt_directory(self) -> Optional[str]:
        """提示输入目录名"""
        with self._terminal_mode_switch():
            try:
                dirname = input("Enter directory name: ").strip()
                return dirname if dirname else None
            except:
                return None
    
    def confirm_exit(self) -> bool:
        """确认退出"""
        with self._terminal_mode_switch():
            try:
                response = input("\nAre you sure you want to exit? (y/N): ").strip().lower()
                return response == 'y' or response == 'yes'
            except:
                return False
    
    def show_error(self, message: str):
        """显示错误信息"""
        with self._terminal_mode_switch():
            try:
                print(f"\n❌ Error: {message}")
                input("Press any key to continue...")
            except:
                pass
    
    def show_info(self, message: str):
        """显示信息"""
        with self._terminal_mode_switch():
            try:
                print(f"\nℹ️  {message}")
                input("Press any key to continue...")
            except:
                pass


class InputHandler:
    """输入处理器"""
    
    def __init__(self, interface: Interface):
        self.interface = interface
        self.handlers = {}
        self.running = True
    
    def register_handler(self, key: str, handler: Callable):
        """注册按键处理函数"""
        self.handlers[key] = handler
    
    def handle_input(self, key: str) -> bool:
        """处理输入"""
        if key in self.handlers:
            return self.handlers[key]()
        return False
    
    def stop(self):
        """停止处理循环"""
        self.running = False


if __name__ == "__main__":
    interface = Interface()
    interface.setup_terminal()
    
    try:
        interface.show_help()
    finally:
        interface.restore_terminal()