"""
Maintenance Service
Handles system repair and privacy operations
"""

import subprocess
import ctypes
import threading
import winreg
import os
from typing import Tuple, Any, Optional, Callable, List

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class MaintenanceService:
    """Service for system maintenance tasks"""

    @staticmethod
    def is_admin() -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def _run_as_admin(self, command: list, cwd: Optional[str] = None) -> Tuple[bool, str]:
        """Run command with elevation"""
        try:
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                command[0],
                " ".join(command[1:]),
                cwd or None,
                0
            )
            if result > 32:
                return True, "Command executed with elevation"
            return False, f"Failed to elevate (error code: {result})"
        except Exception as exc:
            return False, str(exc)

    def _run_powershell(self, script: str, as_admin: bool = False) -> Tuple[bool, str]:
        """Run a PowerShell script"""
        command = [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-Command", script
        ]

        if as_admin and not self.is_admin():
            return self._run_as_admin(command)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                output = result.stdout.strip() or "Command completed"
                return True, output
            return False, result.stderr.strip() or "Command failed"
        except Exception as exc:
            logger.error(f"PowerShell execution failed: {exc}")
            return False, str(exc)

    @staticmethod
    def _get_hive(hive: str):
        mapping = {
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
        }
        return mapping.get(hive, winreg.HKEY_CURRENT_USER)

    def _set_registry_value(self, key_path, value_name, value, value_type, hive="HKCU") -> Tuple[bool, str]:
        """Set a registry value"""
        try:
            root = self._get_hive(hive)
            with winreg.CreateKeyEx(root, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value)
            return True, "Registry updated"
        except Exception as exc:
            logger.error(f"Failed to set registry value: {exc}")
            return False, str(exc)

    # System Repair methods
    def run_sfc_scan(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> Tuple[bool, str]:
        """Run System File Checker scan"""
        return self._run_long_command(
            ["sfc", "/scannow"],
            progress_callback,
            admin_required=True,
            name="SFC"
        )

    def run_dism_repair(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> Tuple[bool, str]:
        """Run DISM repair"""
        return self._run_long_command(
            ["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            progress_callback,
            admin_required=True,
            name="DISM"
        )

    def schedule_chkdsk(self) -> Tuple[bool, str]:
        """Schedule CHKDSK for next restart"""
        script = "echo Y | chkdsk C: /f /r"
        return self._run_powershell(script, as_admin=True)

    def reset_windows_update(self) -> Tuple[bool, str]:
        """Reset Windows Update components"""
        script = r"""
        $services = @("wuauserv","bits","cryptsvc")
        foreach ($svc in $services) { Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue }

        $sd = "C:\Windows\SoftwareDistribution"
        $cr = "C:\Windows\System32\catroot2"
        if (Test-Path $sd) { Remove-Item -Path $sd -Recurse -Force -ErrorAction SilentlyContinue }
        if (Test-Path $cr) { Remove-Item -Path $cr -Recurse -Force -ErrorAction SilentlyContinue }

        $dlls = @(
            "atl.dll","urlmon.dll","mshtml.dll","shdocvw.dll","browseui.dll",
            "jscript.dll","vbscript.dll","scrrun.dll","msxml.dll","msxml3.dll",
            "msxml6.dll","actxprxy.dll","softpub.dll","wintrust.dll","dssenh.dll",
            "rsaenh.dll","gpkcsp.dll","sccbase.dll","slbcsp.dll","cryptdlg.dll",
            "oleaut32.dll","ole32.dll","shell32.dll","initpki.dll","wuapi.dll",
            "wuaueng.dll","wuaueng1.dll","wucltui.dll","wups.dll","wups2.dll",
            "wuweb.dll","qmgr.dll","qmgrprxy.dll","wucltux.dll","muweb.dll","wuwebv.dll"
        )
        foreach ($dll in $dlls) { regsvr32.exe /s $dll }

        foreach ($svc in $services) { Start-Service -Name $svc -ErrorAction SilentlyContinue }

        Write-Output "Windows Update reset completed"
        """
        return self._run_powershell(script, as_admin=True)

    # Privacy methods
    def disable_telemetry(self) -> Tuple[bool, str]:
        """Disable Windows telemetry"""
        return self._set_registry_value(
            r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "AllowTelemetry",
            0,
            winreg.REG_DWORD,
            hive="HKLM"
        )

    def disable_activity_history(self) -> Tuple[bool, str]:
        """Disable activity history"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "Start_TrackProgs",
            0,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def disable_advertising_id(self) -> Tuple[bool, str]:
        """Disable advertising ID"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
            "Enabled",
            0,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def disable_cortana(self) -> Tuple[bool, str]:
        """Disable Cortana"""
        return self._set_registry_value(
            r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",
            "AllowCortana",
            0,
            winreg.REG_DWORD,
            hive="HKLM"
        )

    def _run_long_command(
        self,
        command: list,
        progress_callback: Optional[Callable[[int, str], None]],
        admin_required: bool = False,
        name: str = "Command"
    ) -> Tuple[bool, str]:
        """Run a long command with progress parsing"""
        result = {"success": False, "message": f"{name} failed"}

        def worker():
            if admin_required and not self.is_admin():
                success, message = self._run_as_admin(command)
                result["success"] = success
                result["message"] = message
                return

            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if not line:
                        continue
                    if progress_callback:
                        percent = self._parse_percent(line)
                        if percent is not None:
                            progress_callback(percent, line)
                        else:
                            progress_callback(0, line)

                process.wait()
                if process.returncode == 0:
                    result["success"] = True
                    result["message"] = f"{name} completed"
                else:
                    result["message"] = f"{name} failed (code {process.returncode})"
            except Exception as exc:
                logger.error(f"{name} failed: {exc}")
                result["message"] = str(exc)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join()
        return result["success"], result["message"]

    @staticmethod
    def _parse_percent(text: str) -> Optional[int]:
        """Extract percentage from output"""
        for token in text.replace('%', ' %').split():
            if token.endswith('%'):
                token = token.replace('%', '')
            if token.isdigit():
                value = int(token)
                if 0 <= value <= 100:
                    return value
        return None
