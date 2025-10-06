"""
Utility classes for terminal management and performance monitoring.
"""

import os
import sys
import time
import psutil
import threading
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class PerformanceStats:
    """Performance statistics container."""
    fps: float = 0.0
    frame_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    frames_processed: int = 0
    dropped_frames: int = 0


class TerminalManager:
    """
    Advanced terminal management with cross-platform support and dynamic resizing.
    """
    
    def __init__(self):
        self.original_size = self.get_terminal_size()
        self.current_size = self.original_size
        self.resize_callbacks = []
        self._monitoring = False
        self._monitor_thread = None
        
        # Platform-specific setup
        self.is_windows = os.name == 'nt'
        self.clear_command = 'cls' if self.is_windows else 'clear'
        
        # Initialize colorama for Windows color support
        if self.is_windows:
            try:
                import colorama
                colorama.init()
            except ImportError:
                pass
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """
        Get current terminal size with fallback options.
        
        Returns:
            (width, height) in characters
        """
        try:
            # Try multiple methods for robustness
            if hasattr(os, 'get_terminal_size'):
                size = os.get_terminal_size()
                return size.columns, size.lines
            
            # Fallback for older Python versions
            import subprocess
            if self.is_windows:
                result = subprocess.run(['mode', 'con'], capture_output=True, text=True)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Columns:' in line:
                        width = int(line.split(':')[1].strip())
                    elif 'Lines:' in line:
                        height = int(line.split(':')[1].strip())
                return width, height
            else:
                result = subprocess.run(['stty', 'size'], capture_output=True, text=True)
                height, width = map(int, result.stdout.split())
                return width, height
                
        except Exception:
            # Ultimate fallback
            return 80, 24
    
    def clear_screen(self):
        """Clear the terminal screen efficiently."""
        # Use ANSI escape codes for faster clearing on all systems. On Windows,
        # colorama initialization enables ANSI processing to avoid flicker.
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
    
    def hide_cursor(self):
        """Hide the terminal cursor."""
        if not self.is_windows:
            sys.stdout.write('\033[?25l')
            sys.stdout.flush()
    
    def show_cursor(self):
        """Show the terminal cursor."""
        if not self.is_windows:
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()
    
    def move_cursor(self, x: int, y: int):
        """Move cursor to specific position."""
        if not self.is_windows:
            sys.stdout.write(f'\033[{y};{x}H')
            sys.stdout.flush()

    def cursor_home(self):
        """Move cursor to top-left without clearing the screen."""
        sys.stdout.write('\033[H')
        sys.stdout.flush()
    
    def register_resize_callback(self, callback):
        """Register a callback for terminal resize events."""
        self.resize_callbacks.append(callback)
    
    def _monitor_resize(self):
        """Monitor terminal size changes in background thread."""
        while self._monitoring:
            new_size = self.get_terminal_size()
            if new_size != self.current_size:
                old_size = self.current_size
                self.current_size = new_size
                
                # Notify all callbacks
                for callback in self.resize_callbacks:
                    try:
                        callback(old_size, new_size)
                    except Exception as e:
                        print(f"Resize callback error: {e}")
            
            time.sleep(0.1)  # Check every 100ms
    
    def start_resize_monitoring(self):
        """Start monitoring terminal resize events."""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_resize, daemon=True)
            self._monitor_thread.start()
    
    def stop_resize_monitoring(self):
        """Stop monitoring terminal resize events."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    @contextmanager
    def managed_terminal(self):
        """Context manager for terminal state management."""
        try:
            self.hide_cursor()
            self.start_resize_monitoring()
            yield self
        finally:
            self.show_cursor()
            self.stop_resize_monitoring()


class PerformanceMonitor:
    """
    Real-time performance monitoring and optimization.
    """
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.stats = PerformanceStats()
        self.start_time = time.time()
        self.last_update = self.start_time
        self.frame_times = []
        self.max_frame_history = 60  # Keep last 60 frame times
        
        # System monitoring
        self.process = psutil.Process()
        self.cpu_percent = 0.0
        
        # Performance tracking
        self._monitoring = False
        self._monitor_thread = None
    
    def start_monitoring(self):
        """Start background performance monitoring."""
        if not self._monitoring:
            self._monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
            self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background performance monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_performance(self):
        """Background performance monitoring loop."""
        while self._monitoring:
            try:
                # Update CPU usage
                self.cpu_percent = self.process.cpu_percent()
                
                # Update memory usage
                memory_info = self.process.memory_info()
                self.stats.memory_usage = memory_info.rss / 1024 / 1024  # MB
                
                time.sleep(0.5)  # Update every 500ms
            except Exception:
                pass
    
    def record_frame(self, frame_start_time: float):
        """
        Record frame processing time and update statistics.
        
        Args:
            frame_start_time: Time when frame processing started
        """
        current_time = time.time()
        frame_time = current_time - frame_start_time
        
        # Update frame times history
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        
        # Update statistics
        self.stats.frames_processed += 1
        self.stats.frame_time = frame_time
        
        # Calculate FPS from recent frame times
        if len(self.frame_times) > 1:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.stats.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Update system stats periodically
        if current_time - self.last_update >= self.update_interval:
            self.stats.cpu_usage = self.cpu_percent
            self.last_update = current_time
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.
        
        Returns:
            Dictionary with performance metrics
        """
        runtime = time.time() - self.start_time
        
        return {
            'fps': round(self.stats.fps, 2),
            'frame_time_ms': round(self.stats.frame_time * 1000, 2),
            'cpu_usage_percent': round(self.stats.cpu_usage, 1),
            'memory_usage_mb': round(self.stats.memory_usage, 1),
            'frames_processed': self.stats.frames_processed,
            'dropped_frames': self.stats.dropped_frames,
            'runtime_seconds': round(runtime, 1),
            'avg_fps': round(self.stats.frames_processed / runtime, 2) if runtime > 0 else 0
        }
    
    def should_drop_frame(self, target_fps: float) -> bool:
        """
        Determine if frame should be dropped to maintain target FPS.
        
        Args:
            target_fps: Target frames per second
            
        Returns:
            True if frame should be dropped
        """
        if target_fps <= 0 or len(self.frame_times) < 5:
            return False
        
        current_fps = self.stats.fps
        return current_fps < target_fps * 0.8  # Drop if significantly below target
    
    def get_adaptive_quality_settings(self) -> Dict[str, Any]:
        """
        Get adaptive quality settings based on performance.
        
        Returns:
            Dictionary with recommended settings
        """
        settings = {
            'use_threading': True,
            'enhance_contrast': True,
            'max_workers': 4
        }
        
        # Reduce quality if performance is poor
        if self.stats.fps < 15:
            settings['use_threading'] = False
            settings['enhance_contrast'] = False
        elif self.stats.fps < 25:
            settings['max_workers'] = 2
        
        # Adjust based on CPU usage
        if self.stats.cpu_usage > 80:
            settings['max_workers'] = max(1, settings['max_workers'] - 1)
            settings['enhance_contrast'] = False
        
        return settings


class ColorManager:
    """Manage terminal colors and styling."""
    
    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
    }
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        if os.name == 'nt':
            # Windows might not support colors
            return text
        return f"{cls.COLORS.get(color, '')}{text}{cls.COLORS['reset']}"
    
    @classmethod
    def progress_bar(cls, progress: float, width: int = 30) -> str:
        """Create a colored progress bar."""
        filled = int(progress * width)
        bar = '█' * filled + '░' * (width - filled)
        
        if progress < 0.3:
            color = 'red'
        elif progress < 0.7:
            color = 'yellow'
        else:
            color = 'green'
        
        return cls.colorize(bar, color)
