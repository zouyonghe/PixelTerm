#!/usr/bin/env python3
"""
PixelTerm 文件浏览器模块
处理目录浏览和图片文件管理
"""

import os
import sys
import tempfile
import hashlib
import shutil
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
        
        # chafa预渲染缓存 - 内存中只保留当前图片及前后各一张
        self.render_cache: Dict[Path, str] = {}
        self.preload_size = DEFAULT_PRELOAD_SIZE
        self.preload_enabled = True
        
        # 临时文件缓存目录
        self.temp_dir = tempfile.mkdtemp(prefix="pixelterm_cache_")
        self.file_cache_range = 10  # 前后10张图存储到临时文件
        
        # 线程池用于预渲染
        self.render_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="chafa_render")
    
    def set_directory(self, directory: str) -> bool:
        """设置当前目录"""
        try:
            path = Path(directory).resolve()
            if not path.exists():
                print(f"Error: Path does not exist {directory}")
                return False
            
            if not path.is_dir():
                print(f"Error: Not a directory {directory}")
                return False
            
            self.current_directory = path
            self.refresh_file_list()
            return True
            
        except Exception as e:
            print(f"Error setting directory: {e}")
            return False
    
    def set_image_file(self, filepath: str) -> bool:
        """设置单个图片文件"""
        try:
            path = Path(filepath).resolve()
            if not path.exists():
                print(f"Error: File does not exist {filepath}")
                return False
            
            if not path.is_file():
                print(f"Error: Not a file {filepath}")
                return False
            
            if not self.is_image_file(path):
                print(f"Error: Unsupported image format {filepath}")
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
            print(f"Error setting image file: {e}")
            return False
    
    def refresh_file_list(self):
        """刷新当前目录的图片文件列表"""
        self.image_files.clear()
        self.render_cache.clear()  # 清空内存缓存
        
        # 清理临时文件缓存
        self._clear_temp_cache()
        
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
            print(f"Error reading directory: {e}")
    
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
            # 预渲染当前图片前后各10张到临时文件
            start_idx = max(0, self.current_index - self.file_cache_range)
            end_idx = min(len(self.image_files), self.current_index + self.file_cache_range + 1)
            
            for i in range(start_idx, end_idx):
                if i != self.current_index:  # 跳过当前图片
                    img_path = self.image_files[i]
                    
                    # 检查是否已经缓存到临时文件
                    if not self._get_cache_file_path(img_path).exists():
                        try:
                            # 使用ChafaWrapper预渲染
                            rendered = ChafaWrapper.render_image(str(img_path))
                            if rendered:
                                # 保存到临时文件
                                self._save_to_temp_cache(img_path, rendered)
                                
                                # 如果在内存缓存范围内，也保存到内存
                                if self._is_in_memory_range(img_path):
                                    self.render_cache[img_path] = rendered
                            
                            time.sleep(PRELOAD_SLEEP_TIME)  # 避免占用过多CPU
                        except Exception:
                            pass  # 忽略渲染失败的图片
            
            # 清理内存缓存，只保留当前图片及前后各一张
            self._cleanup_memory_cache()
            
        except Exception:
            pass  # 忽略预渲染错误
    
    def _cleanup_memory_cache(self):
        """清理内存缓存，只保留当前图片及前后各一张"""
        if not self.image_files:
            return
        
        # 找出应该保留在内存中的图片
        to_keep = set()
        start_idx = max(0, self.current_index - 1)
        end_idx = min(len(self.image_files), self.current_index + 2)
        
        for i in range(start_idx, end_idx):
            to_keep.add(self.image_files[i])
        
        # 清理不在保留范围内的内存缓存
        to_remove = []
        for img_path in self.render_cache:
            if img_path not in to_keep:
                to_remove.append(img_path)
        
        for img_path in to_remove:
            del self.render_cache[img_path]
    
    def _get_cache_file_path(self, img_path: Path) -> Path:
        """获取图片对应的缓存文件路径"""
        # 使用文件路径的哈希值作为缓存文件名，避免路径过长和特殊字符问题
        path_str = str(img_path.absolute())
        hash_obj = hashlib.md5(path_str.encode())
        cache_filename = f"{hash_obj.hexdigest()}.txt"
        return Path(self.temp_dir) / cache_filename
    
    def _clear_temp_cache(self):
        """清理临时文件缓存"""
        try:
            if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            self.temp_dir = tempfile.mkdtemp(prefix="pixelterm_cache_")
        except Exception:
            pass
    
    def _save_to_temp_cache(self, img_path: Path, rendered_data: str):
        """保存渲染数据到临时文件"""
        try:
            cache_file = self._get_cache_file_path(img_path)
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(rendered_data)
        except Exception:
            pass
    
    def _load_from_temp_cache(self, img_path: Path) -> Optional[str]:
        """从临时文件加载渲染数据"""
        try:
            cache_file = self._get_cache_file_path(img_path)
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return None
    
    def _is_in_memory_range(self, img_path: Path) -> bool:
        """判断图片是否应该在内存缓存范围内（当前图片及前后各一张）"""
        if not self.image_files:
            return False
        
        try:
            img_index = self.image_files.index(img_path)
            return abs(img_index - self.current_index) <= 1
        except ValueError:
            return False
    
    def get_rendered_image(self, img_path: Path) -> Optional[str]:
        """获取预渲染的图片数据"""
        # 首先检查内存缓存
        if img_path in self.render_cache:
            return self.render_cache[img_path]
        
        # 如果不在内存缓存中，尝试从临时文件加载
        cached_data = self._load_from_temp_cache(img_path)
        if cached_data:
            # 如果图片在内存缓存范围内，加载到内存
            if self._is_in_memory_range(img_path):
                self.render_cache[img_path] = cached_data
            return cached_data
        
        return None
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'render_executor'):
            self.render_executor.shutdown(wait=False)
        
        # 清理临时文件缓存
        try:
            if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
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
        
        # 更新内存缓存，确保当前图片在内存中
        self._update_memory_cache_on_switch()
        
        # 触发预渲染
        self.preload_renders()
        return True
    
    def previous_image(self) -> bool:
        """切换到上一张图片"""
        if not self.image_files:
            return False
        
        self.current_index = (self.current_index - 1) % len(self.image_files)
        
        # 更新内存缓存，确保当前图片在内存中
        self._update_memory_cache_on_switch()
        
        # 触发预渲染
        self.preload_renders()
        return True
    
    def _update_memory_cache_on_switch(self):
        """切换图片时更新内存缓存"""
        if not self.image_files:
            return
        
        # 确保当前图片在内存缓存中
        current_img = self.get_current_image()
        if current_img and current_img not in self.render_cache:
            # 尝试从临时文件加载
            cached_data = self._load_from_temp_cache(current_img)
            if cached_data:
                self.render_cache[current_img] = cached_data
        
        # 清理不在内存范围内的缓存
        self._cleanup_memory_cache()
    
    def jump_to_image(self, index: int) -> bool:
        """跳转到指定索引的图片"""
        if 0 <= index < len(self.image_files):
            self.current_index = index
            
            # 更新内存缓存，确保当前图片在内存中
            self._update_memory_cache_on_switch()
            
            # 触发预渲染
            self.preload_renders()
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
        print("Usage: python file_browser.py <directory_path>")
        sys.exit(1)
    
    browser = FileBrowser()
    if browser.set_directory(sys.argv[1]):
        print(f"Directory: {browser.get_directory_info()}")
    print(f"Image count: {browser.get_image_count()}")
    
    current = browser.get_current_image()
    if current:
        print(f"Current image: {current}")
    else:
        print("Cannot set directory")