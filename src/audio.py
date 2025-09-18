#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频系统模块
负责音效播放
"""

import pygame
from pathlib import Path


class AudioManager:
    """音频管理器"""
    
    def __init__(self, config):
        self.config = config
        self.sounds = {}
        self.enabled = config.get("audio.sound_effects", True)
        self.volume = config.get("audio.volume", 0.5)
        
        # 初始化pygame音频
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_available = True
            print("音频系统初始化成功")
        except Exception as e:
            print(f"音频系统初始化失败: {e}")
            self.audio_available = False
        
        if self.audio_available and self.enabled:
            self.load_sounds()
    
    def load_sounds(self):
        """加载音效文件"""
        sound_files = {
            'select': 'assets/sounds/select.wav',
            'confirm': 'assets/sounds/confirm.wav',
            'back': 'assets/sounds/back.wav',
            'error': 'assets/sounds/error.wav'
        }
        
        for name, path in sound_files.items():
            sound_path = Path(path)
            if sound_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(sound_path))
                    sound.set_volume(self.volume)
                    self.sounds[name] = sound
                    print(f"音效加载成功: {name}")
                except Exception as e:
                    print(f"音效加载失败 {name}: {e}")
            else:
                # 创建简单的程序生成音效
                self.sounds[name] = self.create_simple_sound(name)
    
    def create_simple_sound(self, sound_type):
        """创建简单的程序生成音效"""
        if not self.audio_available:
            return None
        
        try:
            # 创建简单的音调
            sample_rate = 22050
            duration = 0.1  # 100ms
            
            if sound_type == 'select':
                # 选择音效 - 短促的高音
                frequency = 800
            elif sound_type == 'confirm':
                # 确认音效 - 双音调
                frequency = 600
            elif sound_type == 'back':
                # 返回音效 - 低音
                frequency = 400
            else:
                # 错误音效 - 嗡嗡声
                frequency = 200
            
            # 生成正弦波
            import numpy as np
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                wave = np.sin(2 * np.pi * frequency * i / sample_rate)
                # 添加淡入淡出效果
                envelope = min(i / (frames * 0.1), (frames - i) / (frames * 0.1), 1.0)
                arr[i] = [wave * envelope * 0.3, wave * envelope * 0.3]
            
            # 转换为pygame音效
            arr = (arr * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(arr)
            sound.set_volume(self.volume)
            return sound
            
        except Exception as e:
            print(f"程序生成音效失败 {sound_type}: {e}")
            return None
    
    def play(self, sound_name):
        """播放音效"""
        if not self.enabled or not self.audio_available:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"音效播放失败 {sound_name}: {e}")
    
    def set_enabled(self, enabled):
        """设置音效开关"""
        self.enabled = enabled
    
    def set_volume(self, volume):
        """设置音量"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
    
    def cleanup(self):
        """清理音频资源"""
        if self.audio_available:
            pygame.mixer.quit()