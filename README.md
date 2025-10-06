# ASCII Video Player v2.0 - 4K/6K Enhanced 🎬

A professional, high-performance media player that renders videos and images as ASCII art in your terminal with **4K/6K resolution enhancement**. Built with advanced features including real-time terminal resize handling, multi-threaded processing, neural-inspired upscaling algorithms, and adaptive quality control.

## 🚀 Features

### Core Features
- **Real-time ASCII Conversion**: Convert any video to ASCII art with multiple algorithms
- **Dynamic Terminal Resize**: Automatically adjusts to terminal size changes
- **Multi-threaded Processing**: Optimized performance with background frame buffering
- **Adaptive Quality Control**: Automatically adjusts quality based on performance
- **Multiple ASCII Styles**: Choose from 6 different character sets
- **Performance Monitoring**: Real-time FPS, CPU, and memory usage tracking

### Advanced Features
- **4K/6K Resolution Enhancement**: Advanced upscaling algorithms for ultra-high quality output
- **Neural-Inspired Upscaling**: EDSR-based super-resolution with guided filtering
- **Edge-Enhanced Processing**: Sobel edge detection with brightness enhancement
- **Multi-Scale Processing**: Adaptive 4K enhancement with bilateral filtering
- **Smart Frame Buffering**: Smooth playback with configurable buffer size
- **Image Format Support**: Display static images with all enhancement algorithms
- **Playback Controls**: Pause, speed control, seeking, and restart
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Professional CLI**: Rich command-line interface with comprehensive options
- **Logging & Debugging**: Comprehensive logging with different verbosity levels
- **Error Handling**: Robust error handling and recovery

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
- `opencv-python`: Video processing
- `numpy`: Numerical computations
- `rich`: Beautiful terminal output
- `click`: Command-line interface
- `colorama`: Cross-platform colored terminal text
- `psutil`: System and process utilities
- `pillow`: Image processing support

## 🎮 Usage

### Basic Usage
```bash
python main.py path/to/your/video.mp4
```

### Advanced Usage
```bash
# 4K Enhancement with neural upscaling
python main.py video.mp4 --algorithm neural_upscale --quality 4k

# 6K Super-resolution for images
python main.py photo.jpg --algorithm super_resolution --quality 6k --style detailed

# Edge-enhanced processing with auto quality
python main.py video.mp4 --algorithm edge_enhanced --quality auto

# Adaptive 4K with custom dimensions
python main.py media.mp4 --algorithm adaptive_4k --quality 4k --width 200 --height 100

# Maximum quality 8K mode
python main.py image.png --algorithm neural_upscale --quality 8k --style gradient

# Performance mode for slower systems
python main.py video.mp4 --algorithm luminance --quality standard --no-performance

# Demo mode (uses included demo video)
python main.py --demo --algorithm adaptive_4k --quality auto
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--style, -s` | ASCII character set (minimal, detailed, blocks, gradient, light, dark) | detailed |
| `--algorithm, -a` | Brightness algorithm (see algorithms section) | adaptive_4k |
| `--quality, -q` | Quality mode (standard, 4k, 6k, 8k, auto) | auto |
| `--width, -w` | ASCII width (0 for auto) | 0 |
| `--height, -h` | ASCII height (0 for auto) | 0 |
| `--fps, -f` | Playback FPS (0 for original) | 0 |
| `--speed` | Playback speed multiplier | 1.0 |
| `--no-ui` | Disable UI overlay | False |
| `--no-performance` | Disable performance monitoring | False |
| `--fullscreen` | Fullscreen mode (no UI) | False |
| `--buffer-size` | Frame buffer size | 10 |
| `--threads` | Number of processing threads | 4 |
| `--verbose, -v` | Verbose logging | False |
| `--demo` | Run with demo video | False |

### Playback Controls

| Key | Action |
|-----|--------|
| `SPACE` | Pause/Resume |
| `Q` | Quit |
| `+` or `=` | Increase Speed |
| `-` | Decrease Speed |
| `R` | Restart |
| `F` | Toggle UI |
| `P` | Toggle Performance Stats |

## 🎨 ASCII Styles & Algorithms

### Available Styles
1. **Minimal**: ` .:-=+*#%@` - Simple 10-character set
2. **Detailed**: Full 70-character set for maximum detail
3. **Blocks**: ` ░▒▓█` - Block characters for solid appearance
4. **Gradient**: ` ▁▂▃▄▅▆▇█` - Smooth gradient bars
5. **Light**: ` .·-=+*oO#@` - Optimized for light backgrounds
6. **Dark**: `@#*+=-·. ` - Optimized for dark backgrounds

### 🧠 Advanced Conversion Algorithms

