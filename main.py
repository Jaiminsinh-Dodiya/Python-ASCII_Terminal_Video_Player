#!/usr/bin/env python3
"""
Professional ASCII Video Player
A high-performance, feature-rich video player that renders videos as ASCII art in terminal.

Author: Jaiminsinh Dodiya
Version: 2.0.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ascii_video import ASCIIVideoPlayer
from ascii_video.converter import ASCIIStyle, ConversionAlgorithm
from ascii_video.utils import ColorManager


# Setup rich console
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


def display_banner():
    """Display application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    ASCII VIDEO PLAYER v2.0                   ║
    ║              Professional Terminal Video Player              ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  • Real-time terminal resize handling                        ║
    ║  • Multi-threaded frame processing                           ║
    ║  • Adaptive quality control                                  ║
    ║  • Performance monitoring                                    ║
    ║  • Multiple ASCII styles and algorithms                      ║
    ║                                                              ║
    ║  Author: Jaiminsinh Dodiya                                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold red"))


def display_media_info(player: ASCIIVideoPlayer):
    """Display media information in a formatted table."""
    info = player.get_media_info()
    if not info:
        return
    
    title = f"{info.get('media_type', 'Media')} Information"
    table = Table(title=title, style="cyan")
    table.add_column("Property", style="bold")
    table.add_column("Value")
    
    table.add_row("File", Path(info['path']).name)
    table.add_row("Type", info.get('media_type', 'Unknown'))
    table.add_row("Resolution", f"{info['width']}x{info['height']}")
    
    if info['is_image']:
        table.add_row("Format", "Static Image")
    else:
        table.add_row("FPS", f"{info['fps']:.2f}")
        table.add_row("Duration", f"{info['duration']:.2f}s")
        table.add_row("Total Frames", str(info['total_frames']))
    
    table.add_row("ASCII Size", f"{info['ascii_width']}x{info['ascii_height']}")
    
    console.print(table)


def display_controls():
    """Display playback controls."""
    controls = Table(title="Playback Controls", style="green")
    controls.add_column("Key", style="bold")
    controls.add_column("Action")
    
    controls.add_row("SPACE", "Pause/Resume")
    controls.add_row("Q", "Quit")
    controls.add_row("+/=", "Increase Speed")
    controls.add_row("-", "Decrease Speed")
    controls.add_row("R", "Restart")
    controls.add_row("F", "Toggle UI")
    controls.add_row("P", "Toggle Performance Stats")
    
    console.print(controls)


@click.command()
@click.argument('media_path', type=click.Path(exists=True), required=False)
@click.option('--style', '-s', 
              type=click.Choice(['minimal', 'detailed', 'blocks', 'gradient', 'light', 'dark']),
              default='detailed',
              help='ASCII character set style')
@click.option('--algorithm', '-a',
              type=click.Choice(['luminance', 'average', 'lightness', 'custom', 'edge_enhanced', 'super_resolution', 'adaptive_4k', 'neural_upscale']),
              default='adaptive_4k',
              help='Brightness calculation algorithm')
@click.option('--width', '-w', type=int, default=0,
              help='ASCII width (0 for auto)')
@click.option('--height', '-h', type=int, default=0,
              help='ASCII height (0 for auto)')
@click.option('--fps', '-f', type=float, default=0,
              help='Playback FPS (0 for original)')
@click.option('--speed', type=float, default=1.0,
              help='Playback speed multiplier')
@click.option('--no-ui', is_flag=True,
              help='Disable UI overlay')
@click.option('--no-performance', is_flag=True,
              help='Disable performance monitoring')
@click.option('--fullscreen', is_flag=True,
              help='Fullscreen mode (no UI)')
@click.option('--buffer-size', type=int, default=10,
              help='Frame buffer size')
@click.option('--threads', type=int, default=4,
              help='Number of processing threads')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose logging')
@click.option('--demo', is_flag=True,
              help='Run with demo video')
@click.option('--quality', '-q',
              type=click.Choice(['standard', '4k', '6k', '8k', 'auto']),
              default='auto',
              help='Output quality mode for resolution enhancement')
@click.option('--hq-video', is_flag=True, default=False,
              help='Enable high-quality upscaling for videos (may be heavy)')
@click.option('--no-flicker', is_flag=True, default=False,
              help='Disable flicker reduction (uses full screen clears)')
@click.option('--lock-1440p', is_flag=True, default=False,
              help='Lock ASCII size to 1440p-equivalent grid (non-resizable)')
@click.option('--char-px-w', type=int, default=10,
              help='Approx character cell width in pixels (for 1440p mapping)')
@click.option('--char-px-h', type=int, default=20,
              help='Approx character cell height in pixels (for 1440p mapping)')
