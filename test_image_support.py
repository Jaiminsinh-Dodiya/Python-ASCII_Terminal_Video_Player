#!/usr/bin/env python3
"""
Test script to demonstrate image support in ASCII Video Player
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ascii_video import ASCIIVideoPlayer
from ascii_video.converter import ASCIIStyle


def create_test_image():
    """Create a simple test image."""
    # Create a gradient image
    width, height = 400, 300
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a gradient from left to right
    for x in range(width):
        intensity = int((x / width) * 255)
        image[:, x] = [intensity, intensity, intensity]
    
    # Add some colored shapes
    # Red circle
    cv2.circle(image, (100, 100), 50, (0, 0, 255), -1)
    
    # Green rectangle
    cv2.rectangle(image, (200, 50), (350, 150), (0, 255, 0), -1)
    
    # Blue triangle
    pts = np.array([[300, 200], [250, 280], [350, 280]], np.int32)
    cv2.fillPoly(image, [pts], (255, 0, 0))
    
    return image


def test_image_support():
    """Test the image support functionality."""
    print("Testing ASCII Image Support...")
    
    # Create test image
    test_image = create_test_image()
    test_image_path = Path(__file__).parent / "test_image.png"
    
    # Save test image
    cv2.imwrite(str(test_image_path), test_image)
    print(f"Created test image: {test_image_path}")
    
    # Test loading image
    player = ASCIIVideoPlayer(style=ASCIIStyle.DETAILED)
    
    if player.load_media(str(test_image_path)):
        print("✓ Image loaded successfully!")
        
        # Get media info
        info = player.get_media_info()
        print(f"Media Type: {info['media_type']}")
        print(f"Resolution: {info['width']}x{info['height']}")
        print(f"ASCII Size: {info['ascii_width']}x{info['ascii_height']}")
        print(f"Is Image: {info['is_image']}")
        
        # Convert to ASCII
        ascii_art = player.converter.convert_frame_to_ascii(
            test_image, 80, 40
        )
        
        print("\nASCII Art Preview (first 10 lines):")
        print("-" * 80)
        lines = ascii_art.split('\n')[:10]
        for line in lines:
            print(line)
        print("-" * 80)
        
        print("\n✓ Image support working correctly!")
        
    else:
        print("❌ Failed to load image")
    
    # Cleanup
    player.cleanup()
    if test_image_path.exists():
        test_image_path.unlink()
        print(f"Cleaned up test image: {test_image_path}")


if __name__ == "__main__":
    test_image_support()
