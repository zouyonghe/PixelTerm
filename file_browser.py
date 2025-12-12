#!/usr/bin/env python3
"""
PixelTerm 文件浏览器模块
处理目录浏览和图片文件管理
"""

import os
import sys
from typing import List, Optional, Dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from constants import SUPPORTED_FORMATS, DEFAULT_PRELOAD_SIZE, PRELOAD_SLEEP_TIME
from chafa_wrapper import ChafaWrapper


class FileBrowser:
    """文件浏览器"""
    
    def __init__(self):
        self.current_directory = Path.cwd()
        self.image_files: List[Path] = []
        self.current_index = 0
        
        # chafa预渲染缓存
        self.render_cache: Dict[Path, str] = {}
        self.preload_size = DEFAULT_PRELOAD_SIZE
        self.preload_enabled = True
        
        # 线程池用于预渲染
        self.render_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="chafa_render")
    
    def set_directory(self, directory: str) -> bool:
        """设置当前目录"""
        try:
            path = Path(directory).resolve()
            if not path.exists():
                print(f"错误: 路径不存在 {directory}")
                return False
            
            if not path.is_dir():
                print(f"错误: 不是目录 {directory}")
                return False
            
            self.current_directory = path
            self.refresh_file_list()
            return True
            
        except Exception as e:
            print(f"设置目录时出错: {e}")
            return False
    
    def set_image_file(self, filepath: str) -> bool:
        """设置单个图片文件"""
        try:
            path = Path(filepath).resolve()
            if not path.exists():
                print(f"错误: 文件不存在 {filepath}")
                return False
            
            if not path.is_file():
                print(f"错误: 不是文件 {filepath}")
                return False
            
            if not self.is_image_file(path):
                print(f"错误: 不支持的图片格式 {filepath}")
                return False
            
            # 设置文件所在目录
            self.current_directory = path.parent
            self.refresh_file_list()
            
            # 找到当前文件在列表中的索引
            for i, img_file in enumerate(self.image_files):
                if img_file == path:
                    self.current_index = i
                    return True
            
            # 如果没找到，添加到列表
            self.image_files.append(path)
            self.image_files.sort()
            for i, img_file in enumerate(self.image_files):
                if img_file == path:
                    self.current_index = i
                    return True
            
            return False
            
        except Exception as e:
            print(f"设置图片文件时出错: {e}")
            return False
    
    def refresh_file_list(self):
        """刷新当前目录的图片文件列表"""
        self.image_files.clear()
        self.render_cache.clear()  # 清空预渲染缓存
        
        try:
            for item in self.current_directory.iterdir():
                if item.is_file() and self.is_image_file(item):
                    self.image_files.append(item)
            
            # 按文件名排序
            self.image_files.sort()
            self.current_index = 0
            
            # 开始预渲染
            self.preload_renders()
            
        except Exception as e:
            print(f"读取目录时出错: {e}")
    
    def preload_renders(self):
        """预渲染图片"""
        if not self.image_files or not self.preload_enabled:
            return
        
        # 提交预渲染任务到线程池
        self.render_executor.submit(self._render_worker)
    
    def get_preload_status(self):
        """获取预加载状态"""
        return self.preload_enabled
    
    def _render_worker(self):
        """预渲染工作线程"""
        import time
        try:
            # 预渲染当前图片前后各几张
            start_idx = max(0, self.current_index - self.preload_size)
            end_idx = min(len(self.image_files), self.current_index + self.preload_size + 1)
            
            for i in range(start_idx, end_idx):
                if i != self.current_index:  # 跳过当前图片
                    img_path = self.image_files[i]
                    if img_path not in self.render_cache:
                        try:
                            # 使用ChafaWrapper预渲染
                            rendered = ChafaWrapper.render_image(str(img_path))
                            if rendered:
                                self.render_cache[img_path] = rendered
                            
                            time.sleep(PRELOAD_SLEEP_TIME)  # 避免占用过多CPU
                        except Exception:
                            pass  # 忽略渲染失败的图片
        except Exception:
            pass  # 忽略预渲染错误
    
    def get_rendered_image(self, img_path: Path) -> Optional[str]:
        """获取预渲染的图片数据"""
        return self.render_cache.get(img_path)
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'render_executor'):
            self.render_executor.shutdown(wait=False)
    
    def is_image_file(self, filepath: Path) -> bool:
        """检查是否为支持的图片格式"""
        return filepath.suffix.lower() in SUPPORTED_FORMATS
    
    def get_image_count(self) -> int:
        """获取当前目录图片数量"""
        return len(self.image_files)
    
    def get_current_image(self) -> Optional[Path]:
        """获取当前图片路径"""
        if 0 <= self.current_index < len(self.image_files):
            return self.image_files[self.current_index]
        return None
    
    def next_image(self) -> bool:
        """切换到下一张图片"""
        if not self.image_files:
            return False
        
        self.current_index = (self.current_index + 1) % len(self.image_files)
        # 触发预渲染
        self.preload_renders()
        return True
    
    def previous_image(self) -> bool:
        """切换到上一张图片"""
        if not self.image_files:
            return False
        
        self.current_index = (self.current_index - 1) % len(self.image_files)
        # 触发预渲染
        self.preload_renders()
        return True
    
    def jump_to_image(self, index: int) -> bool:
        """跳转到指定索引的图片"""
        if 0 <= index < len(self.image_files):
            self.current_index = index
            return True
        return False
    
    def get_file_list_display(self, max_items: int = 10) -> List[str]:
        """获取文件列表显示"""
        if not self.image_files:
            return ["当前目录没有图片文件"]
        
        display_list = []
        start = max(0, self.current_index - max_items // 2)
        end = min(len(self.image_files), start + max_items)
        
        # 调整显示范围，确保当前文件在视野中
        if end - start < max_items and start > 0:
            start = max(0, end - max_items)
        
        for i in range(start, end):
            filename = self.image_files[i].name
            if i == self.current_index:
                display_list.append(f"> {i+1:2d}. {filename}")
            else:
                display_list.append(f"  {i+1:2d}. {filename}")
        
        return display_list
    
    def get_directory_info(self) -> str:
        """获取当前目录信息"""
        return f"📁 {self.current_directory} ({len(self.image_files)} 张图片)"
    
    def get_current_file_info(self) -> str:
        """获取当前文件信息"""
        current = self.get_current_image()
        if current:
            return f"📄 {current.name} ({self.current_index + 1}/{len(self.image_files)})"
        return "📄 无文件"
    
    def go_up_directory(self) -> bool:
        """返回上级目录"""
        parent = self.current_directory.parent
        if parent != self.current_directory:  # 避免到达根目录
            self.current_directory = parent
            self.refresh_file_list()
            return True
        return False
    
    def enter_subdirectory(self, subdir_name: str) -> bool:
        """进入子目录"""
        subdir = self.current_directory / subdir_name
        if subdir.is_dir():
            self.current_directory = subdir
            self.refresh_file_list()
            return True
        return False
    
    def get_subdirectories(self) -> List[str]:
        """获取当前目录的子目录列表"""
        subdirs = []
        try:
            for item in self.current_directory.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    subdirs.append(item.name)
            subdirs.sort()
        except Exception:
            pass
        return subdirs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python file_browser.py <目录路径>")
        sys.exit(1)
    
    browser = FileBrowser()
    if browser.set_directory(sys.argv[1]):
        print(f"目录: {browser.get_directory_info()}")
        print(f"图片数量: {browser.get_image_count()}")
        if browser.get_image_count() > 0:
            print(f"当前图片: {browser.get_current_image()}")
    else:
        print("无法设置目录")