#### Standard Algorithms
1. **Luminance**: ITU-R BT.709 standard (0.2126*R + 0.7152*G + 0.0722*B)
2. **Average**: Simple RGB average
3. **Lightness**: (max(RGB) + min(RGB)) / 2
4. **Custom**: Weighted formula for enhanced contrast

#### 🚀 4K/6K Enhancement Algorithms
5. **adaptive_4k**: Multi-scale 4K enhancement with bilateral filtering
   - Uses multi-scale detail enhancement
   - Applies bilateral filtering for noise reduction
   - Preserves edges while enhancing fine details
   - **Best for**: General purpose 4K enhancement

6. **neural_upscale**: Neural network-inspired upscaling
   - LAB color space processing for better perceptual quality
   - Guided filter-like operations for structure preservation
   - Morphological operations for edge enhancement
   - **Best for**: Maximum detail preservation

7. **super_resolution**: EDSR-inspired super-resolution
   - Unsharp masking for detail enhancement
   - CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - Multi-step upscaling for quality preservation
   - **Best for**: Sharp edge enhancement and text

8. **edge_enhanced**: Sobel edge detection enhancement
   - Sobel edge detection for boundary enhancement
   - Combines original brightness with edge information
   - Fast processing with good edge preservation
   - **Best for**: Images with strong geometric features

### 📊 Quality Modes

| Mode | Description | Use Case | Performance |
|------|-------------|----------|-------------|
| **standard** | Basic quality, 1x scaling | Fast performance, low-end systems | ⚡⚡⚡ |
| **auto** | Intelligent scaling based on input resolution | Balanced quality/performance | ⚡⚡ |
| **4k** | 3x scaling with advanced algorithms | High-quality output | ⚡ |
| **6k** | 3.5x scaling for ultra-high quality | Professional presentations | 🐌 |
| **8k** | 4x scaling for maximum quality | Extreme detail requirements | 🐌🐌 |

## 🔧 Technical Details

### Architecture
```
ascii_video/
├── __init__.py          # Package initialization
├── core.py              # Main player class with threading
├── converter.py         # ASCII conversion algorithms
└── utils.py             # Terminal management and monitoring
```

### Performance Optimizations
- **Vectorized Operations**: NumPy-based character mapping
- **Multi-threading**: Separate threads for buffering and display
- **Smart Resizing**: High-quality Lanczos interpolation
- **Adaptive Quality**: Dynamic quality adjustment based on performance
- **Memory Management**: Efficient frame buffering with size limits

### Cross-platform Compatibility
- **Windows**: Uses `msvcrt` for keyboard input, `colorama` for colors
- **Unix/Linux**: Uses `termios` and `select` for input handling
- **Terminal Detection**: Automatic terminal size detection with fallbacks

## 📊 Performance Monitoring

The application includes comprehensive performance monitoring:

- **Real-time FPS**: Current and average frames per second
- **CPU Usage**: Process CPU utilization percentage
- **Memory Usage**: RAM consumption in MB
- **Frame Statistics**: Processed and dropped frame counts
- **Timing**: Frame processing times and delays

## 🐛 Troubleshooting

### Common Issues

1. **Video won't load**
   - Check if the video file exists and is readable
   - Ensure OpenCV supports the video format
   - Try with a different video file

2. **Poor performance**
   - Reduce buffer size: `--buffer-size 5`
   - Disable performance monitoring: `--no-performance`
   - Use fewer threads: `--threads 2`
   - Use minimal ASCII style: `--style minimal`

3. **Terminal resize issues**
   - The application automatically handles resize events
   - If issues persist, restart the application
   - Check terminal compatibility

4. **Keyboard input not working**
   - Ensure terminal supports raw input mode
   - Try running with administrator/sudo privileges
   - Check if other applications are capturing input

### Debug Mode
Run with verbose logging to see detailed information:
```bash
python main.py video.mp4 --verbose
```

## 🎯 Use Cases

### Educational Presentations
- Demonstrate video processing concepts
- Show ASCII art generation algorithms
- Illustrate terminal-based applications

### Entertainment
- Watch videos in a unique ASCII format
- Create ASCII art recordings
- Terminal-based media center

### Development
- Test terminal applications
- Benchmark video processing performance
- Prototype ASCII-based interfaces

## 🔮 Future Enhancements

- [ ] Audio playback support
- [ ] Video recording to ASCII files
- [ ] Network streaming support
- [ ] Plugin system for custom converters
- [ ] Web interface for remote control
- [ ] Color ASCII support
- [ ] Subtitle support
- [ ] Playlist functionality

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Muhammad Abdul Bari**
- Professional ASCII Video Player v2.0
- Built with Python, OpenCV, and Rich

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

*Enjoy watching videos in ASCII art! 🎬✨*
