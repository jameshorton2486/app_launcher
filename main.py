#!/usr/bin/env python3
"""
James's Project Launcher - Main Entry Point

A Windows desktop application for managing and launching development projects,
organizing downloads, and running system maintenance utilities.

Usage:
    python main.py              # Normal start
    python main.py --minimized  # Start minimized to tray
    pythonw main.py             # Start without console window
"""

import sys
import os
import argparse
import traceback
from pathlib import Path

# Ensure the app directory is in the path
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    APP_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    # Running from source
    APP_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = APP_DIR

sys.path.insert(0, str(APP_DIR))

# Set working directory to app location
os.chdir(APP_DIR)


def setup_logging():
    """Initialize the logging system."""
    try:
        from src.utils.logger import setup_logger, logger
        setup_logger()
        return logger
    except ImportError:
        # Fallback if logger module not available
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s'
        )
        return logging.getLogger(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler for uncaught exceptions.
    Logs the error and shows a user-friendly message.
    """
    # Don't intercept keyboard interrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Format error message
    error_msg = str(exc_value) if exc_value else "Unknown error"
    
    # Always print to console for visibility
    print(f"\n[CRITICAL] Uncaught exception: {error_msg}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("Check logs/app.log for full details.\n")
    
    # Log the exception
    try:
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    except Exception as log_err:
        print(f"[WARNING] Failed to log exception: {log_err}")
    
    # Try to show error dialog
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        # Create hidden root for dialog
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "App Launcher Error",
            f"An unexpected error occurred:\n\n{error_msg}\n\n"
            f"Please check logs/app.log for details."
        )
        root.destroy()
    except Exception as ui_err:
        print(f"[WARNING] Could not show error dialog: {ui_err}")


def check_dependencies():
    """
    Check that required dependencies are installed.
    Returns True if all dependencies are available.
    """
    missing = []
    required_packages = [
        ('customtkinter', 'customtkinter'),
        ('PIL', 'Pillow'),
        ('pystray', 'pystray'),
        ('keyboard', 'keyboard'),
        ('git', 'GitPython'),
    ]
    
    logger.debug("Checking dependencies...")
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            logger.debug(f"  OK: {package_name}")
        except ImportError as e:
            missing.append(package_name)
            logger.warning(f"  Missing: {package_name} ({e})")
    
    if missing:
        print("[ERROR] Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing)}")
        logger.error(f"Missing dependencies: {missing}")
        return False
    
    logger.info("All dependencies OK")
    return True


def check_single_instance():
    """
    Check if another instance is already running.
    Uses a lock file approach for Windows compatibility.
    Returns True if this is the only instance.
    """
    import tempfile
    import atexit
    
    lock_file = Path(tempfile.gettempdir()) / "james_project_launcher.lock"
    
    try:
        # Try to create lock file exclusively
        if lock_file.exists():
            # Check if the process that created it is still running
            try:
                with open(lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Check if process is still running (Windows)
                import ctypes
                kernel32 = ctypes.windll.kernel32
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, old_pid)
                
                if handle:
                    kernel32.CloseHandle(handle)
                    # Process still running
                    logger.warning(f"Another instance appears to be running (PID: {old_pid})")
                    return False
            except (ValueError, OSError, AttributeError):
                # Can't read PID or check process, assume it's stale
                pass
        
        # Create/update lock file with our PID
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Register cleanup
        def cleanup_lock():
            try:
                lock_file.unlink()
            except Exception:
                pass
        
        atexit.register(cleanup_lock)
        return True
        
    except Exception as e:
        print(f"[WARNING] Could not check for existing instance: {e}")
        logger.warning(f"Could not check for existing instance: {e}", exc_info=True)
        return True  # Allow running anyway


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="James's Project Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Start normally
  python main.py --minimized  Start minimized to system tray
  pythonw main.py             Start without console window

Keyboard Shortcuts:
  Win+Shift+L    Show/hide launcher (global hotkey)
        """
    )
    
    parser.add_argument(
        '--minimized', '-m',
        action='store_true',
        help='Start with window hidden (tray icon only)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging to console'
    )
    
    parser.add_argument(
        '--reset-config',
        action='store_true',
        help='Reset configuration to defaults'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser.parse_args()


def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        APP_DIR / 'config',
        APP_DIR / 'logs',
        APP_DIR / 'assets' / 'icons',
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ready: {directory}")
        except OSError as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            print(f"[ERROR] Failed to create {directory}: {e}")
            raise


def reset_configuration():
    """Reset configuration files to defaults."""
    config_dir = APP_DIR / 'config'
    
    # Backup existing configs
    backup_dir = config_dir / 'backup'
    backup_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for config_file in config_dir.glob('*.json'):
        if config_file.is_file():
            backup_path = backup_dir / f"{config_file.stem}_{timestamp}.json"
            config_file.rename(backup_path)
            logger.info(f"Backed up {config_file.name} to {backup_path.name}")
    
    logger.info("Configuration reset. Defaults will be created on next run.")


def run_with_app(app_factory, app_display_name: str) -> int:
    """Run the application with a provided app factory."""
    global logger
    
    # Parse arguments first (before logging, so --help works fast)
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging()

    # Ensure directories exist
    ensure_directories()
    
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info("=" * 50)
    logger.info(f"{app_display_name} starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {APP_DIR}")
    logger.info(f"Arguments: minimized={args.minimized}, debug={args.debug}")
    
    # Handle config reset
    if args.reset_config:
        reset_configuration()
        print("Configuration reset complete. Please restart the application.")
        return 0
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies. Please install required packages.")
        return 1
    
    # Check for existing instance (optional - can be disabled)
    # if not check_single_instance():
    #     logger.info("Another instance is running. Exiting.")
    #     return 0
    
    # Install global exception handler
    sys.excepthook = handle_exception
    
    # Import and run the application
    try:
        print("[INFO] Loading application modules...")
        logger.info("Loading application modules...")

        print("[INFO] Creating application window...")
        logger.info("Creating application window...")
        app = app_factory()
        
        # Start minimized if requested (from command line)
        if args.minimized:
            print("[INFO] Starting minimized to tray")
            logger.info("Starting minimized as requested (from command line)")
            app._minimized_from_cli = True  # Mark that this was from CLI
            app.after(100, app.withdraw)
        
        print("[INFO] Application initialized - starting main loop")
        logger.info("Application initialized successfully")
        logger.info("Starting main event loop...")
        
        # Run the application
        app.run()
        
        print("[INFO] Application closed normally")
        logger.info("Application closed normally")
        return 0
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        logger.error(f"Failed to import application modules: {e}", exc_info=True)
        logger.error("Make sure all source files are present in the src/ directory")
        
        # Show helpful error
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Import Error",
                f"Failed to load application:\n\n{e}\n\n"
                f"Please ensure all files are present in the src/ directory."
            )
            root.destroy()
        except Exception as ui_err:
            print(f"[WARNING] Could not show error dialog: {ui_err}")
        return 1
        
    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        traceback.print_exc()
        logger.exception(f"Failed to start application: {e}")
        return 1


def main():
    """Main entry point for the application."""
    from src.apps.core_app import create_app
    return run_with_app(create_app, "James's Project Launcher")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
