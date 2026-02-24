"""
Administrator Privilege Elevation
Handles UAC elevation for tools that require admin privileges
"""

import ctypes
import sys
import os
import subprocess
from typing import Tuple, Optional

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


def is_admin() -> bool:
    """Check if current process is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate_script(script_path: str, args: list = None, cwd: Optional[str] = None) -> Tuple[bool, str]:
    """
    Elevate and run a Python script with administrator privileges
    
    Args:
        script_path: Path to Python script to run
        args: Additional arguments to pass
        cwd: Working directory
        
    Returns:
        Tuple of (success, message)
    """
    try:
        if args is None:
            args = []
        
        # Get Python executable
        python_exe = sys.executable
        
        # Build command
        cmd = [python_exe, script_path] + args
        
        # Use ShellExecuteW with runas verb to trigger UAC
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # This triggers UAC elevation prompt
            python_exe,
            f'"{script_path}" {" ".join(args)}',
            cwd or os.getcwd(),
            1  # SW_SHOWNORMAL - show window
        )
        
        # ShellExecute returns value > 32 on success
        if result > 32:
            return True, "Elevation requested - UAC prompt should appear"
        return False, f"Failed to elevate (error code: {result})"
    except Exception as e:
        logger.error(f"Error elevating script: {e}")
        return False, str(e)


def run_command_elevated(command: list, cwd: Optional[str] = None, wait: bool = True) -> Tuple[bool, str]:
    """
    Run a command with administrator privileges
    
    Args:
        command: Command as list (e.g., ['cmd', '/c', 'dir'])
        cwd: Working directory
        wait: Whether to wait for command to complete
        
    Returns:
        Tuple of (success, message)
    """
    try:
        if not command:
            return False, "No command provided"
        
        # Convert command list to string for ShellExecute
        if isinstance(command, list):
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in command)
        else:
            cmd_str = str(command)
        
        # Use ShellExecuteW with runas verb
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # This triggers UAC elevation prompt
            command[0] if isinstance(command, list) else command,
            ' '.join(command[1:]) if isinstance(command, list) and len(command) > 1 else '',
            cwd or None,
            1 if wait else 0  # SW_SHOWNORMAL or SW_HIDE
        )
        
        # ShellExecute returns value > 32 on success
        if result > 32:
            return True, "Command executed with elevation"
        return False, f"Failed to elevate (error code: {result})"
    except Exception as e:
        logger.error(f"Error running elevated command: {e}")
        return False, str(e)


def run_powershell_elevated(script: str, wait: bool = True) -> Tuple[bool, str]:
    """
    Run PowerShell script with administrator privileges
    
    Args:
        script: PowerShell script/command to run
        wait: Whether to wait for completion
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Create a temporary PowerShell script
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(script)
            temp_script = f.name
        
        try:
            # Use ShellExecuteW to run PowerShell with runas
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                "powershell.exe",
                f'-NoProfile -ExecutionPolicy Bypass -File "{temp_script}"',
                None,
                1 if wait else 0
            )
            
            if result > 32:
                return True, "PowerShell script executed with elevation"
            return False, f"Failed to elevate (error code: {result})"
        finally:
            # Clean up temp file after a delay
            import threading
            def cleanup():
                import time
                time.sleep(2)
                try:
                    os.unlink(temp_script)
                except Exception as e:
                    logger.debug(f"Suppressed exception removing temp script: {e}")
            threading.Thread(target=cleanup, daemon=True).start()
    except Exception as e:
        logger.error(f"Error running elevated PowerShell: {e}")
        return False, str(e)


def request_elevation_if_needed(requires_admin: bool) -> Tuple[bool, str]:
    """
    Check if admin is needed and request elevation if not already admin
    
    Args:
        requires_admin: Whether the operation requires admin
        
    Returns:
        Tuple of (is_admin, message)
    """
    if not requires_admin:
        return True, "No elevation needed"
    
    if is_admin():
        return True, "Already running as administrator"
    
    # If we need admin but aren't running as admin, we can't elevate
    # the current process. The caller should use run_command_elevated
    # or elevate_script instead.
    return False, "Administrator privileges required - use elevate_script or run_command_elevated"
