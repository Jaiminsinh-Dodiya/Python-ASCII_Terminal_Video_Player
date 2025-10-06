#!/usr/bin/env python3
"""
Setup script for ASCII Video Player
Handles installation, dependency checking, and environment setup.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def upgrade_build_tools():
    """Ensure pip, setuptools, and wheel are up-to-date for Python 3.13 compatibility."""
    print("🛠️  Upgrading build tools (pip, setuptools, wheel)...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Build tools upgraded successfully")
            return True
        else:
            print(f"⚠️  Warning: Could not upgrade build tools: {result.stderr}")
            # Continue anyway; sometimes it's already sufficient
            return True
    except Exception as e:
        print(f"⚠️  Warning: Exception while upgrading build tools: {e}")
        return True


def install_requirements():
    """Install required packages."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Error: requirements.txt not found")
        return False
    
    print("📦 Installing required packages...")
    
    try:
        # Install packages
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All packages installed successfully")
            return True
        else:
            print(f"❌ Error installing packages: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False


def check_opencv():
    """Check if OpenCV is working properly."""
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
        
        # Test basic functionality
        cap = cv2.VideoCapture()
        cap.release()
        
        return True
    except ImportError:
        print("❌ OpenCV not found or not working")
        return False
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False


def check_terminal_support():
    """Check terminal capabilities."""
    print("🖥️  Checking terminal support...")
    
    # Check terminal size detection
    try:
        if hasattr(os, 'get_terminal_size'):
            size = os.get_terminal_size()
            print(f"✓ Terminal size: {size.columns}x{size.lines}")
        else:
            print("⚠️  Warning: Terminal size detection may not work on this system")
    except Exception:
        print("⚠️  Warning: Could not detect terminal size")
    
    # Check color support
    if os.name == 'nt':
        try:
            import colorama
            print("✓ Windows color support available")
        except ImportError:
            print("⚠️  Warning: colorama not available for Windows color support")
    else:
        print("✓ Unix-like system detected (color support expected)")
    
    return True


def create_demo_script():
    """Create a demo launcher script."""
    demo_script = Path(__file__).parent / "demo.py"
    
    demo_content = '''#!/usr/bin/env python3
"""
Quick demo launcher for ASCII Video Player
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from main import main
import click

if __name__ == "__main__":
    # Run with demo flag
    sys.argv = ["demo.py", "--demo"]
    main()
'''
    
    try:
        with open(demo_script, 'w') as f:
            f.write(demo_content)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(demo_script, 0o755)
        
        print(f"✓ Demo script created: {demo_script}")
        return True
    except Exception as e:
        print(f"⚠️  Could not create demo script: {e}")
        return False


def run_tests():
    """Run basic functionality tests."""
    print("🧪 Running basic tests...")
    
    try:
        # Import test module
        sys.path.insert(0, str(Path(__file__).parent))
        import test_player
        
        # Run tests
        test_player.run_all_tests()
        return True
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("ASCII Video Player v2.0 - Setup")
    print("=" * 60)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Upgrade build tools first for Python 3.13 compatibility
    if success:
        upgrade_build_tools()
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Check OpenCV
    if success and not check_opencv():
        success = False
    
    # Check terminal support
    if success:
        check_terminal_support()
    
    # Create demo script
    if success:
        create_demo_script()
    
    # Run tests
    if success:
        print("\n" + "=" * 60)
        run_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nYou can now run the ASCII Video Player:")
        print("  python main.py --demo                 # Run demo")
        print("  python main.py path/to/video.mp4     # Play specific video")
        print("  python demo.py                       # Quick demo launcher")
        print("\nFor help:")
        print("  python main.py --help")
    else:
        print("❌ Setup failed. Please check the errors above.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
