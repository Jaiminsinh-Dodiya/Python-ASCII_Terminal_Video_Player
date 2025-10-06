"""
ASCII Video Player - Professional Video to ASCII Art Converter
A high-performance, feature-rich video player that renders videos as ASCII art in terminal.
"""

__version__ = "2.0.0"
__author__ = "Jaiminsinh Dodiya"
__description__ = "Professional ASCII Video Player with Advanced Features"

from .core import ASCIIVideoPlayer
from .converter import ASCIIConverter
from .utils import TerminalManager, PerformanceMonitor

__all__ = [
    'ASCIIVideoPlayer',
    'ASCIIConverter', 
    'TerminalManager',
    'PerformanceMonitor'
]
