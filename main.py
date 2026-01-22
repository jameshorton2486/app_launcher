"""
Main Entry Point
Launches the App Launcher application
"""

import sys
import os
import argparse
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import logger early
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Show user-friendly error message
    try:
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "Application Error",
            f"An unexpected error occurred:\n\n{exc_value}\n\nCheck logs/app.log for details."
        )
    except:
        pass


def main():
    """Main entry point"""
    # Set up global exception handler
    sys.excepthook = handle_exception
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="James's Project Launcher")
    parser.add_argument(
        '--minimized',
        action='store_true',
        help='Start application minimized to system tray'
    )
    args = parser.parse_args()
    
    try:
        logger.info("Starting App Launcher...")
        
        # Import and create app
        from src.app import AppLauncher
        app = AppLauncher()
        
        # Start minimized if requested (from command line)
        if args.minimized:
            logger.info("Starting minimized as requested (from command line)")
            app._minimized_from_cli = True  # Mark that this was from CLI
            app.after(100, app.withdraw)
        
        # Run application
        app.run()
        
        logger.info("Application closed")
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
