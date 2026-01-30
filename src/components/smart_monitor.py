"""
Smart Monitor
Monitors system health and recommends tools to run.
"""

from __future__ import annotations

import os
import socket
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import psutil
except Exception:
    psutil = None

try:
    import winreg
except Exception:
    winreg = None

from src.utils.tool_usage import ToolUsageStore


class SmartMonitor:
    """
    Monitors system health and recommends tools to run.
    Shows visual indicators on Dashboard.
    """

    def __init__(self):
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._callback = None
        self._dispatch = None
        self.latest: Dict[str, Any] = {}
        self.usage_store = ToolUsageStore()

    def start(self, callback, dispatch=None):
        if self._thread and self._thread.is_alive():
            return
        self._callback = callback
        self._dispatch = dispatch
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def scan(self) -> Dict[str, Any]:
        metrics = {}
        recommendations: List[Dict[str, Any]] = []

        metrics["ram"] = self._check_ram()
        metrics["disk"] = self._check_disk()
        metrics["temp"] = self._check_temp_size()
        metrics["dns"] = self._check_dns()
        metrics["recycle"] = self._check_recycle_bin()
        metrics["uptime"] = self._check_uptime()
        metrics["updates"] = self._check_updates()
        metrics["maintenance"] = self._check_last_cleanup()

        for metric in metrics.values():
            recs = metric.get("recommendations", [])
            recommendations.extend(recs)

        attention_count = sum(
            1 for metric in metrics.values()
            if metric.get("status") in {"yellow", "red"}
        )

        result = {
            "metrics": metrics,
            "recommendations": recommendations,
            "attention_count": attention_count,
            "checked_at": datetime.utcnow().isoformat()
        }
        self.latest = result
        return result

    def _run_loop(self):
        while not self._stop_event.is_set():
            result = self.scan()
            if self._callback:
                if self._dispatch:
                    try:
                        self._dispatch(lambda r=result: self._callback(r))
                    except Exception:
                        pass
                else:
                    self._callback(result)
            for _ in range(60):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def _check_ram(self) -> Dict[str, Any]:
        if not psutil:
            return self._metric("RAM Usage", "--", "green")

        usage = psutil.virtual_memory().percent
        status = self._status_for_thresholds(usage, 70, 85)
        metric = self._metric("RAM Usage", f"{usage:.0f}%", status)
        if status != "green":
            strength = "Strongly suggest" if status == "red" else "Suggest"
            metric["recommendations"] = [{
                "message": f"{strength} running 'Clear RAM Standby' to free memory.",
                "tool_id": "clear_ram_standby"
            }]
        return metric

    def _check_disk(self) -> Dict[str, Any]:
        if not psutil:
            return self._metric("Disk Space", "--", "green")

        disk = psutil.disk_usage("C:\\")
        free_percent = 100 - disk.percent
        free_gb = disk.free / (1024 ** 3)
        status = "green"
        if free_percent < 10:
            status = "red"
        elif free_percent < 20:
            status = "yellow"
        metric = self._metric("Disk Space", f"{disk.percent:.0f}% ({free_gb:.0f} GB free)", status)
        if status != "green":
            message = "Disk space is getting low. Run 'Disk Cleanup' to free space."
            if status == "red":
                message = "Disk space is critically low. Run 'Disk Cleanup' and clear temp files."
            metric["recommendations"] = [
                {"message": message, "tool_id": "disk_cleanup"},
                {"message": "Clear temp files to reclaim space.", "tool_id": "clear_temp_files"}
            ]
        return metric

    def _check_temp_size(self) -> Dict[str, Any]:
        temp_path = os.path.expandvars(os.environ.get("TEMP", ""))
        size_bytes = self._dir_size(temp_path) if temp_path else 0
        size_mb = size_bytes / (1024 ** 2)
        status = self._status_for_thresholds(size_mb, 500, 2000)
        metric = self._metric("Temp Files", f"{size_mb:.1f} MB", status)
        if status != "green":
            strength = "Strongly suggest" if status == "red" else "Suggest"
            metric["recommendations"] = [{
                "message": f"{strength} clearing temp files.",
                "tool_id": "clear_temp_files"
            }]
        return metric

    def _check_dns(self) -> Dict[str, Any]:
        start = time.time()
        try:
            socket.gethostbyname("example.com")
            elapsed_ms = (time.time() - start) * 1000
        except Exception:
            elapsed_ms = None

        if elapsed_ms is None:
            metric = self._metric("DNS Response", "Failed", "red")
            metric["recommendations"] = [{
                "message": "DNS resolution is failing. Try flushing DNS.",
                "tool_id": "flush_dns"
            }]
            return metric

        status = self._status_for_thresholds(elapsed_ms, 50, 200)
        metric = self._metric("DNS Response", f"{elapsed_ms:.0f} ms", status)
        if status != "green":
            metric["recommendations"] = [{
                "message": "DNS is slow. Consider flushing DNS.",
                "tool_id": "flush_dns"
            }]
        return metric

    def _check_recycle_bin(self) -> Dict[str, Any]:
        recycle_path = r"C:\$Recycle.Bin"
        size_bytes = self._dir_size(recycle_path)
        size_gb = size_bytes / (1024 ** 3)
        status = "green"
        if size_gb > 5:
            status = "red"
        elif size_gb > 1:
            status = "yellow"
        metric = self._metric("Recycle Bin", f"{size_gb:.2f} GB", status)
        if status != "green":
            strength = "Strongly suggest" if status == "red" else "Suggest"
            metric["recommendations"] = [{
                "message": f"{strength} emptying the Recycle Bin.",
                "tool_id": "empty_recycle_bin"
            }]
        return metric

    def _check_uptime(self) -> Dict[str, Any]:
        if not psutil:
            return self._metric("System Uptime", "--", "green")

        uptime = datetime.utcnow() - datetime.fromtimestamp(psutil.boot_time())
        days = uptime.days
        hours = uptime.seconds // 3600
        label = f"{days} days, {hours} hours"
        status = "green"
        if days >= 14:
            status = "red"
        elif days >= 7:
            status = "yellow"
        metric = self._metric("System Uptime", label, status)
        if status != "green":
            metric["recommendations"] = [{
                "message": "A restart is recommended to maintain performance.",
                "tool_id": None
            }]
        return metric

    def _check_updates(self) -> Dict[str, Any]:
        status = "green"
        label = "Up to date"

        if self._pending_restart():
            status = "red"
            label = "Pending restart"
        else:
            available = self._updates_available()
            if available is True:
                status = "yellow"
                label = "Updates available"
            elif available is None:
                label = "Unknown"

        metric = self._metric("Windows Update", label, status)
        if status != "green":
            metric["recommendations"] = [{
                "message": "Check Windows Update settings.",
                "tool_id": None
            }]
        return metric

    def _check_last_cleanup(self) -> Dict[str, Any]:
        last_cleanup = self.usage_store.get_stats().get("last_full_cleanup")
        if not last_cleanup:
            metric = self._metric("Last Cleanup", "Never", "red")
            metric["recommendations"] = [{
                "message": "Run Quick Cleanup to catch up on maintenance.",
                "action": "quick_cleanup"
            }]
            return metric
        try:
            last_dt = datetime.fromisoformat(last_cleanup)
            days = (datetime.utcnow() - last_dt).days
        except Exception:
            days = 0
        status = "green"
        if days > 30:
            status = "red"
        elif days > 7:
            status = "yellow"
        metric = self._metric("Last Cleanup", f"{days} days ago", status)
        if status != "green":
            metric["recommendations"] = [{
                "message": "It's been a while since your last cleanup.",
                "action": "quick_cleanup"
            }]
        return metric

    @staticmethod
    def _metric(label: str, value: str, status: str) -> Dict[str, Any]:
        return {
            "label": label,
            "value": value,
            "status": status,
            "recommendations": []
        }

    @staticmethod
    def _status_for_thresholds(value: float, yellow_threshold: float, red_threshold: float) -> str:
        if value >= red_threshold:
            return "red"
        if value >= yellow_threshold:
            return "yellow"
        return "green"

    @staticmethod
    def _dir_size(path: str) -> int:
        if not path or not os.path.exists(path):
            return 0
        total = 0
        try:
            for root, dirs, files in os.walk(path):
                for name in files:
                    try:
                        total += os.path.getsize(os.path.join(root, name))
                    except Exception:
                        pass
        except Exception:
            return total
        return total

    def _pending_restart(self) -> bool:
        if not winreg:
            return False
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def _updates_available(self) -> Optional[bool]:
        try:
            import win32com.client  # type: ignore
        except Exception:
            return None
        try:
            session = win32com.client.Dispatch("Microsoft.Update.Session")
            searcher = session.CreateUpdateSearcher()
            result = searcher.Search("IsInstalled=0 and IsHidden=0")
            return result.Updates.Count > 0
        except Exception:
            return None
