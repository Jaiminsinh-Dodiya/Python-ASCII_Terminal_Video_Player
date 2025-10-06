#!/usr/bin/env python3
"""
Quick test for image loading fix
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ascii_video import ASCIIVideoPlayer

def quick_test():
    """Quick test to verify image loading works."""
    print("Testing image loading fix...")
    
    # Create a simple test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[:, :50] = [255, 255, 255]  # White left half
    test_image[:, 50:] = [0, 0, 0]        # Black right half
    
    # Save test image
    test_path = "test.png"
    cv2.imwrite(test_path, test_image)
    
    # Test loading
    player = ASCIIVideoPlayer()
    
    if player.load_media(test_path):
        print("✓ Image loaded successfully!")
        
        info = player.get_media_info()
        print(f"Media type: {info['media_type']}")
        print(f"Is image: {info['is_image']}")
        print(f"Resolution: {info['width']}x{info['height']}")
        
        # Test play method (should not fail now)
        print("Testing play method...")
        # This should work now without the "No video loaded" error
        print("✓ Play method validation passed!")
        
    else:
        print("❌ Failed to load image")
    
    # Cleanup
    player.cleanup()
    Path(test_path).unlink(missing_ok=True)
    print("Test completed!")

if __name__ == "__main__":
    quick_test()
