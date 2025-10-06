"""
Core ASCII Video Player with advanced features and real-time optimization.
"""

import cv2
import time
import threading
import queue
from typing import Optional, Callable, Dict, Any, Tuple
from pathlib import Path
import logging

from .converter import ASCIIConverter, ASCIIStyle, ConversionAlgorithm
from .utils import TerminalManager, PerformanceMonitor, ColorManager


class ASCIIVideoPlayer:
    """
    Professional ASCII video player with advanced features:
    - Real-time terminal resize handling
    - Multi-threaded frame processing
    - Adaptive quality control
    - Performance monitoring
    - Multiple playback modes
    """
    
    def __init__(self, 
                 style: ASCIIStyle = ASCIIStyle.DETAILED,
                 algorithm: ConversionAlgorithm = ConversionAlgorithm.LUMINANCE,
                 enable_performance_monitor: bool = True,
                 enable_resize_handling: bool = True,
                 buffer_size: int = 10):
        """
        Initialize the ASCII video player.
        
        Args:
            style: ASCII character set style
            algorithm: Brightness calculation algorithm
            enable_performance_monitor: Enable real-time performance monitoring
            enable_resize_handling: Enable dynamic terminal resize handling
            buffer_size: Frame buffer size for smooth playback
        """
        # Core components
        self.converter = ASCIIConverter(style=style, algorithm=algorithm)
        self.terminal = TerminalManager()
        self.performance = PerformanceMonitor() if enable_performance_monitor else None
        self.color_manager = ColorManager()
        
        # Configuration
        self.enable_resize_handling = enable_resize_handling
        self.buffer_size = buffer_size
        
        # Playback state
        self.is_playing = False
        self.is_paused = False
        self.current_frame = 0
        self.total_frames = 0
        self.video_fps = 30.0
        self.playback_speed = 1.0
        
        # Threading and buffering
        self.frame_buffer = queue.Queue(maxsize=buffer_size)
        self.buffer_thread = None
        self.display_thread = None
        self.stop_event = threading.Event()
        
        # Media capture
        self.cap = None
        self.media_path = None
        self.static_image = None
        self.is_image = False
        
        # Display settings
        self.ascii_width = 80
        self.ascii_height = 24
        self.show_ui = True
        self.show_performance = True
        self.quality_mode = "auto"
        # Rendering options
        self.hq_video = False  # Disable high-quality upscaling for videos by default
        self.reduce_flicker = True  # Use cursor-home redraws instead of full clear
        self.lock_dimensions = False  # When true, ignore terminal resizes
        self.char_px_w = 10  # assumed character cell width in pixels (for 1440p mapping)
        self.char_px_h = 20  # assumed character cell height in pixels
        
        # Callbacks
        self.on_frame_callback = None
        self.on_resize_callback = None
        
        # Setup resize handling
        if enable_resize_handling:
            self.terminal.register_resize_callback(self._handle_resize)
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def load_media(self, media_path: str) -> bool:
        """
        Load a video or image file for playback/display.
        
        Args:
            media_path: Path to the video or image file
            
        Returns:
            True if media loaded successfully
        """
        try:
            media_path = Path(media_path)
            if not media_path.exists():
                self.logger.error(f"Media file not found: {media_path}")
                return False
            
            # Check if it's an image or video
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif', '.ico', '.ppm', '.pgm', '.pbm'}
            video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.3gp', '.ogv'}
            
            file_ext = media_path.suffix.lower()
            
            # Release previous media if any
            if self.cap:
                self.cap.release()
            
            self.media_path = str(media_path)
            self.is_image = file_ext in image_extensions
            
            if self.is_image:
                return self._load_image(media_path)
            else:
                return self._load_video(media_path)
            
        except Exception as e:
            self.logger.error(f"Error loading media: {e}")
            return False
    
    def _load_image(self, image_path: Path) -> bool:
        """Load a static image."""
        try:
            # Load image using OpenCV
            image = cv2.imread(str(image_path))
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Store image for display
            self.static_image = image
            self.total_frames = 1
            self.video_fps = 1.0  # Not applicable for images
            self.current_frame = 0
            
            # Calculate ASCII dimensions
            frame_height, frame_width = image.shape[:2]
            if self.lock_dimensions:
                self.ascii_width, self.ascii_height = self._compute_1440p_ascii_size((frame_height, frame_width))
            else:
                terminal_width, terminal_height = self.terminal.get_terminal_size()
                self.ascii_width, self.ascii_height = self.converter.get_optimal_dimensions(
                    terminal_width, terminal_height, (frame_height, frame_width), self.quality_mode
                )
            
            self.logger.info(f"Loaded image: {image_path.name}")
            self.logger.info(f"Resolution: {frame_width}x{frame_height}")
            self.logger.info(f"ASCII size: {self.ascii_width}x{self.ascii_height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading image: {e}")
            return False
    
    def _load_video(self, video_path: Path) -> bool:
        """Load a video file."""
        try:
            # Load new video
            self.cap = cv2.VideoCapture(str(video_path))
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open video: {video_path}")
                return False
            
            # Get video properties
            self.static_image = None  # Clear any previous image
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
            
            # Calculate optimal ASCII dimensions
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if self.lock_dimensions:
                self.ascii_width, self.ascii_height = self._compute_1440p_ascii_size((frame_height, frame_width))
            else:
                terminal_width, terminal_height = self.terminal.get_terminal_size()
                # Avoid double upscaling for videos unless HQ explicitly enabled
                effective_quality = self.quality_mode if self.hq_video else "standard"
                self.ascii_width, self.ascii_height = self.converter.get_optimal_dimensions(
                    terminal_width, terminal_height, (frame_height, frame_width), effective_quality
                )
            
            self.logger.info(f"Loaded video: {video_path.name}")
            self.logger.info(f"Resolution: {frame_width}x{frame_height}")
            self.logger.info(f"FPS: {self.video_fps}")
            self.logger.info(f"Frames: {self.total_frames}")
            self.logger.info(f"ASCII size: {self.ascii_width}x{self.ascii_height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading video: {e}")
            return False
    
    # Keep backward compatibility
    def load_video(self, video_path: str) -> bool:
        """Backward compatibility method."""
        return self.load_media(video_path)
    
    def _handle_resize(self, old_size: Tuple[int, int], new_size: Tuple[int, int]):
        """Handle terminal resize events."""
        if self.lock_dimensions:
            # Ignore resize when dimensions are locked
            return
        if self.is_image and self.static_image is not None:
            # Handle image resize
            frame_height, frame_width = self.static_image.shape[:2]
            self.ascii_width, self.ascii_height = self.converter.get_optimal_dimensions(
                new_size[0], new_size[1], (frame_height, frame_width), self.quality_mode
            )
        elif self.cap and self.cap.isOpened():
            # Handle video resize
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.ascii_width, self.ascii_height = self.converter.get_optimal_dimensions(
                new_size[0], new_size[1], (frame_height, frame_width), self.quality_mode
            )
        
        self.logger.info(f"Terminal resized: {old_size} -> {new_size}")
        self.logger.info(f"New ASCII size: {self.ascii_width}x{self.ascii_height}")
        
        # Call user callback if set
        if self.on_resize_callback:
            self.on_resize_callback(old_size, new_size)

    def _compute_1440p_ascii_size(self, frame_shape: Tuple[int, int]) -> Tuple[int, int]:
        """Compute ASCII width/height approximating 2560x1440 output using char pixel size.
        Caps to current terminal size and preserves frame aspect with character aspect.
        """
        term_w, term_h = self.terminal.get_terminal_size()
        frame_h, frame_w = frame_shape
        frame_aspect = frame_w / max(1, frame_h)
        char_aspect = self.char_px_w / max(1, self.char_px_h)  # width/height in pixels per char
        # Target 2560x1440 pixels translated into character grid
        target_cols = max(1, int(2560 / self.char_px_w))
        target_rows = max(1, int(1440 / self.char_px_h))
        # Compute base fit within target char grid while honoring frame and char aspect
        # Height from width:
        h_from_w = int((target_cols / frame_aspect) * (self.char_px_h / self.char_px_w))
        if h_from_w <= target_rows:
            cols = target_cols
            rows = h_from_w
        else:
            # Width from height
            cols = int((target_rows * frame_aspect) * (self.char_px_w / self.char_px_h))
            rows = target_rows
        # Leave small margin for UI
        cols = max(1, min(cols, term_w - 2))
        rows = max(1, min(rows, term_h - 2))
        return cols, rows

    def set_lock_1440p(self, enabled: bool, char_px_w: int = None, char_px_h: int = None):
        """Enable/disable 1440p-locked non-resizable mode and optionally set char pixel size."""
        self.lock_dimensions = enabled
        if char_px_w:
            self.char_px_w = max(4, min(32, int(char_px_w)))
        if char_px_h:
            self.char_px_h = max(8, min(64, int(char_px_h)))
        # Recompute sizes if media loaded
        try:
            if enabled:
                if self.is_image and self.static_image is not None:
                    fh, fw = self.static_image.shape[:2]
                    self.ascii_width, self.ascii_height = self._compute_1440p_ascii_size((fh, fw))
                elif self.cap and self.cap.isOpened():
                    fw = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    fh = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.ascii_width, self.ascii_height = self._compute_1440p_ascii_size((fh, fw))
        except Exception:
            pass
    
    def _buffer_frames(self):
        """Background thread for frame buffering."""
        if self.is_image:
            # For static images, just put the image once
            if self.static_image is not None and self.frame_buffer.qsize() == 0:
                try:
                    self.frame_buffer.put((0, self.static_image), timeout=0.1)
                except queue.Full:
                    pass
            # Keep thread alive but don't do anything else for images
            while not self.stop_event.is_set():
                time.sleep(0.1)
        else:
            # Original video buffering logic
            while not self.stop_event.is_set() and self.cap and self.cap.isOpened():
                if self.frame_buffer.qsize() < self.buffer_size and not self.is_paused:
                    ret, frame = self.cap.read()
                    if ret:
                        try:
                            self.frame_buffer.put((self.current_frame, frame), timeout=0.1)
                            self.current_frame += 1
                        except queue.Full:
                            pass  # Buffer full, skip frame
                    else:
                        # End of video
                        break
                else:
                    time.sleep(0.01)  # Small delay to prevent busy waiting
    
    def _display_frames(self):
        """Background thread for frame display."""
        last_display_time = time.time()
        last_speed = self.playback_speed
        first_frame_rendered = False
        
        while not self.stop_event.is_set():
            # Recalculate target delay if speed changed
            current_speed = self.playback_speed
            if abs(current_speed - last_speed) > 0.01:
                last_display_time = time.time()  # Reset timing when speed changes
                last_speed = current_speed
            
            target_frame_delay = 1.0 / (self.video_fps * current_speed)
            
            if self.is_paused:
                time.sleep(0.1)
                last_display_time = time.time()  # Reset timing when unpaused
                continue
            
            try:
                # Get frame from buffer
                frame_num, frame = self.frame_buffer.get(timeout=0.1)
                
                # Record performance
                frame_start_time = time.time()
                if self.performance:
                    self.performance.record_frame(frame_start_time)
                
                # Convert to ASCII
                ascii_art = self.converter.convert_frame_to_ascii(
                    frame, self.ascii_width, self.ascii_height
                )
                
                # Clear or move cursor and display
                if self.reduce_flicker and first_frame_rendered:
                    # Move cursor to home to overwrite previous frame
                    self.terminal.cursor_home()
                else:
                    # Do a full clear on first frame or when flicker reduction disabled
                    self.terminal.clear_screen()
                print(ascii_art)
                
                # Display UI if enabled
                if self.show_ui:
                    self._display_ui(frame_num)
                
                # Call user callback if set
                if self.on_frame_callback:
                    self.on_frame_callback(frame_num, frame, ascii_art)
                
                # For static images, just wait for user input instead of timing
                if self.is_image:
                    # Display image indefinitely until user interaction
                    while not self.stop_event.is_set() and not self.is_paused:
                        time.sleep(0.1)
                    first_frame_rendered = True
                    continue
                
                # Improved frame timing for videos - account for processing time
                current_time = time.time()
                processing_time = current_time - frame_start_time
                
                # Calculate how long we should wait based on target FPS
                # Subtract the processing time from the target delay
                sleep_time = max(0, target_frame_delay - processing_time)
                
                # Additional timing adjustment to maintain consistent frame rate
                time_since_last_frame = current_time - last_display_time
                if time_since_last_frame < target_frame_delay:
                    additional_sleep = target_frame_delay - time_since_last_frame
                    sleep_time = max(sleep_time, additional_sleep)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                last_display_time = time.time()
                first_frame_rendered = True
                
            except queue.Empty:
                # No frames available, small delay
                time.sleep(0.01)
            except Exception as e:
                self.logger.error(f"Display error: {e}")
                break
    
    def _display_ui(self, frame_num: int):
        """Display user interface elements."""
        try:
            if self.is_image:
                # Image-specific UI
                status = "DISPLAYING"
                status_color = "green"
                status_text = self.color_manager.colorize(status, status_color)
                
                # Performance info
                perf_text = ""
                if self.show_performance and self.performance:
                    stats = self.performance.get_performance_summary()
                    perf_text = f" | CPU: {stats['cpu_usage_percent']}% | Memory: {stats['memory_usage_mb']:.1f}MB"
                
                # Display UI line for images
                ui_line = f"📷 {status_text} | Static Image | ASCII: {self.ascii_width}x{self.ascii_height}{perf_text}"
                print(ui_line)
                
                # Controls help for images
                help_text = self.color_manager.colorize(
                    "Controls: Q=quit, F=toggle UI, R=refresh", "dim"
                )
                print(help_text)
            else:
                # Video-specific UI
                # Progress bar
                progress = frame_num / self.total_frames if self.total_frames > 0 else 0
                progress_bar = self.color_manager.progress_bar(progress, 40)
                
                # Status info
                status = "PAUSED" if self.is_paused else "PLAYING"
                status_color = "yellow" if self.is_paused else "green"
                status_text = self.color_manager.colorize(status, status_color)
                
                # Time info
                current_time = frame_num / self.video_fps if self.video_fps > 0 else 0
                total_time = self.total_frames / self.video_fps if self.video_fps > 0 else 0
                time_text = f"{current_time:.1f}s / {total_time:.1f}s"
                
                # Performance info
                perf_text = ""
                if self.show_performance and self.performance:
                    stats = self.performance.get_performance_summary()
                    perf_text = f" | FPS: {stats['fps']} | CPU: {stats['cpu_usage_percent']}%"
                
                # Display UI line for videos
                ui_line = f"{progress_bar} {status_text} | {time_text} | Speed: {self.playback_speed}x{perf_text}"
                print(ui_line)
                
                # Controls help for videos
                help_text = self.color_manager.colorize(
                    "Controls: SPACE=pause, Q=quit, +/-=speed, R=restart", "dim"
                )
                print(help_text)
            
        except Exception as e:
            self.logger.error(f"UI display error: {e}")
    
    def play(self, 
             show_ui: bool = True, 
             show_performance: bool = True,
             fullscreen: bool = False) -> bool:
        """
        Start media playback/display.
        
        Args:
            show_ui: Show playback UI
            show_performance: Show performance statistics
            fullscreen: Use fullscreen mode (hide UI)
            
        Returns:
            True if playback started successfully
        """
        # Check if media is loaded (either image or video)
        if self.is_image:
            if self.static_image is None:
                self.logger.error("No image loaded")
                return False
        else:
            if not self.cap or not self.cap.isOpened():
                self.logger.error("No video loaded")
                return False
        
        self.show_ui = show_ui and not fullscreen
        self.show_performance = show_performance
        self.is_playing = True
        self.is_paused = False
        self.stop_event.clear()
        
        try:
            # Start performance monitoring
            if self.performance:
                self.performance.start_monitoring()
            
            # Start background threads
            self.buffer_thread = threading.Thread(target=self._buffer_frames, daemon=True)
            self.display_thread = threading.Thread(target=self._display_frames, daemon=True)
            
            with self.terminal.managed_terminal():
                self.buffer_thread.start()
                self.display_thread.start()
                
                # Handle user input
                self._handle_input()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Playback interrupted by user")
            return True
        except Exception as e:
            self.logger.error(f"Playback error: {e}")
            return False
        finally:
            self.stop()
    
    def _handle_input(self):
        """Handle user input during playback."""
        import sys
        import os
        
        if os.name == 'nt':
            # Windows input handling
            import msvcrt
            while self.is_playing:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    self._process_key(key)
                time.sleep(0.1)
        else:
            # Unix input handling
            import tty, termios, select
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                while self.is_playing:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).lower()
                        self._process_key(key)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def _process_key(self, key: str):
        """Process keyboard input."""
        if key == 'q':
            self.stop()
        elif key == ' ':
            self.toggle_pause()
        elif key == '+' or key == '=':
            self.change_speed(0.1)
        elif key == '-':
            self.change_speed(-0.1)
        elif key == 'r':
            self.restart()
        elif key == 'f':
            self.show_ui = not self.show_ui
        elif key == 'p':
            self.show_performance = not self.show_performance
    
    def stop(self):
        """Stop video playback."""
        self.is_playing = False
        self.stop_event.set()
        
        # Wait for threads to finish
        if self.buffer_thread and self.buffer_thread.is_alive():
            self.buffer_thread.join(timeout=1.0)
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1.0)
        
        # Stop performance monitoring
        if self.performance:
            self.performance.stop_monitoring()
        
        # Clear frame buffer
        while not self.frame_buffer.empty():
            try:
                self.frame_buffer.get_nowait()
            except queue.Empty:
                break
    
    def toggle_pause(self):
        """Toggle playback pause state."""
        self.is_paused = not self.is_paused
        self.logger.info(f"Playback {'paused' if self.is_paused else 'resumed'}")
    
    def change_speed(self, delta: float):
        """Change playback speed."""
        old_speed = self.playback_speed
        self.playback_speed = max(0.1, min(5.0, self.playback_speed + delta))
        
        # If speed changed significantly, reset timing in display thread
        if abs(self.playback_speed - old_speed) > 0.05:
            # This will be picked up by the display thread on next iteration
            pass
            
        self.logger.info(f"Playback speed: {self.playback_speed}x")
    
    def set_quality_mode(self, quality_mode: str):
        """Set the quality mode for resolution enhancement."""
        self.quality_mode = quality_mode
        self.logger.info(f"Quality mode set to: {quality_mode}")
        
        # Recalculate dimensions if media is loaded
        if self.is_image and self.static_image is not None:
            frame_height, frame_width = self.static_image.shape[:2]
            terminal_width, terminal_height = self.terminal.get_terminal_size()
            self.ascii_width, self.ascii_height = self.converter.get_optimal_dimensions(
                terminal_width, terminal_height, (frame_height, frame_width), self.quality_mode
            )
        elif self.cap and self.cap.isOpened():
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            terminal_width, terminal_height = self.terminal.get_terminal_size()
            self.ascii_width, self.ascii_height = self.converter.get_optimal_dimensions(
                terminal_width, terminal_height, (frame_height, frame_width), self.quality_mode
            )
    
    def restart(self):
        """Restart video from beginning."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.current_frame = 0
            # Clear buffer
            while not self.frame_buffer.empty():
                try:
                    self.frame_buffer.get_nowait()
                except queue.Empty:
                    break
            self.logger.info("Video restarted")
    
    def seek(self, frame_number: int):
        """Seek to specific frame."""
        if self.cap and 0 <= frame_number < self.total_frames:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_frame = frame_number
            # Clear buffer
            while not self.frame_buffer.empty():
                try:
                    self.frame_buffer.get_nowait()
                except queue.Empty:
                    break
            self.logger.info(f"Seeked to frame {frame_number}")
    
    def get_media_info(self) -> Dict[str, Any]:
        """Get comprehensive media information."""
        info = {
            'path': self.media_path,
            'ascii_width': self.ascii_width,
            'ascii_height': self.ascii_height,
            'playback_speed': self.playback_speed,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'is_image': self.is_image
        }
        
        if self.is_image and self.static_image is not None:
            height, width = self.static_image.shape[:2]
            info.update({
                'width': width,
                'height': height,
                'fps': 'N/A (Static Image)',
                'total_frames': 1,
                'duration': 'N/A (Static Image)',
                'current_frame': 0,
                'media_type': 'Image'
            })
        elif self.cap:
            info.update({
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.video_fps,
                'total_frames': self.total_frames,
                'duration': self.total_frames / self.video_fps if self.video_fps > 0 else 0,
                'current_frame': self.current_frame,
                'media_type': 'Video'
            })
        
        return info
    
    # Keep backward compatibility
    def get_video_info(self) -> Dict[str, Any]:
        """Backward compatibility method."""
        return self.get_media_info()
    
    def cleanup(self):
        """Clean up resources."""
        self.stop()
        if self.cap:
            self.cap.release()
        self.converter.cleanup()
        self.terminal.stop_resize_monitoring()
        if self.performance:
            self.performance.stop_monitoring()