def main(media_path: Optional[str], style: str, algorithm: str, width: int, height: int,
         fps: float, speed: float, no_ui: bool, no_performance: bool, fullscreen: bool,
         buffer_size: int, threads: int, verbose: bool, demo: bool, quality: str,
         hq_video: bool, no_flicker: bool, lock_1440p: bool, char_px_w: int, char_px_h: int):
    """
    Professional ASCII Media Player with 4K/6K Enhancement
    
    Display videos and images as ASCII art in your terminal with advanced features and optimizations.
    
    Supported formats:
    - Videos: MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V, 3GP, OGV
    - Images: JPG, PNG, BMP, TIFF, WebP, GIF, ICO, PPM, PGM, PBM
    
    Advanced Algorithms:
    - adaptive_4k: Multi-scale 4K enhancement with bilateral filtering
    - neural_upscale: Neural network-inspired upscaling with guided filtering
    - super_resolution: EDSR-inspired super-resolution with unsharp masking
    - edge_enhanced: Sobel edge detection with brightness enhancement
    
    Quality Modes:
    - auto: Automatically detects optimal quality based on input resolution
    - 4k/6k/8k: Force high-resolution output with advanced upscaling
    - standard: Basic quality for performance-critical scenarios
    """
    
    # Setup logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Display banner
    display_banner()
    
    # Handle demo mode
    if demo:
        demo_path = Path(__file__).parent / "vid.mp4"
        if demo_path.exists():
            media_path = str(demo_path)
            console.print(f"[green]Using demo video: {demo_path.name}[/green]")
        else:
            console.print("[red]Demo video not found![/red]")
            return
    
    # Get media path if not provided
    if not media_path:
        media_path = console.input("[cyan]Enter media file path (video or image): [/cyan]").strip()
        if not media_path or not Path(media_path).exists():
            console.print("[red]Invalid media path![/red]")
            return
    
    # Map style names to enums
    style_map = {
        'minimal': ASCIIStyle.MINIMAL,
        'detailed': ASCIIStyle.DETAILED,
        'blocks': ASCIIStyle.BLOCKS,
        'gradient': ASCIIStyle.GRADIENT,
        'light': ASCIIStyle.CUSTOM_LIGHT,
        'dark': ASCIIStyle.CUSTOM_DARK
    }
    
    # Map algorithm names to enums
    algorithm_map = {
        'luminance': ConversionAlgorithm.LUMINANCE,
        'average': ConversionAlgorithm.AVERAGE,
        'lightness': ConversionAlgorithm.LIGHTNESS,
        'custom': ConversionAlgorithm.CUSTOM_WEIGHTED,
        'edge_enhanced': ConversionAlgorithm.EDGE_ENHANCED,
        'super_resolution': ConversionAlgorithm.SUPER_RESOLUTION,
        'adaptive_4k': ConversionAlgorithm.ADAPTIVE_4K,
        'neural_upscale': ConversionAlgorithm.NEURAL_UPSCALE
    }
    
    try:
        # Create player with specified settings
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing player...", total=None)
            
            player = ASCIIVideoPlayer(
                style=style_map[style],
                algorithm=algorithm_map[algorithm],
                enable_performance_monitor=not no_performance,
                enable_resize_handling=True,
                buffer_size=buffer_size
            )
            
            progress.update(task, description="Loading video...")
            
            # Set quality mode before loading media
            player.set_quality_mode(quality)
            # Apply rendering preferences
            player.hq_video = hq_video
            player.reduce_flicker = not no_flicker
            # Apply 1440p lock if requested
            if lock_1440p:
                player.set_lock_1440p(True, char_px_w=char_px_w, char_px_h=char_px_h)
            
            # Load media (video or image)
            if not player.load_media(media_path):
                console.print("[red]Failed to load media![/red]")
                return
            
            progress.update(task, description="Setting up playback...")
            
            # Apply custom settings
            if width > 0:
                player.ascii_width = width
            if height > 0:
                player.ascii_height = height
            if speed != 1.0:
                player.playback_speed = speed
        
        # Display media information
        display_media_info(player)
        
        # Display controls
        if not fullscreen and not no_ui:
            display_controls()
        
        # Wait for user to start
        if not console.input("\n[green]Press Enter to start playback (or Ctrl+C to exit)...[/green]"):
            pass
        
        console.clear()
        
        # Start playback
        success = player.play(
            show_ui=not no_ui,
            show_performance=not no_performance,
            fullscreen=fullscreen
        )
        
        if success:
            console.print("\n[green]Playback completed successfully![/green]")
            
            # Show final performance stats
            if not no_performance and player.performance:
                stats = player.performance.get_performance_summary()
                
                perf_table = Table(title="Performance Summary", style="yellow")
                perf_table.add_column("Metric", style="bold")
                perf_table.add_column("Value")
                
                perf_table.add_row("Average FPS", f"{stats['avg_fps']:.2f}")
                perf_table.add_row("Frames Processed", str(stats['frames_processed']))
                perf_table.add_row("Runtime", f"{stats['runtime_seconds']:.1f}s")
                perf_table.add_row("CPU Usage", f"{stats['cpu_usage_percent']:.1f}%")
                perf_table.add_row("Memory Usage", f"{stats['memory_usage_mb']:.1f} MB")
                
                console.print(perf_table)
        else:
            console.print("[red]Playback failed![/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Playback interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
    finally:
        # Cleanup
        if 'player' in locals():
            player.cleanup()
        console.print("[dim]Goodbye![/dim]")


if __name__ == "__main__":
    main()
