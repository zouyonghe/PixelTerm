#!/usr/bin/env python3
"""
PixelTerm 配置模块
管理应用程序设置和选项
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from constants import DEFAULT_SCALE, SCALE_STEP, MIN_SCALE, MAX_SCALE


class Config:
    """配置管理器"""
    
    def __init__(self):
        self.config_file = Path.home() / '.pixelterm' / 'config.json'
        self.default_config = {
            'display': {
                'default_scale': DEFAULT_SCALE,
                'scale_step': SCALE_STEP,
                'min_scale': MIN_SCALE,
                'max_scale': MAX_SCALE,
                'auto_fit': True,
                'preserve_aspect_ratio': True
            },
            'chafa': {
                'format': 'symbols',
                'color_space': 'rgb',
                'dither': 'none',
                'symbols': 'block'
            },
            'interface': {
                'show_file_list': True,
                'file_list_max_items': 10,
                'auto_refresh': True,
                'confirm_exit': True
            },
            'navigation': {
                'wrap_around': True,
                'remember_position': True,
                'sort_by': 'name'  # name, size, date
            }
        }
        self.config = self.default_config.copy()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(self.config, user_config)
        except Exception as e:
            print(f"Failed to load configuration file: {e}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save configuration file: {e}")
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """设置配置值"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self.default_config.copy()
    
    def get_display_config(self) -> Dict[str, Any]:
        """获取显示配置"""
        return self.config.get('display', {})
    
    def get_chafa_config(self) -> Dict[str, Any]:
        """获取chafa配置"""
        return self.config.get('chafa', {})
    
    def get_interface_config(self) -> Dict[str, Any]:
        """获取界面配置"""
        return self.config.get('interface', {})
    
    def get_navigation_config(self) -> Dict[str, Any]:
        """获取导航配置"""
        return self.config.get('navigation', {})


class DisplayOptions:
    """显示选项管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.scale = config.get('display.default_scale', 1.0)
        self.scale_step = config.get('display.scale_step', 0.1)
        self.min_scale = config.get('display.min_scale', 0.1)
        self.max_scale = config.get('display.max_scale', 3.0)
        self.auto_fit = config.get('display.auto_fit', True)
        self.preserve_aspect_ratio = config.get('display.preserve_aspect_ratio', True)
    
    def zoom_in(self) -> bool:
        """放大"""
        new_scale = self.scale + self.scale_step
        if new_scale <= self.max_scale:
            self.scale = new_scale
            return True
        return False
    
    def zoom_out(self) -> bool:
        """缩小"""
        new_scale = self.scale - self.scale_step
        if new_scale >= self.min_scale:
            self.scale = new_scale
            return True
        return False
    
    def reset_zoom(self):
        """重置缩放"""
        self.scale = self.config.get('display.default_scale', 1.0)
    
    def set_scale(self, scale: float) -> bool:
        """设置缩放比例"""
        if self.min_scale <= scale <= self.max_scale:
            self.scale = scale
            return True
        return False
    
    def get_scale(self) -> float:
        """获取当前缩放比例"""
        return self.scale
    
    def toggle_auto_fit(self):
        """切换自动适配"""
        self.auto_fit = not self.auto_fit
    
    def toggle_preserve_aspect_ratio(self):
        """切换保持宽高比"""
        self.preserve_aspect_ratio = not self.preserve_aspect_ratio


if __name__ == "__main__":
    config = Config()
    print("Current configuration:")
    print(json.dumps(config.config, indent=2, ensure_ascii=False))