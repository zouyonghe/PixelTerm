#!/usr/bin/env python3
"""
PixelTerm 用户界面模块
处理键盘输入和用户交互
"""

import os
import sys
import termios
import tty
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
        print("\n按任意键继续...")
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
        print(f"🖼️  {current+1}/{total} | 🔍 {scale:.1f}x | 按 h 查看帮助")
        print(f"{'='*60}")
    
    def show_file_list(self, files: list, current_index: int):
        """显示文件列表"""
        print("\n📋 文件列表:")
        for i, file_info in enumerate(files):
            print(file_info)
    
    def show_directory_list(self, directories: list):
        """显示目录列表"""
        if not directories:
            print("\n📁 当前目录没有子目录")
            return
        
        print("\n📁 子目录列表:")
        for i, dirname in enumerate(directories):
            print(f"  {i+1}. {dirname}")
        print("\n输入目录名进入，或按 Esc 取消:")
    
    def prompt_directory(self) -> Optional[str]:
        """提示输入目录名"""
        # 临时恢复终端模式以获取正常输入
        temp_settings = self.old_settings
        if self.old_settings:
            self.restore_terminal()
        
        try:
            dirname = input("输入目录名: ").strip()
            return dirname if dirname else None
        except:
            return None
        finally:
            # 恢复原始模式
            if temp_settings:
                try:
                    self.old_settings = temp_settings
                    tty.setraw(sys.stdin.fileno())
                except:
                    self.old_settings = None
    
    def confirm_exit(self) -> bool:
        """确认退出"""
        # 临时恢复终端模式以获取正常输入
        temp_settings = self.old_settings
        if self.old_settings:
            self.restore_terminal()
        
        try:
            response = input("\n确定要退出吗? (y/N): ").strip().lower()
            return response == 'y' or response == 'yes'
        except:
            return False
        finally:
            # 恢复原始模式
            if temp_settings:
                try:
                    self.old_settings = temp_settings
                    tty.setraw(sys.stdin.fileno())
                except:
                    self.old_settings = None
    
    def show_error(self, message: str):
        """显示错误信息"""
        # 临时恢复终端模式以获取正常输入
        temp_settings = self.old_settings
        if self.old_settings:
            self.restore_terminal()
        
        try:
            print(f"\n❌ 错误: {message}")
            input("按任意键继续...")
        except:
            pass
        finally:
            # 恢复原始模式
            if temp_settings:
                try:
                    self.old_settings = temp_settings
                    tty.setraw(sys.stdin.fileno())
                except:
                    self.old_settings = None
    
    def show_info(self, message: str):
        """显示信息"""
        # 临时恢复终端模式以获取正常输入
        temp_settings = self.old_settings
        if self.old_settings:
            self.restore_terminal()
        
        try:
            print(f"\nℹ️  {message}")
            input("按任意键继续...")
        except:
            pass
        finally:
            # 恢复原始模式
            if temp_settings:
                try:
                    self.old_settings = temp_settings
                    tty.setraw(sys.stdin.fileno())
                except:
                    self.old_settings = None


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