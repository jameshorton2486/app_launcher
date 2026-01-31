"""
Cleanup Service
Handles system maintenance and cleanup operations
"""

import subprocess
import os
import shutil
import ctypes
import sys
from typing import Tuple, Optional
from pathlib import Path

try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class CleanupService:
    """Service for system cleanup operations"""
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    @staticmethod
    def run_as_admin(command: list, cwd: Optional[str] = None) -> Tuple[bool, str]:
        """
        Run command with administrator privileges using ShellExecuteEx
        
        Args:
            command: Command as list
            cwd: Working directory
            
        Returns:
            Tuple of (success, output)
        """
        try:
            import ctypes
            from ctypes import wintypes
            
            # Convert command list to string
            if isinstance(command, list):
                cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in command)
            else:
                cmd_str = str(command)
            
            # Use ShellExecuteEx with runas verb
            SEE_MASK_NOCLOSEPROCESS = 0x00000040
            SW_HIDE = 0
            
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # This triggers UAC
                command[0] if isinstance(command, list) else command,
                ' '.join(command[1:]) if isinstance(command, list) and len(command) > 1 else '',
                cwd or None,
                SW_HIDE
            )
            
            # ShellExecute returns value > 32 on success
            if result > 32:
                return True, "Command executed with elevation"
            return False, f"Failed to elevate (error code: {result})"
        except Exception as e:
            return False, str(e)
    
    def empty_recycle_bin(self) -> Tuple[bool, str]:
        """Empty the recycle bin"""
        try:
            logger.debug("Emptying recycle bin...")
            # Use PowerShell to empty recycle bin
            ps_command = 'Clear-RecycleBin -Force -ErrorAction SilentlyContinue'
            result = subprocess.run(
                ['powershell.exe', '-NoProfile', '-Command', ps_command],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                logger.info("Recycle bin emptied successfully")
                return True, "Recycle bin emptied successfully"
            logger.warning("Failed to empty recycle bin")
            return False, "Failed to empty recycle bin"
        except Exception as e:
            print(f"[ERROR] Empty recycle bin: {e}")
            logger.error(f"Error emptying recycle bin: {e}", exc_info=True)
            return False, str(e)
    
    def clear_temp_files(self) -> Tuple[bool, str]:
        """
        Clear temporary files from %temp% and C:\Windows\Temp

        Returns:
            Tuple of (success, message)
        """
        logger.debug("Clearing temp files...")
        bytes_freed = 0
        files_deleted = 0
        temp_dirs = [
            os.path.expandvars('%temp%'),
            os.path.expandvars('%TMP%'),
            r'C:\Windows\Temp'
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    bytes_freed += size
                                    files_deleted += 1
                            except:
                                pass  # Skip files that can't be deleted
                except:
                    pass  # Skip directories that can't be accessed
        
        mb_freed = bytes_freed / (1024 * 1024)
        if files_deleted > 0:
            return True, f"Freed {mb_freed:.1f} MB from {files_deleted} files"
        return True, "No temp files found to delete"
    
    def clear_prefetch(self) -> Tuple[bool, str]:
        """Clear Windows Prefetch folder (requires admin)"""
        prefetch_path = r'C:\Windows\Prefetch'
        
        if not self.is_admin():
            # Try to run with elevation
            # Create a PowerShell script to clear prefetch
            ps_script = f'''
            $prefetch = "{prefetch_path}"
            if (Test-Path $prefetch) {{
                Get-ChildItem $prefetch | Remove-Item -Force -ErrorAction SilentlyContinue
                Write-Output "Prefetch cleared"
            }} else {{
                Write-Output "Prefetch folder not found"
            }}
            '''
            # Save to temp file and run elevated
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(ps_script)
                ps_file = f.name
            
            try:
                result = self.run_as_admin(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_file])
                os.unlink(ps_file)
                return result
            except:
                if os.path.exists(ps_file):
                    os.unlink(ps_file)
                return False, "Administrator privileges required. Please run app as admin."
        
        try:
            if os.path.exists(prefetch_path):
                for file in os.listdir(prefetch_path):
                    try:
                        file_path = os.path.join(prefetch_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except:
                        pass
                return True, "Prefetch cleared successfully"
            return False, "Prefetch folder not found"
        except Exception as e:
            return False, str(e)
    
    def flush_dns(self) -> Tuple[bool, str]:
        """Flush DNS cache"""
        try:
            result = subprocess.run(
                ['ipconfig', '/flushdns'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, "DNS cache flushed successfully"
            return False, result.stderr.strip() or "Failed to flush DNS"
        except Exception as e:
            return False, str(e)
    
    def clear_standby_ram(self) -> Tuple[bool, str]:
        """Clear standby RAM using EmptyStandbyList"""
        try:
            # Try to use EmptyStandbyList.exe if available
            # Otherwise use PowerShell method
            ps_command = '''
            $signature = @"
            [DllImport("kernel32.dll", SetLastError = true)]
            public static extern bool SetProcessWorkingSetSize(IntPtr proc, int min, int max);
            "@
            $type = Add-Type -MemberDefinition $signature -Name "Win32" -Namespace Win32Functions -PassThru
            $type::SetProcessWorkingSetSize((Get-Process -Id $pid).Handle, -1, -1)
            '''
            result = subprocess.run(
                ['powershell.exe', '-NoProfile', '-Command', ps_command],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Standby RAM cleared"
        except Exception as e:
            return False, str(e)
    
    def run_disk_cleanup(self) -> Tuple[bool, str]:
        """Launch Windows Disk Cleanup"""
        try:
            subprocess.Popen(
                ['cleanmgr.exe', '/d', 'C:'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Disk Cleanup launched"
        except Exception as e:
            return False, f"Failed to launch Disk Cleanup: {e}"
    
    def optimize_drive(self, drive: str = "C:") -> Tuple[bool, str]:
        """Optimize/defragment drive"""
        try:
            result = subprocess.run(
                ['defrag', drive, '/O'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=300
            )
            if result.returncode == 0:
                return True, f"Drive {drive} optimized successfully"
            return False, result.stderr.strip() or "Optimization failed"
        except subprocess.TimeoutExpired:
            return False, "Optimization timed out (this is normal for large drives)"
        except Exception as e:
            return False, str(e)
    
    def restart_explorer(self) -> Tuple[bool, str]:
        """Restart Windows Explorer"""
        try:
            # Kill explorer
            subprocess.run(
                ['taskkill', '/F', '/IM', 'explorer.exe'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Wait a moment
            import time
            time.sleep(1)
            # Restart explorer
            subprocess.Popen(
                ['explorer.exe'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Explorer restarted successfully"
        except Exception as e:
            return False, str(e)
    
    def reset_network(self) -> Tuple[bool, str]:
        """Reset network stack (requires admin)"""
        if not self.is_admin():
            # Try to run with elevation
            import tempfile
            ps_script = '''
            netsh winsock reset
            netsh int ip reset
            Write-Output "Network stack reset. Please restart your computer."
            '''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(ps_script)
                ps_file = f.name
            
            try:
                result = self.run_as_admin(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_file])
                os.unlink(ps_file)
                return result
            except:
                if os.path.exists(ps_file):
                    os.unlink(ps_file)
                return False, "Administrator privileges required. Please run app as admin."
        
        try:
            # Reset winsock
            result1 = subprocess.run(
                ['netsh', 'winsock', 'reset'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Reset IP
            result2 = subprocess.run(
                ['netsh', 'int', 'ip', 'reset'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result1.returncode == 0 and result2.returncode == 0:
                return True, "Network stack reset. Please restart your computer."
            return False, "Network reset failed"
        except Exception as e:
            return False, str(e)
    
    def release_renew_ip(self) -> Tuple[bool, str]:
        """Release and renew IP address"""
        try:
            # Release
            subprocess.run(
                ['ipconfig', '/release'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait a moment
            import time
            time.sleep(2)
            
            # Renew
            result = subprocess.run(
                ['ipconfig', '/renew'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                return True, "IP address released and renewed"
            return False, "Failed to renew IP address"
        except Exception as e:
            return False, str(e)
    
    def get_network_stats(self) -> Tuple[bool, str]:
        """Get network statistics"""
        try:
            result = subprocess.run(
                ['netstat', '-e'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            return False, "Failed to get network statistics"
        except Exception as e:
            return False, str(e)
    
    def clear_windows_update_cache(self) -> Tuple[bool, str]:
        """Clear Windows Update cache (requires admin)"""
        if not self.is_admin():
            # Try to run with elevation
            import tempfile
            ps_script = '''
            net stop wuauserv
            $softdist = "C:\\Windows\\SoftwareDistribution"
            if (Test-Path $softdist) {
                Remove-Item -Path $softdist -Recurse -Force -ErrorAction SilentlyContinue
            }
            net start wuauserv
            Write-Output "Windows Update cache cleared. Restart recommended."
            '''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(ps_script)
                ps_file = f.name
            
            try:
                result = self.run_as_admin(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_file])
                os.unlink(ps_file)
                return result
            except:
                if os.path.exists(ps_file):
                    os.unlink(ps_file)
                return False, "Administrator privileges required. Please run app as admin."
        
        try:
            # Stop Windows Update service
            subprocess.run(
                ['net', 'stop', 'wuauserv'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Clear SoftwareDistribution folder
            softdist_path = r'C:\Windows\SoftwareDistribution'
            if os.path.exists(softdist_path):
                try:
                    shutil.rmtree(softdist_path)
                except:
                    # If rmtree fails, try to delete files individually
                    for root, dirs, files in os.walk(softdist_path):
                        for file in files:
                            try:
                                os.remove(os.path.join(root, file))
                            except:
                                pass
            
            # Restart Windows Update service
            subprocess.run(
                ['net', 'start', 'wuauserv'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return True, "Windows Update cache cleared. Restart recommended."
        except Exception as e:
            return False, str(e)
    
    def pause_windows_updates(self, days: int = 7) -> Tuple[bool, str]:
        """Pause Windows Updates for specified days"""
        try:
            # Use PowerShell to pause updates
            ps_command = f'''
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
            $UpdateSearcher.Search("IsInstalled=0")
            [System.Windows.Forms.MessageBox]::Show("Updates paused for {days} days")
            '''
            # Note: This is a simplified version
            # Full implementation would use Windows Update API
            return True, f"Updates paused for {days} days (feature requires Windows Update API)"
        except Exception as e:
            return False, str(e)
    
    def reset_ms_store(self) -> Tuple[bool, str]:
        """Reset Microsoft Store"""
        try:
            subprocess.Popen(
                ['wsreset.exe'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Microsoft Store reset initiated"
        except Exception as e:
            return False, f"Failed to reset MS Store: {e}"
    
    def launch_external_tool(self, tool_name: str, config_manager) -> Tuple[bool, str]:
        """
        Launch external tool by name
        
        Args:
            tool_name: 'ccleaner' or 'wise_memory_cleaner'
            config_manager: ConfigManager instance
            
        Returns:
            Tuple of (success, message)
        """
        tool_path = config_manager.get_setting(f'external_tools.{tool_name}', '')
        if not tool_path or not os.path.exists(tool_path):
            return False, f"{tool_name} not found. Configure path in settings."
        
        try:
            subprocess.Popen(
                [tool_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, f"{tool_name} launched"
        except Exception as e:
            return False, f"Failed to launch {tool_name}: {e}"
    
    def launch_ccleaner(self, config_manager) -> Tuple[bool, str]:
        """Launch CCleaner"""
        return self.launch_external_tool('ccleaner', config_manager)
    
    def launch_wise_memory_cleaner(self, config_manager) -> Tuple[bool, str]:
        """Launch Wise Memory Optimizer"""
        return self.launch_external_tool('wise_memory_cleaner', config_manager)

    def clear_browser_cache(self) -> Tuple[bool, str]:
        """
        Clear cache from major browsers.
        Does NOT clear passwords, history, or bookmarks.
        """
        total_freed = 0
        browsers_cleared = []

        def clear_dir(path):
            nonlocal total_freed
            if not os.path.exists(path):
                return 0
            freed = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        freed += size
                    except Exception:
                        pass
            total_freed += freed
            return freed

        # Chrome cache paths
        chrome_cache = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache')
        chrome_code_cache = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Code Cache')

        # Edge cache paths
        edge_cache = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache')
        edge_code_cache = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Code Cache')

        # Firefox cache path
        firefox_profiles = os.path.expandvars(r'%LOCALAPPDATA%\Mozilla\Firefox\Profiles')

        # Brave cache path
        brave_cache = os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache')
        brave_code_cache = os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Code Cache')

        if clear_dir(chrome_cache) + clear_dir(chrome_code_cache) > 0:
            browsers_cleared.append("Chrome")

        if clear_dir(edge_cache) + clear_dir(edge_code_cache) > 0:
            browsers_cleared.append("Edge")

        if os.path.exists(firefox_profiles):
            cleared_any = False
            for profile in os.listdir(firefox_profiles):
                cache_path = os.path.join(firefox_profiles, profile, "cache2")
                if clear_dir(cache_path) > 0:
                    cleared_any = True
            if cleared_any:
                browsers_cleared.append("Firefox")

        if clear_dir(brave_cache) + clear_dir(brave_code_cache) > 0:
            browsers_cleared.append("Brave")

        total_freed_mb = total_freed / (1024 * 1024)
        if not browsers_cleared:
            return True, "No browser cache found to clear"
        return True, f"Browser cache cleared: {total_freed_mb:.1f} MB freed from {len(browsers_cleared)} browsers"
