#!/usr/bin/env python3
"""
PixelTerm - 终端图片浏览器主程序
"""

import sys
import os
import signal
import argparse
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
        
        # Info display state
        self.info_displayed = False
        
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
        """Setup keyboard event handlers"""
        self.input_handler.register_handler('q', self.quit)
        self.input_handler.register_handler(KEY_CTRL_C, self.quit)  # Ctrl+C
        
        # Navigation keys
        self.input_handler.register_handler(KEY_LEFT, self.previous_image)  # 左箭头
        self.input_handler.register_handler(KEY_RIGHT, self.next_image)     # 右箭头
        self.input_handler.register_handler(KEY_LEFT_ALT, self.previous_image) # Left arrow (some terminals)
        self.input_handler.register_handler(KEY_RIGHT_ALT, self.next_image)    # Right arrow (some terminals)
        
        # Alternative keys
        self.input_handler.register_handler('a', self.previous_image)  # a key as left arrow
        self.input_handler.register_handler('d', self.next_image)     # d key as right arrow
        
        # Information display
        self.input_handler.register_handler('i', self.show_image_info)
        
        # Delete image
        self.input_handler.register_handler('r', self.delete_current_image)
    
    def signal_handler(self, signum, frame):
        """Signal handler"""
        # Force exit, skip confirmation
        self.input_handler.stop()
    
    def run(self):
        """Run main loop"""
        # Check if there are images, if not, don't setup terminal mode
        has_images = self.file_browser.get_current_image() is not None
        
        if has_images:
            self.interface.setup_terminal()
        
        # Remember last terminal size
        last_term_size = self.image_viewer.get_terminal_size()
        
        try:
            self.refresh_display()
            
            while self.input_handler.running and has_images:
                # Check if terminal size has changed
                current_term_size = self.image_viewer.get_terminal_size()
                if current_term_size != last_term_size:
                    last_term_size = current_term_size
                    # Terminal size changed, redraw
                    self.refresh_display(clear_first=True)
                
                # Read key directly, don't use select detection
                key = self.interface.get_key()
                if key:
                    # Add key to buffer
                    self.key_buffer += key
                    
                    # Try to handle key sequence in buffer
                    handled = self.input_handler.handle_input(self.key_buffer)
                    
                    if handled:
                        # If handled successfully, clear buffer
                        self.key_buffer = ""
                    elif len(self.key_buffer) > 10:
                        # If buffer is too long and not handled, clear it
                        self.key_buffer = ""
                    elif not self.key_buffer.startswith('\x1b'):
                        # If not starting with ESC sequence, handle single character directly
                        self.input_handler.handle_input(key)
                        self.key_buffer = ""
                    elif len(self.key_buffer) >= 3 and not self.input_handler.handle_input(self.key_buffer):
                        # If ESC sequence with length>=3 but not handled, might be invalid sequence, clear it
                        self.key_buffer = ""
        
        finally:
            if has_images:
                self.interface.restore_terminal()
    
    def refresh_display(self, clear_first: bool = True):
        """Refresh display"""
        current_image = self.file_browser.get_current_image()
        if current_image:
            # Display image, pass file_browser to support pre-rendering
            self.image_viewer.display_image_with_info(
                str(current_image), 
                self.display_options.get_scale(),
                clear_first,
                self.file_browser
            )
            
            
        else:
            print("No images found")
            print()
            # Show usage help and exit
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
  ←/→        Previous/Next image
  a/d        Alternative left/right keys
  i          Show/hide image information
  r          Delete current image
  q          Quit program
  Ctrl+C     Force exit
            """)
            parser.add_argument('path', nargs='?', help='Image file or directory path')
            parser.add_argument('--no-preload', action='store_false', dest='preload_enabled', 
                                help='Disable preloading feature (enabled by default)')
            parser.print_help()
            self.input_handler.stop()
    
    
    
    def next_image(self):
        """Next image"""
        if self.file_browser.next_image():
            self.info_displayed = False  # Reset info display state
            self.refresh_display(clear_first=True)
        return True
    
    def previous_image(self):
        """Previous image"""
        if self.file_browser.previous_image():
            self.info_displayed = False  # 重置信息显示状态
            self.refresh_display(clear_first=True)
        return True
    
    
    
    def zoom_in(self):
        """Zoom in"""
        if self.display_options.zoom_in():
            self.refresh_display()
        else:
            self.interface.show_info("Maximum zoom level reached")
        return True
    
    def zoom_out(self):
        """Zoom out"""
        if self.display_options.zoom_out():
            self.refresh_display()
        else:
            self.interface.show_info("Minimum zoom level reached")
        return True
    
    def reset_zoom(self):
        """Reset zoom"""
        self.display_options.reset_zoom()
        self.refresh_display()
        return True
    
    
    
    def show_image_info(self):
        """Show/hide image information"""
        current_image = self.file_browser.get_current_image()
        if not current_image:
            return True
        
        if self.info_displayed:
            # If info is displayed, hide info and re-render image
            self.info_displayed = False
            self.refresh_display(clear_first=True)
        else:
            # Show image information
            self.interface.show_image_info(current_image, self.file_browser.get_image_count(), self.file_browser.current_index)
            self.info_displayed = True
        
        return True
    
    def delete_current_image(self):
        """Delete current image and jump to next"""
        current_image = self.file_browser.get_current_image()
        if not current_image:
            return True
        
        # Confirm deletion
        with self.interface._terminal_mode_switch():
            try:
                print(f"\nAre you sure you want to delete image '{current_image.name}'? (y/N): ", end='', flush=True)
                response = input().strip().lower()
                if response != 'y' and response != 'yes':
                    return True
            except:
                return True
        
        # Delete file
        try:
            import os
            os.remove(current_image)
            
            # Remove from file list
            self.file_browser.image_files.remove(current_image)
            
            # If no more images after deletion, exit
            if not self.file_browser.image_files:
                print("No more images")
                self.input_handler.stop()
                return True
            
            # If current index is out of range, adjust index
            if self.file_browser.current_index >= len(self.file_browser.image_files):
                self.file_browser.current_index = 0
            
            # Refresh display
            self.refresh_display(clear_first=True)
            
        except Exception as e:
            with self.interface._terminal_mode_switch():
                try:
                    print(f"Deletion failed: {e}")
                    input("Press any key to continue...")
                except:
                    pass
        
        return True
    
    def go_up_directory(self):
        """Go up to parent directory"""
        if self.file_browser.go_up_directory():
            self.refresh_display()
        else:
            self.interface.show_info("Already at root directory")
        return True
    
    def show_directory_list(self):
        """Show directory list"""
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
    
    
    
    def refresh(self):
        """Refresh"""
        self.file_browser.refresh_file_list()
        self.refresh_display()
        return True
    
    def quit(self):
        """Quit"""
        self.input_handler.stop()
        print("\r", flush=True)
        return True


def main():
    """Main function"""
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
  ←/→        Previous/Next image
  a/d        Alternative left/right keys
  i          Show/hide image information
  r          Delete current image
  q          Quit program
  Ctrl+C     Force exit
        """
    )
    
    parser.add_argument('path', nargs='?', help='Image file or directory path')
    parser.add_argument('--no-preload', action='store_false', dest='preload_enabled', 
                        help='Disable preloading feature (enabled by default)')
    
    args = parser.parse_args()
    
    # Check if chafa is available
    from chafa_wrapper import ChafaWrapper
    if not ChafaWrapper.check_chafa_available():
        print(ERR_CHAFA_NOT_FOUND)
        print(ERR_CHAFA_INSTALL_HINT)
        sys.exit(1)
    
    # Start application
    path = args.path if args.path else '.'
    app = PixelTerm(path, preload_enabled=args.preload_enabled)
    try:
        app.run()
    finally:
        # Clean up resources
        app.file_browser.cleanup()


if __name__ == "__main__":
    main()