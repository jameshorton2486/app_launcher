"""
Optimization Service
Handles Windows performance and optimization operations
"""

import subprocess
import ctypes
import winreg
from typing import Tuple, Any, List, Dict

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class OptimizationService:
    """Service for Windows optimization tasks"""

    @staticmethod
    def is_admin() -> bool:
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def _run_as_admin(self, command: list, cwd: str | None = None) -> Tuple[bool, str]:
        """Run a command with elevation"""
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

    def _get_registry_value(self, key_path, value_name, hive="HKCU") -> Tuple[bool, Any]:
        """Get a registry value"""
        try:
            root = self._get_hive(hive)
            with winreg.OpenKey(root, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
            return True, value
        except Exception as exc:
            logger.error(f"Failed to read registry value: {exc}")
            return False, None

    def _run_sc_command(self, args: list) -> Tuple[bool, str]:
        """Run a service control command"""
        try:
            result = subprocess.run(
                ["sc"] + args,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, result.stdout.strip() or "Service command completed"
            return False, result.stderr.strip() or result.stdout.strip() or "Service command failed"
        except Exception as exc:
            logger.error(f"SC command failed: {exc}")
            return False, str(exc)

    @staticmethod
    def _get_hive(hive: str):
        mapping = {
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
            "HKCR": winreg.HKEY_CLASSES_ROOT,
            "HKU": winreg.HKEY_USERS,
            "HKCC": winreg.HKEY_CURRENT_CONFIG,
        }
        return mapping.get(hive, winreg.HKEY_CURRENT_USER)

    # SysMain methods
    def get_sysmain_status(self) -> Tuple[bool, str]:
        """Get SysMain service status"""
        success, value = self._get_registry_value(
            r"SYSTEM\CurrentControlSet\Services\SysMain",
            "Start",
            hive="HKLM"
        )
        if not success:
            return False, "Unable to read SysMain state"

        status_map = {2: "Enabled", 4: "Disabled"}
        status = status_map.get(value, f"Unknown ({value})")
        return True, f"SysMain: {status}"

    def disable_sysmain(self) -> Tuple[bool, str]:
        """Disable SysMain service"""
        self._run_sc_command(["stop", "SysMain"])
        return self._run_sc_command(["config", "SysMain", "start=", "disabled"])

    def enable_sysmain(self) -> Tuple[bool, str]:
        """Enable SysMain service"""
        self._run_sc_command(["config", "SysMain", "start=", "auto"])
        return self._run_sc_command(["start", "SysMain"])

    # Visual Effects methods
    def disable_animations(self) -> Tuple[bool, str]:
        """Disable window animations"""
        mask = bytes([0x90, 0x12, 0x03, 0x80, 0x10, 0x00, 0x00, 0x00])
        success, message = self._set_registry_value(
            r"Control Panel\Desktop",
            "UserPreferencesMask",
            mask,
            winreg.REG_BINARY,
            hive="HKCU"
        )
        if success:
            self._run_powershell("RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters")
        return success, message

    def enable_animations(self) -> Tuple[bool, str]:
        """Enable window animations"""
        mask = bytes([0x9E, 0x3E, 0x07, 0x80, 0x12, 0x00, 0x00, 0x00])
        success, message = self._set_registry_value(
            r"Control Panel\Desktop",
            "UserPreferencesMask",
            mask,
            winreg.REG_BINARY,
            hive="HKCU"
        )
        if success:
            self._run_powershell("RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters")
        return success, message

    def disable_transparency(self) -> Tuple[bool, str]:
        """Disable Windows transparency effects"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            "EnableTransparency",
            0,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def enable_transparency(self) -> Tuple[bool, str]:
        """Enable Windows transparency effects"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            "EnableTransparency",
            1,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def set_best_performance(self) -> Tuple[bool, str]:
        """Apply best performance visual settings"""
        return self.disable_animations()

    def set_best_appearance(self) -> Tuple[bool, str]:
        """Apply best appearance visual settings"""
        return self.enable_animations()

    # Background Services methods
    def disable_widgets(self) -> Tuple[bool, str]:
        """Disable Windows Widgets"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "TaskbarDa",
            0,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def enable_widgets(self) -> Tuple[bool, str]:
        """Enable Windows Widgets"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "TaskbarDa",
            1,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def disable_search_highlights(self) -> Tuple[bool, str]:
        """Disable search highlights"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\SearchSettings",
            "IsDynamicSearchBoxEnabled",
            0,
            winreg.REG_DWORD,
            hive="HKCU"
        )

    def disable_delivery_optimization(self) -> Tuple[bool, str]:
        """Disable Delivery Optimization"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config",
            "DODownloadMode",
            0,
            winreg.REG_DWORD,
            hive="HKLM"
        )

    def enable_delivery_optimization(self) -> Tuple[bool, str]:
        """Enable Delivery Optimization (LAN mode)"""
        return self._set_registry_value(
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\DeliveryOptimization\Config",
            "DODownloadMode",
            1,
            winreg.REG_DWORD,
            hive="HKLM"
        )

    # Power Plan methods
    def get_current_power_plan(self) -> str:
        """Get current power plan name"""
        try:
            result = subprocess.run(
                ["powercfg", "/getactivescheme"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.stdout.strip()
        except Exception as exc:
            logger.error(f"Failed to get power plan: {exc}")
            return ""

    def set_power_plan(self, plan: str) -> Tuple[bool, str]:
        """Set power plan by friendly name"""
        plans = {
            "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "ultimate_performance": "e9a42b02-d5df-448d-aa00-03f14749eb61",
        }
        guid = plans.get(plan)
        if not guid:
            return False, "Unknown power plan"

        try:
            result = subprocess.run(
                ["powercfg", "/S", guid],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, f"Power plan set: {plan.replace('_', ' ').title()}"
            return False, result.stderr.strip() or "Failed to set power plan"
        except Exception as exc:
            logger.error(f"Power plan change failed: {exc}")
            return False, str(exc)

    def open_power_options(self) -> Tuple[bool, str]:
        """Open Windows Power Options"""
        try:
            subprocess.Popen(
                ["control.exe", "powercfg.cpl"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, "Power Options opened"
        except Exception as exc:
            return False, str(exc)

    # System Info methods
    def get_system_info(self) -> Tuple[bool, Dict[str, Any]]:
        """Collect basic system info"""
        try:
            import psutil
            info = {
                "cpu_percent": psutil.cpu_percent(interval=0.2),
                "ram_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("C:\\").percent,
                "uptime_seconds": int(psutil.boot_time()),
            }
            return True, info
        except Exception as exc:
            logger.error(f"System info error: {exc}")
            return False, {}

    def get_recommendations(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """Return basic optimization recommendations"""
        recommendations: List[Dict[str, Any]] = []
        success, info = self.get_system_info()
        if not success:
            return False, recommendations

        if info.get("ram_percent", 0) > 80:
            recommendations.append({
                "id": "clear_ram_standby",
                "title": "Clear RAM Standby",
                "reason": "High memory usage detected"
            })
        if info.get("disk_percent", 0) > 85:
            recommendations.append({
                "id": "disk_cleanup",
                "title": "Disk Cleanup",
                "reason": "Disk usage is high"
            })
        if info.get("cpu_percent", 0) > 70:
            recommendations.append({
                "id": "disable_animations",
                "title": "Disable Animations",
                "reason": "High CPU usage detected"
            })

        return True, recommendations
