#!/usr/bin/env python3
"""
PixelTerm Chafa封装模块
统一chafa命令调用和配置
"""

import subprocess
from typing import Optional, Tuple, List
from constants import CHAFA_CMD, DEFAULT_CHAFA_ARGS


class ChafaWrapper:
    """Chafa命令封装器"""
    
    @staticmethod
    def build_command(filepath: str, scale: float = 1.0, size: Optional[Tuple[int, int]] = None) -> List[str]:
        """构建chafa命令"""
        cmd = [CHAFA_CMD] + DEFAULT_CHAFA_ARGS + [filepath]
        
        # 如果指定了尺寸，添加尺寸参数
        if size:
            width, height = size
            cmd.extend(['--size', f'{width}x{height}'])
        elif scale != 1.0:
            # 如果有缩放需求但没有具体尺寸，需要计算
            import shutil
            term_width, term_height = shutil.get_terminal_size()
            display_width = int(term_width * scale)
            display_height = int(term_height * scale)
            cmd.extend(['--size', f'{display_width}x{display_height}'])
        
        return cmd
    
    @staticmethod
    def render_image(filepath: str, scale: float = 1.0, size: Optional[Tuple[int, int]] = None) -> Optional[str]:
        """渲染图片并返回输出"""
        try:
            cmd = ChafaWrapper.build_command(filepath, scale, size)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception:
            return None
    
    @staticmethod
    def check_chafa_available() -> bool:
        """检查chafa是否可用"""
        try:
            result = subprocess.run([CHAFA_CMD, '--version'], capture_output=True, check=True)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def get_chafa_version() -> Optional[str]:
        """获取chafa版本信息"""
        try:
            result = subprocess.run([CHAFA_CMD, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None