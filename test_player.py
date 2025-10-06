#!/usr/bin/env python3
"""
Test script for ASCII Video Player
Quick testing and validation of core functionality.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ascii_video import ASCIIVideoPlayer
from ascii_video.converter import ASCIIStyle, ConversionAlgorithm
from ascii_video.utils import TerminalManager, PerformanceMonitor


def test_terminal_manager():
    """Test terminal management functionality."""
    print("Testing Terminal Manager...")
    
    terminal = TerminalManager()
    
    # Test terminal size detection
    width, height = terminal.get_terminal_size()
    print(f"Terminal size: {width}x{height}")
    
    # Test resize monitoring
    def on_resize(old_size, new_size):
        print(f"Resize detected: {old_size} -> {new_size}")
    
    terminal.register_resize_callback(on_resize)
    terminal.start_resize_monitoring()
    
    print("Resize monitoring started (resize terminal to test)")
    time.sleep(3)
    
    terminal.stop_resize_monitoring()
    print("Terminal manager test completed ✓")


def test_performance_monitor():
    """Test performance monitoring functionality."""
    print("\nTesting Performance Monitor...")
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # Simulate frame processing
    for i in range(10):
        start_time = time.time()
        time.sleep(0.1)  # Simulate processing
        monitor.record_frame(start_time)
    
    stats = monitor.get_performance_summary()
    print(f"Performance stats: {stats}")
    
    monitor.stop_monitoring()
    print("Performance monitor test completed ✓")


def test_ascii_converter():
    """Test ASCII conversion functionality."""
    print("\nTesting ASCII Converter...")
    
    try:
        import cv2
        import numpy as np
        
        from ascii_video.converter import ASCIIConverter
        
        # Create test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test different styles
        styles = [ASCIIStyle.MINIMAL, ASCIIStyle.DETAILED, ASCIIStyle.BLOCKS]
        
        for style in styles:
            converter = ASCIIConverter(style=style)
            ascii_art = converter.convert_frame_to_ascii(test_image, 40, 20)
            print(f"Style {style.name}: {len(ascii_art)} characters")
            converter.cleanup()
        
        print("ASCII converter test completed ✓")
        
    except ImportError as e:
        print(f"Skipping ASCII converter test: {e}")


def test_video_loading():
    """Test video loading functionality."""
    print("\nTesting Video Loading...")
    
    # Check for demo video
    demo_video = Path(__file__).parent / "vid.mp4"
    
    if demo_video.exists():
        player = ASCIIVideoPlayer()
        
        if player.load_video(str(demo_video)):
            info = player.get_video_info()
            print(f"Video loaded successfully:")
            print(f"  Resolution: {info['width']}x{info['height']}")
            print(f"  FPS: {info['fps']}")
            print(f"  Duration: {info['duration']:.2f}s")
            print(f"  ASCII size: {info['ascii_width']}x{info['ascii_height']}")
        else:
            print("Failed to load demo video")
        
        player.cleanup()
        print("Video loading test completed ✓")
    else:
        print("Demo video not found, skipping video loading test")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("ASCII Video Player - Test Suite")
    print("=" * 60)
    
    try:
        test_terminal_manager()
        test_performance_monitor()
        test_ascii_converter()
        test_video_loading()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully! ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
