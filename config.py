"""
Configuration management for ASCII Video Player.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from ascii_video.converter import ASCIIStyle, ConversionAlgorithm


@dataclass
class PlayerConfig:
    """Configuration settings for the ASCII video player."""
    
    # Display settings
    ascii_style: str = "detailed"
    conversion_algorithm: str = "luminance"
    default_width: int = 0  # 0 for auto
    default_height: int = 0  # 0 for auto
    
    # Performance settings
    buffer_size: int = 10
    max_threads: int = 4
    enable_performance_monitor: bool = True
    enable_resize_handling: bool = True
    
    # Playback settings
    default_speed: float = 1.0
    show_ui: bool = True
    show_performance: bool = True
    
    # Quality settings
    enhance_contrast: bool = True
    use_threading: bool = True
    
    # Advanced settings
    frame_drop_threshold: float = 0.8
    cpu_usage_threshold: float = 80.0
    memory_limit_mb: float = 500.0


class ConfigManager:
    """Manage configuration loading, saving, and validation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            config_path = Path.home() / ".ascii_video_config.json"
        
        self.config_path = config_path
        self.config = PlayerConfig()
        self.load_config()
    
    def load_config(self) -> bool:
        """
        Load configuration from file.
        
        Returns:
            True if config loaded successfully
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Update config with loaded data
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                return True
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
        
        return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if config saved successfully
        """
        try:
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
            return False
    
    def get_style_enum(self) -> ASCIIStyle:
        """Get ASCII style enum from config."""
        style_map = {
            'minimal': ASCIIStyle.MINIMAL,
            'detailed': ASCIIStyle.DETAILED,
            'blocks': ASCIIStyle.BLOCKS,
            'gradient': ASCIIStyle.GRADIENT,
            'light': ASCIIStyle.CUSTOM_LIGHT,
            'dark': ASCIIStyle.CUSTOM_DARK
        }
        return style_map.get(self.config.ascii_style, ASCIIStyle.DETAILED)
    
    def get_algorithm_enum(self) -> ConversionAlgorithm:
        """Get conversion algorithm enum from config."""
        algorithm_map = {
            'luminance': ConversionAlgorithm.LUMINANCE,
            'average': ConversionAlgorithm.AVERAGE,
            'lightness': ConversionAlgorithm.LIGHTNESS,
            'custom': ConversionAlgorithm.CUSTOM_WEIGHTED
        }
        return algorithm_map.get(self.config.conversion_algorithm, ConversionAlgorithm.LUMINANCE)
    
    def update_from_args(self, **kwargs):
        """Update configuration from command line arguments."""
        for key, value in kwargs.items():
            if hasattr(self.config, key) and value is not None:
                setattr(self.config, key, value)
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = PlayerConfig()
    
    def validate_config(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Validate ranges
            if not (0 <= self.config.buffer_size <= 100):
                return False
            
            if not (1 <= self.config.max_threads <= 16):
                return False
            
            if not (0.1 <= self.config.default_speed <= 10.0):
                return False
            
            if not (0 <= self.config.default_width <= 1000):
                return False
            
            if not (0 <= self.config.default_height <= 1000):
                return False
            
            # Validate enums
            valid_styles = ['minimal', 'detailed', 'blocks', 'gradient', 'light', 'dark']
            if self.config.ascii_style not in valid_styles:
                return False
            
            valid_algorithms = ['luminance', 'average', 'lightness', 'custom']
            if self.config.conversion_algorithm not in valid_algorithms:
                return False
            
            return True
        except Exception:
            return False


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> PlayerConfig:
    """Get current configuration."""
    return config_manager.config


def save_config() -> bool:
    """Save current configuration."""
    return config_manager.save_config()


def load_config() -> bool:
    """Load configuration from file."""
    return config_manager.load_config()


# Preset configurations
PRESETS = {
    'performance': PlayerConfig(
        ascii_style='minimal',
        conversion_algorithm='average',
        buffer_size=5,
        max_threads=2,
        enhance_contrast=False,
        use_threading=False,
        show_performance=False
    ),
    
    'quality': PlayerConfig(
        ascii_style='detailed',
        conversion_algorithm='luminance',
        buffer_size=20,
        max_threads=8,
        enhance_contrast=True,
        use_threading=True,
        show_performance=True
    ),
    
    'minimal': PlayerConfig(
        ascii_style='blocks',
        conversion_algorithm='average',
        buffer_size=3,
        max_threads=1,
        enhance_contrast=False,
        use_threading=False,
        show_ui=False,
        show_performance=False
    ),
    
    'presentation': PlayerConfig(
        ascii_style='gradient',
        conversion_algorithm='luminance',
        buffer_size=15,
        max_threads=4,
        enhance_contrast=True,
        use_threading=True,
        show_ui=True,
        show_performance=False
    )
}


def apply_preset(preset_name: str) -> bool:
    """
    Apply a preset configuration.
    
    Args:
        preset_name: Name of the preset to apply
        
    Returns:
        True if preset applied successfully
    """
    if preset_name in PRESETS:
        config_manager.config = PRESETS[preset_name]
        return True
    return False


def list_presets() -> list:
    """Get list of available presets."""
    return list(PRESETS.keys())
