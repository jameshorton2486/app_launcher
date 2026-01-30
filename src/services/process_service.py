"""
Process Service
Handles launching applications and opening files/folders
"""

import subprocess
import os
import tempfile
import threading
from typing import Optional, Tuple

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class ProcessService:
    """Service for launching processes and opening files"""
    
    @staticmethod
    def escape_powershell_path(path: str) -> str:
        """Escape a path for use in PowerShell commands"""
        return path.replace("'", "''")
    
    def launch_python_script(self, path: str, script: str) -> Tuple[bool, str]:
        """
        Launch a Python script
        
        Args:
            path: Project directory path
            script: Script filename or path
            
        Returns:
            Tuple of (success, message)
        """
        try:
            script_path = os.path.join(path, script) if not os.path.isabs(script) else script
            
            if not os.path.exists(script_path):
                return False, f"Script not found: {script_path}"
            
            pythonw_path = os.path.join(os.path.dirname(os.__file__), 'pythonw.exe')
            if not os.path.exists(pythonw_path):
                pythonw_path = 'pythonw.exe'
            
            subprocess.Popen(
                [pythonw_path, script_path],
                cwd=path,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.info(f"Launched Python script: {script_path}")
            return True, "Launched"
        except Exception as e:
            logger.error(f"Error launching Python script: {e}")
            return False, str(e)
    
    def launch_npm_command(self, path: str, command: str) -> Tuple[bool, str]:
        """
        Launch an npm command
        
        Args:
            path: Project directory path
            command: npm command (e.g., "run dev")
            
        Returns:
            Tuple of (success, message)
        """
        try:
            folder_escaped = self.escape_powershell_path(path)
            cmd = [
                'powershell.exe',
                '-NoProfile',
                '-NonInteractive',
                '-ExecutionPolicy', 'Bypass',
                '-WindowStyle', 'Hidden',
                '-Command',
                f"Set-Location -LiteralPath '{folder_escaped}'; npm {command}"
            ]
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info(f"Launched npm command: {command} in {path}")
            return True, "Launched"
        except Exception as e:
            logger.error(f"Error launching npm command: {e}")
            return False, str(e)
    
    def launch_powershell_script(self, path: str, script: str) -> Tuple[bool, str]:
        """
        Launch a PowerShell script
        
        Args:
            path: Project directory path
            script: Script filename or path
            
        Returns:
            Tuple of (success, message)
        """
        try:
            script_path = os.path.join(path, script) if not os.path.isabs(script) else script
            
            if not os.path.exists(script_path):
                return False, f"Script not found: {script_path}"
            
            script_escaped = self.escape_powershell_path(script_path)
            folder_escaped = self.escape_powershell_path(path)
            cmd = [
                'powershell.exe',
                '-NoProfile',
                '-NonInteractive',
                '-ExecutionPolicy', 'Bypass',
                '-WindowStyle', 'Hidden',
                '-Command',
                f"Set-Location -LiteralPath '{folder_escaped}'; & '{script_escaped}'"
            ]
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info(f"Launched PowerShell script: {script_path}")
            return True, "Launched"
        except Exception as e:
            logger.error(f"Error launching PowerShell script: {e}")
            return False, str(e)
    
    def launch_exe(self, path: str) -> Tuple[bool, str]:
        """
        Launch an executable
        
        Args:
            path: Full path to executable
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not os.path.exists(path):
                return False, f"Executable not found: {path}"
            
            subprocess.Popen([path], cwd=os.path.dirname(path), creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info(f"Launched executable: {path}")
            return True, "Launched"
        except Exception as e:
            logger.error(f"Error launching executable: {e}")
            return False, str(e)

    def launch_with_debugger(self, project_path: str, config_manager) -> Tuple[bool, str]:
        """Launch project in IDE with debugger attached (best-effort)"""
        if not project_path or not os.path.isdir(project_path):
            return False, "Project path not found"

        candidates = ["cursor", "vscode", "pycharm"]
        for ide_name in candidates:
            ide_path = config_manager.get_setting(f'external_tools.{ide_name}', '')
            if ide_path and os.path.exists(ide_path):
                try:
                    subprocess.Popen([ide_path, project_path], creationflags=subprocess.CREATE_NO_WINDOW)
                    return True, f"Launched in {ide_name}"
                except Exception as e:
                    logger.error(f"Error launching {ide_name}: {e}")
                    return False, f"Failed to launch {ide_name}"

        return False, "No IDE configured"
    
    def open_in_explorer(self, path: str) -> bool:
        """
        Open folder in File Explorer
        
        Args:
            path: Directory path to open
        """
        try:
            if not os.path.isdir(path):
                logger.warning(f"Path is not a directory: {path}")
                return False
            os.startfile(path)
            logger.debug(f"Opened in Explorer: {path}")
            return True
        except Exception as e:
            logger.error(f"Error opening in Explorer: {e}")
            return False
    
    def open_in_terminal(self, path: str) -> bool:
        """
        Open PowerShell in project directory
        
        Args:
            path: Directory path
        """
        try:
            if not os.path.isdir(path):
                logger.warning(f"Path is not a directory: {path}")
                return False
            subprocess.Popen(['powershell.exe'], cwd=path)
            logger.debug(f"Opened terminal in: {path}")
            return True
        except Exception as e:
            logger.error(f"Error opening terminal: {e}")
            return False
    
    def open_in_ide(self, path: str, ide_name: str, config_manager) -> bool:
        """
        Open project in IDE
        
        Args:
            path: Project folder path
            ide_name: 'cursor', 'vscode', or 'pycharm'
            config_manager: ConfigManager instance
        """
        try:
            if not os.path.isdir(path):
                logger.warning(f"Path is not a directory: {path}")
                return False
            
            ide_path = config_manager.get_setting(f'external_tools.{ide_name}', '')
            if not ide_path or not os.path.exists(ide_path):
                logger.warning(f"IDE not found: {ide_name} at {ide_path}")
                return False
            
            subprocess.Popen([ide_path, path], creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info(f"Opened {ide_name} in: {path}")
            return True
        except Exception as e:
            logger.error(f"Error opening IDE: {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """
        Open URL in default browser
        
        Args:
            url: URL to open
        """
        try:
            if not url or not url.startswith(('http://', 'https://')):
                logger.warning(f"Invalid URL: {url}")
                return False
            import webbrowser
            webbrowser.open(url)
            logger.debug(f"Opened URL: {url}")
            return True
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            return False
    
    # Backward compatibility method
    def launch_project(self, project: dict) -> Tuple[bool, str]:
        """
        Launch a project based on its launch_type
        
        Args:
            project: Project dictionary with path, launch_script, launch_type
            
        Returns:
            Tuple of (success, message)
        """
        project_path = project.get('path', '')
        launch_script = project.get('launch_script', '')
        launch_type = project.get('launch_type', 'python')
        
        if not project_path or not os.path.isdir(project_path):
            return False, "Project path does not exist"
        
        script_path = os.path.join(project_path, launch_script) if not os.path.isabs(launch_script) else launch_script
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            if launch_type == 'python':
                # Python script
                pythonw_path = os.path.join(os.path.dirname(os.__file__), 'pythonw.exe')
                if not os.path.exists(pythonw_path):
                    pythonw_path = 'pythonw.exe'
                subprocess.Popen(
                    [pythonw_path, script_path],
                    cwd=project_path,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True, "Project launched"
            
            elif launch_type == 'npm':
                # NPM command
                script_escaped = self.escape_powershell_path(script_path)
                folder_escaped = self.escape_powershell_path(project_path)
                cmd = [
                    'powershell.exe',
                    '-NoProfile',
                    '-NonInteractive',
                    '-ExecutionPolicy', 'Bypass',
                    '-WindowStyle', 'Hidden',
                    '-Command',
                    f"Set-Location -LiteralPath '{folder_escaped}'; npm run dev"
                ]
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "Project launched"
            
            elif launch_type == 'powershell':
                # PowerShell script
                script_escaped = self.escape_powershell_path(script_path)
                folder_escaped = self.escape_powershell_path(project_path)
                cmd = [
                    'powershell.exe',
                    '-NoProfile',
                    '-NonInteractive',
                    '-ExecutionPolicy', 'Bypass',
                    '-WindowStyle', 'Hidden',
                    '-Command',
                    f"Set-Location -LiteralPath '{folder_escaped}'; & '{script_escaped}'"
                ]
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "Project launched"
            
            elif launch_type == 'bat' or launch_type == 'cmd':
                # Batch script
                vbs_script = tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False, encoding='utf-8')
                vbs_script.write(f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{project_path.replace(chr(92), chr(92)+chr(92))}"
WshShell.Run "cmd.exe /c ""{script_path.replace(chr(92), chr(92)+chr(92))}""", 0, False
Set WshShell = Nothing''')
                vbs_script.close()
                subprocess.Popen(['wscript.exe', vbs_script.name], creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Clean up VBScript after delay
                def cleanup_vbs():
                    import time
                    time.sleep(2)
                    try:
                        os.unlink(vbs_script.name)
                    except:
                        pass
                threading.Thread(target=cleanup_vbs, daemon=True).start()
                return True, "Project launched"
            
            elif launch_type == 'exe':
                # Executable
                subprocess.Popen([script_path], cwd=project_path, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "Project launched"
            
            else:
                return False, f"Unknown launch type: {launch_type}"
        
        except Exception as e:
            return False, str(e)
    
    def open_folder(self, folder_path: str) -> bool:
        """Open folder in File Explorer"""
        try:
            os.startfile(folder_path)
            return True
        except:
            return False
    
    def open_terminal(self, folder_path: str) -> bool:
        """Open PowerShell in project directory"""
        try:
            terminal_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe")
            if os.path.exists(terminal_path):
                subprocess.Popen(
                    [terminal_path, "-d", folder_path],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True
            subprocess.Popen(['powershell.exe'], cwd=folder_path)
            return True
        except:
            return False
    
    def open_in_ide(self, ide_name: str, folder_path: str, config_manager) -> bool:
        """
        Open project in IDE
        
        Args:
            ide_name: 'cursor', 'vscode', or 'pycharm'
            folder_path: Project folder path
            config_manager: ConfigManager instance
        """
        ide_path = config_manager.get_setting(f'external_tools.{ide_name}', '')
        if not ide_path or not os.path.exists(ide_path):
            return False
        
        try:
            subprocess.Popen([ide_path, folder_path], creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except:
            return False
    
    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except:
            return False
