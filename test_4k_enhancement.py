#!/usr/bin/env python3
"""
Test script to demonstrate 4K/6K enhancement capabilities
"""

import sys
from pathlib import Path
import numpy as np
import cv2
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ascii_video import ASCIIVideoPlayer
from ascii_video.converter import ASCIIStyle, ConversionAlgorithm


def create_high_res_test_image():
    """Create a high-resolution test image with fine details."""
    # Create a 4K test image (3840x2160)
    width, height = 1920, 1080  # Use 1080p for testing (4K might be too large for demo)
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create complex patterns to test upscaling
    for y in range(height):
        for x in range(width):
            # Create a complex pattern with fine details
            r = int(128 + 127 * np.sin(x * 0.01) * np.cos(y * 0.01))
            g = int(128 + 127 * np.sin(x * 0.02) * np.cos(y * 0.02))
            b = int(128 + 127 * np.sin(x * 0.03) * np.cos(y * 0.03))
            image[y, x] = [b, g, r]  # BGR format
    
    # Add some geometric shapes for edge detection testing
    cv2.circle(image, (width//4, height//4), 100, (255, 255, 255), 2)
    cv2.rectangle(image, (width//2, height//4), (width//2 + 200, height//4 + 150), (0, 255, 0), 3)
    
    # Add fine text-like patterns
    for i in range(10):
        y_pos = height//2 + i * 20
        cv2.line(image, (width//4, y_pos), (3*width//4, y_pos), (255, 255, 255), 1)
        for j in range(0, width//2, 10):
            cv2.line(image, (width//4 + j, y_pos - 5), (width//4 + j, y_pos + 5), (255, 255, 255), 1)
    
    return image


def test_algorithms():
    """Test different enhancement algorithms."""
    print("🚀 Testing 4K/6K Enhancement Algorithms")
    print("=" * 60)
    
    # Create test image
    test_image = create_high_res_test_image()
    test_image_path = "test_4k.png"
    cv2.imwrite(test_image_path, test_image)
    
    algorithms = [
        ('standard', ConversionAlgorithm.LUMINANCE),
        ('edge_enhanced', ConversionAlgorithm.EDGE_ENHANCED),
        ('super_resolution', ConversionAlgorithm.SUPER_RESOLUTION),
        ('adaptive_4k', ConversionAlgorithm.ADAPTIVE_4K),
        ('neural_upscale', ConversionAlgorithm.NEURAL_UPSCALE)
    ]
    
    quality_modes = ['standard', '4k', '6k']
    
    for alg_name, algorithm in algorithms:
        print(f"\n🔍 Testing Algorithm: {alg_name.upper()}")
        print("-" * 40)
        
        for quality in quality_modes:
            print(f"  📊 Quality Mode: {quality}")
            
            # Create player with specific algorithm
            player = ASCIIVideoPlayer(
                style=ASCIIStyle.DETAILED,
                algorithm=algorithm
            )
            
            # Set quality mode
            player.set_quality_mode(quality)
            
            # Load image
            start_time = time.time()
            if player.load_media(test_image_path):
                load_time = time.time() - start_time
                
                info = player.get_media_info()
                print(f"    ✓ Loaded: {info['width']}x{info['height']} -> {info['ascii_width']}x{info['ascii_height']}")
                print(f"    ⏱️  Load time: {load_time:.3f}s")
                
                # Test conversion performance
                start_time = time.time()
                ascii_art = player.converter.convert_frame_to_ascii(
                    test_image, info['ascii_width'], info['ascii_height']
                )
                convert_time = time.time() - start_time
                
                print(f"    🎨 ASCII chars: {len(ascii_art)}")
                print(f"    ⚡ Convert time: {convert_time:.3f}s")
                
                # Show quality metrics
                lines = ascii_art.split('\n')
                avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
                print(f"    📏 Avg line length: {avg_line_length:.1f}")
                
            else:
                print("    ❌ Failed to load image")
            
            player.cleanup()
    
    # Cleanup
    Path(test_image_path).unlink(missing_ok=True)
    
    print("\n" + "=" * 60)
    print("🎉 4K/6K Enhancement Testing Complete!")
    print("\nRecommendations:")
    print("• Use 'adaptive_4k' for best quality/performance balance")
    print("• Use 'neural_upscale' for maximum detail preservation")
    print("• Use 'super_resolution' for sharp edge enhancement")
    print("• Use 'auto' quality mode for intelligent scaling")


def demo_quality_comparison():
    """Demonstrate quality differences between modes."""
    print("\n🎭 Quality Mode Comparison Demo")
    print("=" * 40)
    
    # Create simple test pattern
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    
    # Create checkerboard pattern
    for y in range(200):
        for x in range(200):
            if (x // 10 + y // 10) % 2:
                test_image[y, x] = [255, 255, 255]
    
    test_path = "quality_test.png"
    cv2.imwrite(test_path, test_image)
    
    quality_modes = ['standard', '4k', '6k', '8k']
    
    for quality in quality_modes:
        print(f"\n📊 Quality Mode: {quality.upper()}")
        
        player = ASCIIVideoPlayer(algorithm=ConversionAlgorithm.ADAPTIVE_4K)
        player.set_quality_mode(quality)
        
        if player.load_media(test_path):
            info = player.get_media_info()
            scale_factor = (info['ascii_width'] * info['ascii_height']) / (200 * 200)
            print(f"  📐 Dimensions: {info['ascii_width']}x{info['ascii_height']}")
            print(f"  📈 Scale factor: {scale_factor:.2f}x")
            
            # Show first few lines of ASCII
            ascii_art = player.converter.convert_frame_to_ascii(
                test_image, info['ascii_width'], info['ascii_height']
            )
            lines = ascii_art.split('\n')[:3]
            print(f"  🎨 Sample output:")
            for line in lines:
                print(f"    {line[:50]}{'...' if len(line) > 50 else ''}")
        
        player.cleanup()
    
    Path(test_path).unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        test_algorithms()
        demo_quality_comparison()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
