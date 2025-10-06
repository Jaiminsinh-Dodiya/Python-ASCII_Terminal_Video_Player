"""
Advanced ASCII Conversion Engine
Supports multiple algorithms and character sets for optimal ASCII art generation.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor


class ASCIIStyle(Enum):
    """Different ASCII character sets for various visual styles."""
    MINIMAL = " .:-=+*#%@"
    DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    BLOCKS = " ░▒▓█"
    GRADIENT = " ▁▂▃▄▅▆▇█"
    CUSTOM_LIGHT = " .·-=+*oO#@"
    CUSTOM_DARK = "@#*+=-·. "


class ConversionAlgorithm(Enum):
    """Different algorithms for brightness calculation."""
    LUMINANCE = "luminance"
    AVERAGE = "average"
    LIGHTNESS = "lightness"
    CUSTOM_WEIGHTED = "custom_weighted"
    EDGE_ENHANCED = "edge_enhanced"
    SUPER_RESOLUTION = "super_resolution"
    ADAPTIVE_4K = "adaptive_4k"
    NEURAL_UPSCALE = "neural_upscale"


class ASCIIConverter:
    """
    High-performance ASCII converter with multiple algorithms and optimizations.
    """
    
    def __init__(self, 
                 style: ASCIIStyle = ASCIIStyle.DETAILED,
                 algorithm: ConversionAlgorithm = ConversionAlgorithm.LUMINANCE,
                 use_threading: bool = True,
                 max_workers: int = 4):
        """
        Initialize the ASCII converter.
        
        Args:
            style: ASCII character set to use
            algorithm: Brightness calculation algorithm
            use_threading: Enable multi-threading for performance
            max_workers: Maximum number of worker threads
        """
        self.style = style
        self.algorithm = algorithm
        self.use_threading = use_threading
        self.max_workers = max_workers
        self.ascii_chars = style.value
        self.char_count = len(self.ascii_chars)
        
        # Pre-calculate character mapping for performance
        self._char_map = np.array(list(self.ascii_chars))
        
        # Threading setup
        if use_threading:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        else:
            self.executor = None
    
    def calculate_brightness(self, pixel_values: np.ndarray) -> np.ndarray:
        """
        Calculate brightness using the selected algorithm.
        
        Args:
            pixel_values: RGB pixel values
            
        Returns:
            Normalized brightness values (0-1)
        """
        if self.algorithm == ConversionAlgorithm.LUMINANCE:
            # Standard luminance formula (ITU-R BT.709)
            return 0.2126 * pixel_values[:, :, 2] + 0.7152 * pixel_values[:, :, 1] + 0.0722 * pixel_values[:, :, 0]
        
        elif self.algorithm == ConversionAlgorithm.AVERAGE:
            return np.mean(pixel_values, axis=2)
        
        elif self.algorithm == ConversionAlgorithm.LIGHTNESS:
            return (np.max(pixel_values, axis=2) + np.min(pixel_values, axis=2)) / 2
        
        elif self.algorithm == ConversionAlgorithm.CUSTOM_WEIGHTED:
            # Custom weighting for better contrast
            return 0.3 * pixel_values[:, :, 2] + 0.59 * pixel_values[:, :, 1] + 0.11 * pixel_values[:, :, 0]
        
        elif self.algorithm == ConversionAlgorithm.EDGE_ENHANCED:
            # Edge-enhanced brightness with Sobel edge detection
            return self._edge_enhanced_brightness(pixel_values)
        
        elif self.algorithm == ConversionAlgorithm.SUPER_RESOLUTION:
            # Super-resolution brightness calculation
            return self._super_resolution_brightness(pixel_values)
        
        elif self.algorithm == ConversionAlgorithm.ADAPTIVE_4K:
            # Adaptive 4K enhancement
            return self._adaptive_4k_brightness(pixel_values)
        
        elif self.algorithm == ConversionAlgorithm.NEURAL_UPSCALE:
            # Neural network-inspired upscaling
            return self._neural_upscale_brightness(pixel_values)
        
        else:
            return np.mean(pixel_values, axis=2)
    
    def _edge_enhanced_brightness(self, pixel_values: np.ndarray) -> np.ndarray:
        """Edge-enhanced brightness calculation using Sobel edge detection."""
        # Convert to grayscale first
        gray = 0.2126 * pixel_values[:, :, 2] + 0.7152 * pixel_values[:, :, 1] + 0.0722 * pixel_values[:, :, 0]
        
        # Apply Sobel edge detection
        sobel_x = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        
        # Calculate edge magnitude
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        edge_magnitude = np.clip(edge_magnitude / 255.0, 0, 1)
        
        # Combine original brightness with edge information
        enhanced = gray / 255.0 + 0.3 * edge_magnitude
        return np.clip(enhanced, 0, 1)
    
    def _super_resolution_brightness(self, pixel_values: np.ndarray) -> np.ndarray:
        """Super-resolution brightness using bicubic interpolation and sharpening."""
        # Convert to grayscale
        gray = 0.2126 * pixel_values[:, :, 2] + 0.7152 * pixel_values[:, :, 1] + 0.0722 * pixel_values[:, :, 0]
        gray_normalized = gray / 255.0
        
        # Apply unsharp masking for enhanced detail
        blurred = cv2.GaussianBlur(gray_normalized.astype(np.float32), (3, 3), 1.0)
        sharpened = gray_normalized + 0.5 * (gray_normalized - blurred)
        
        # Apply adaptive histogram equalization for better contrast
        gray_uint8 = (np.clip(sharpened, 0, 1) * 255).astype(np.uint8)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray_uint8)
        
        return enhanced / 255.0
    
    def _adaptive_4k_brightness(self, pixel_values: np.ndarray) -> np.ndarray:
        """Adaptive 4K enhancement with multi-scale processing."""
        # Multi-scale luminance calculation
        luminance = 0.2126 * pixel_values[:, :, 2] + 0.7152 * pixel_values[:, :, 1] + 0.0722 * pixel_values[:, :, 0]
        luminance_norm = luminance / 255.0
        
        # Apply bilateral filter for noise reduction while preserving edges
        filtered = cv2.bilateralFilter(luminance.astype(np.uint8), 9, 75, 75)
        filtered_norm = filtered / 255.0
        
        # Multi-scale detail enhancement
        scales = [1, 2, 4]
        enhanced = filtered_norm.copy()
        
        for scale in scales:
            if scale > 1:
                # Downsample
                small = cv2.resize(filtered_norm, None, fx=1/scale, fy=1/scale, interpolation=cv2.INTER_AREA)
                # Upsample back
                upsampled = cv2.resize(small, (filtered_norm.shape[1], filtered_norm.shape[0]), 
                                     interpolation=cv2.INTER_CUBIC)
                # Add detail
                detail = filtered_norm - upsampled
                enhanced += 0.3 * detail / scale
        
        return np.clip(enhanced, 0, 1)
    
    def _neural_upscale_brightness(self, pixel_values: np.ndarray) -> np.ndarray:
        """Neural network-inspired upscaling using advanced interpolation."""
        # Convert to LAB color space for better perceptual processing
        lab = cv2.cvtColor(pixel_values.astype(np.uint8), cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0] / 255.0
        
        # Apply morphological operations for structure preservation
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(l_channel.astype(np.float32), cv2.MORPH_OPEN, kernel)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        
        # Apply guided filter-like operation
        mean_I = cv2.boxFilter(l_channel.astype(np.float32), cv2.CV_32F, (5, 5))
        mean_p = cv2.boxFilter(closed, cv2.CV_32F, (5, 5))
        corr_Ip = cv2.boxFilter(l_channel.astype(np.float32) * closed, cv2.CV_32F, (5, 5))
        cov_Ip = corr_Ip - mean_I * mean_p
        
        mean_II = cv2.boxFilter(l_channel.astype(np.float32) * l_channel.astype(np.float32), cv2.CV_32F, (5, 5))
        var_I = mean_II - mean_I * mean_I
        
        eps = 0.01
        a = cov_Ip / (var_I + eps)
        b = mean_p - a * mean_I
        
        mean_a = cv2.boxFilter(a, cv2.CV_32F, (5, 5))
        mean_b = cv2.boxFilter(b, cv2.CV_32F, (5, 5))
        
        enhanced = mean_a * l_channel + mean_b
        return np.clip(enhanced, 0, 1)
    
    def resize_frame_smart(self, frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """
        Advanced smart frame resizing with 4K/6K upscaling and quality optimization.
        
        Args:
            frame: Input frame
            target_width: Target width
            target_height: Target height
            
        Returns:
            Resized frame with enhanced quality
        """
        # Calculate optimal dimensions maintaining aspect ratio
        frame_height, frame_width = frame.shape[:2]
        aspect_ratio = frame_width / frame_height
        
        # Adjust for character aspect ratio (characters are typically taller than wide)
        char_aspect_ratio = 0.5  # Typical character height/width ratio
        adjusted_height = int(target_width / aspect_ratio * char_aspect_ratio)
        
        if adjusted_height > target_height:
            adjusted_height = target_height
            target_width = int(adjusted_height * aspect_ratio / char_aspect_ratio)
        
        # Determine if we need upscaling (4K/6K enhancement)
        scale_factor_x = target_width / frame_width
        scale_factor_y = adjusted_height / frame_height
        max_scale_factor = max(scale_factor_x, scale_factor_y)
        
        if max_scale_factor > 2.0:
            # High-resolution upscaling for 4K/6K output
            return self._super_resolution_resize(frame, target_width, adjusted_height)
        elif max_scale_factor > 1.5:
            # Medium upscaling with edge preservation
            return self._edge_preserving_resize(frame, target_width, adjusted_height)
        else:
            # Standard high-quality resize
            return cv2.resize(frame, (target_width, adjusted_height), interpolation=cv2.INTER_LANCZOS4)
    
    def _super_resolution_resize(self, frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """Super-resolution upscaling for 4K/6K quality."""
        # Multi-step upscaling for better quality
        current_frame = frame.copy()
        current_width, current_height = frame.shape[1], frame.shape[0]
        
        # Calculate intermediate steps
        steps = []
        while current_width < target_width or current_height < target_height:
            next_width = min(current_width * 2, target_width)
            next_height = min(current_height * 2, target_height)
            steps.append((next_width, next_height))
            current_width, current_height = next_width, next_height
        
        # Apply multi-step upscaling
        for step_width, step_height in steps:
            # Use EDSR-inspired upscaling
            current_frame = self._edsr_upscale(current_frame, step_width, step_height)
        
        # Final resize to exact dimensions
        if current_frame.shape[1] != target_width or current_frame.shape[0] != target_height:
            current_frame = cv2.resize(current_frame, (target_width, target_height), 
                                     interpolation=cv2.INTER_LANCZOS4)
        
        return current_frame
    
    def _edsr_upscale(self, frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """EDSR-inspired upscaling algorithm."""
        # Apply bilateral filter for noise reduction
        denoised = cv2.bilateralFilter(frame, 9, 75, 75)
        
        # Initial upscale with bicubic interpolation
        upscaled = cv2.resize(denoised, (target_width, target_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply unsharp masking for detail enhancement
        blurred = cv2.GaussianBlur(upscaled.astype(np.float32), (3, 3), 1.0)
        sharpened = upscaled.astype(np.float32) + 0.7 * (upscaled.astype(np.float32) - blurred)
        
        # Apply CLAHE for adaptive contrast enhancement
        if len(frame.shape) == 3:
            # Convert to LAB for better contrast enhancement
            lab = cv2.cvtColor(np.clip(sharpened, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(np.clip(sharpened, 0, 255).astype(np.uint8))
        
        return enhanced
    
    def _edge_preserving_resize(self, frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """Edge-preserving resize for medium upscaling."""
        # Apply edge-preserving smoothing
        smoothed = cv2.edgePreservingFilter(frame, flags=2, sigma_s=50, sigma_r=0.4)
        
        # Resize with high-quality interpolation
        resized = cv2.resize(smoothed, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Apply guided filter for detail preservation
        if len(frame.shape) == 3:
            # Convert to grayscale for guided filter
            gray_guide = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_resized = cv2.resize(gray_guide, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Apply guided filter to each channel
            enhanced = resized.copy()
            for i in range(3):
                enhanced[:, :, i] = self._guided_filter(gray_resized.astype(np.float32), 
                                                      resized[:, :, i].astype(np.float32), 
                                                      radius=8, eps=0.01)
        else:
            enhanced = self._guided_filter(resized.astype(np.float32), resized.astype(np.float32), 
                                         radius=8, eps=0.01)
        
        return np.clip(enhanced, 0, 255).astype(np.uint8)
    
    def _guided_filter(self, guide: np.ndarray, src: np.ndarray, radius: int, eps: float) -> np.ndarray:
        """Guided filter implementation for detail preservation."""
        mean_I = cv2.boxFilter(guide, cv2.CV_32F, (radius, radius))
        mean_p = cv2.boxFilter(src, cv2.CV_32F, (radius, radius))
        corr_Ip = cv2.boxFilter(guide * src, cv2.CV_32F, (radius, radius))
        cov_Ip = corr_Ip - mean_I * mean_p
        
        mean_II = cv2.boxFilter(guide * guide, cv2.CV_32F, (radius, radius))
        var_I = mean_II - mean_I * mean_I
        
        a = cov_Ip / (var_I + eps)
        b = mean_p - a * mean_I
        
        mean_a = cv2.boxFilter(a, cv2.CV_32F, (radius, radius))
        mean_b = cv2.boxFilter(b, cv2.CV_32F, (radius, radius))
        
        return mean_a * guide + mean_b
    
    def convert_frame_chunk(self, brightness_chunk: np.ndarray, start_row: int) -> List[str]:
        """
        Convert a chunk of brightness values to ASCII characters.
        
        Args:
            brightness_chunk: Chunk of brightness values
            start_row: Starting row index
            
        Returns:
            List of ASCII strings for each row
        """
        result = []
        for row in brightness_chunk:
            # Vectorized character mapping for performance
            indices = (row * (self.char_count - 1)).astype(np.int32)
            indices = np.clip(indices, 0, self.char_count - 1)
            ascii_row = ''.join(self._char_map[indices])
            result.append(ascii_row)
        return result
    
    def convert_frame_to_ascii(self, 
                             frame: np.ndarray, 
                             width: int, 
                             height: Optional[int] = None,
                             enhance_contrast: bool = True) -> str:
        """
        Convert a video frame to ASCII art with advanced optimizations.
        
        Args:
            frame: Input video frame
            width: Target ASCII width
            height: Target ASCII height (auto-calculated if None)
            enhance_contrast: Apply contrast enhancement
            
        Returns:
            ASCII art string
        """
        if frame is None or frame.size == 0:
            return ""
        
        # Auto-calculate height if not provided
        if height is None:
            frame_height, frame_width = frame.shape[:2]
            height = int(frame_height * width / frame_width * 0.5)  # 0.5 for character aspect ratio
        
        # Ensure minimum dimensions
        width = max(1, width)
        height = max(1, height)
        
        # Resize frame with smart algorithm
        resized_frame = self.resize_frame_smart(frame, width, height)
        
        # Convert to grayscale if needed
        if len(resized_frame.shape) == 3:
            if self.algorithm == ConversionAlgorithm.LUMINANCE:
                # Use custom luminance calculation for better quality
                brightness = self.calculate_brightness(resized_frame.astype(np.float32))
            else:
                gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                brightness = gray_frame.astype(np.float32)
        else:
            brightness = resized_frame.astype(np.float32)
        
        # Normalize to 0-1 range
        brightness = brightness / 255.0
        
        # Enhance contrast if requested
        if enhance_contrast:
            # Apply histogram equalization for better contrast
            brightness = np.power(brightness, 0.8)  # Gamma correction
            brightness = np.clip(brightness, 0, 1)
        
        # Multi-threaded conversion for large frames
        if self.use_threading and height > 50:
            chunk_size = max(1, height // self.max_workers)
            chunks = []
            futures = []
            
            for i in range(0, height, chunk_size):
                chunk = brightness[i:i + chunk_size]
                future = self.executor.submit(self.convert_frame_chunk, chunk, i)
                futures.append(future)
            
            # Collect results
            ascii_lines = []
            for future in futures:
                ascii_lines.extend(future.result())
        else:
            # Single-threaded conversion
            ascii_lines = self.convert_frame_chunk(brightness, 0)
        
        return '\n'.join(ascii_lines)
    
    def get_optimal_dimensions(self, terminal_width: int, terminal_height: int, 
                             frame_shape: Tuple[int, int], 
                             quality_mode: str = "auto") -> Tuple[int, int]:
        """
        Calculate optimal ASCII dimensions with 4K/6K support for given terminal size and frame.
        
        Args:
            terminal_width: Terminal width in characters
            terminal_height: Terminal height in characters
            frame_shape: Original frame shape (height, width)
            quality_mode: Quality mode ("auto", "4k", "6k", "8k", "standard")
            
        Returns:
            Optimal (width, height) for ASCII conversion
        """
        frame_height, frame_width = frame_shape
        frame_aspect = frame_width / frame_height
        
        # Account for character aspect ratio
        char_aspect = 0.5
        
        # Determine quality multiplier based on mode and input resolution
        if quality_mode == "auto":
            # Auto-detect based on input resolution and terminal size
            input_pixels = frame_width * frame_height
            terminal_chars = terminal_width * terminal_height
            
            if input_pixels >= 8294400:  # 4K (3840x2160) or higher
                quality_multiplier = 3.0  # Ultra-high quality
            elif input_pixels >= 2073600:  # 1080p (1920x1080)
                quality_multiplier = 2.5  # High quality
            elif input_pixels >= 921600:   # 720p (1280x720)
                quality_multiplier = 2.0   # Enhanced quality
            else:
                quality_multiplier = 1.5   # Standard enhanced
        elif quality_mode == "8k":
            quality_multiplier = 4.0
        elif quality_mode == "6k":
            quality_multiplier = 3.5
        elif quality_mode == "4k":
            quality_multiplier = 3.0
        else:  # standard
            quality_multiplier = 1.0
        
        # Calculate base dimensions that fit in terminal
        if terminal_width / terminal_height > frame_aspect * char_aspect:
            # Height is limiting factor
            base_height = terminal_height - 2  # Leave space for UI
            base_width = int(base_height * frame_aspect / char_aspect)
        else:
            # Width is limiting factor
            base_width = terminal_width - 2  # Leave space for UI
            base_height = int(base_width / frame_aspect * char_aspect)
        
        # Apply quality multiplier for high-resolution output
        enhanced_width = int(base_width * quality_multiplier)
        enhanced_height = int(base_height * quality_multiplier)
        
        # Ensure we don't exceed reasonable limits (prevent memory issues)
        max_width = min(terminal_width * 4, 1000)  # Cap at 4x terminal width or 1000
        max_height = min(terminal_height * 4, 800)  # Cap at 4x terminal height or 800
        
        final_width = min(enhanced_width, max_width)
        final_height = min(enhanced_height, max_height)
        
        return max(1, final_width), max(1, final_height)
    
    def cleanup(self):
        """Clean up resources."""
        if self.executor:
            self.executor.shutdown(wait=True)
