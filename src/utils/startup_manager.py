"""
Startup Manager
Manages Windows startup registry entries
"""

import winreg
import sys
import os

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class StartupManager:
    """Manages application startup with Windows"""
    
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "JamesProjectLauncher"
    SUPPRESS_ERRORS = False

    @classmethod
    def set_suppress_errors(cls, suppress: bool):
        cls.SUPPRESS_ERRORS = bool(suppress)
    
    @staticmethod
    def get_app_path(start_minimized: bool = False) -> str:
        """
        Get the path to the application executable
        
        Args:
            start_minimized: Whether to add --minimized flag
            
        Returns:
            Command string to run the application
        """
        # Get the path to main.py
        # Calculate path: from src/utils/startup_manager.py -> app_launcher/main.py
        current_file = os.path.abspath(__file__)
        # Go up: utils -> src -> app_launcher -> (root)
        utils_dir = os.path.dirname(current_file)
        src_dir = os.path.dirname(utils_dir)
        app_launcher_dir = os.path.dirname(src_dir)
        main_py = os.path.join(app_launcher_dir, "main.py")
        
        # Use pythonw.exe to run without console window
        # Find pythonw.exe (usually in same directory as python.exe)
        python_exe = sys.executable
        pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
        
        # If pythonw.exe doesn't exist, use python.exe
        if not os.path.exists(pythonw_exe):
            pythonw_exe = python_exe
        
        # Build command
        cmd = f'"{pythonw_exe}" "{main_py}"'
        
        # Add --minimized flag if requested
        if start_minimized:
            cmd += ' --minimized'
        
        return cmd
    
    @classmethod
    def enable_startup(cls, start_minimized: bool = False) -> bool:
        """
        Add application to Windows startup
        
        Args:
            start_minimized: Whether to start minimized (adds --minimized flag)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            app_path = cls.get_app_path(start_minimized)
            winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, app_path)
            
            winreg.CloseKey(key)
            logger.info(f"Startup enabled (minimized={start_minimized})")
            return True
        except Exception as e:
            if cls.SUPPRESS_ERRORS:
                logger.debug(f"Startup enable suppressed: {e}")
            else:
                logger.error(f"Error enabling startup: {e}")
            return False
    
    @classmethod
    def disable_startup(cls) -> bool:
        """
        Remove application from Windows startup
        
        Returns:
            True if successful, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, cls.APP_NAME)
            except FileNotFoundError:
                # Key doesn't exist, which is fine
                pass
            
            winreg.CloseKey(key)
            logger.info("Startup disabled")
            return True
        except Exception as e:
            if cls.SUPPRESS_ERRORS:
                logger.debug(f"Startup disable suppressed: {e}")
            else:
                logger.error(f"Error disabling startup: {e}")
            return False
    
    @classmethod
    def is_startup_enabled(cls) -> bool:
        """
        Check if application is set to start with Windows
        
        Returns:
            True if enabled, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REGISTRY_KEY,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, cls.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception as e:
            if cls.SUPPRESS_ERRORS:
                logger.debug(f"Startup check suppressed: {e}")
            else:
                logger.error(f"Error checking startup: {e}")
            return False
    
    @classmethod
    def check_startup_enabled(cls) -> bool:
        """
        Alias for is_startup_enabled() for backward compatibility
        
        Returns:
            True if enabled, False otherwise
        """
        return cls.is_startup_enabled()
