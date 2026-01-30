"""
System Tray Management
Handles system tray icon and menu using pystray
"""

import pystray
from PIL import Image, ImageDraw, ImageFont
import threading
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils.tool_registry import ToolRegistry

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


def create_tray_icon_image():
    """
    Create tray icon image that works on both light and dark taskbars
    
    Returns:
        PIL Image object
    """
    # Create a 64x64 image with transparent background
    image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a rounded rectangle background
    # Use a color that works on both light and dark backgrounds
    bg_color = (108, 92, 231, 255)  # Purple color
    draw.rounded_rectangle([8, 8, 56, 56], radius=8, fill=bg_color)
    
    # Draw a simple "L" for Launcher in white
    try:
        # Try to use a font if available
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw "L" text
    draw.text((20, 16), 'L', fill='white', font=font)
    
    # Convert to RGB for pystray (it doesn't support RGBA well)
    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
    rgb_image.paste(image, mask=image.split()[3])  # Use alpha channel as mask
    
    return rgb_image


def create_tray_icon(app_instance, config_manager, process_service, cleanup_service, on_settings=None):
    """
    Create system tray icon with menu
    
    Args:
        app_instance: Main AppLauncher instance
        config_manager: ConfigManager instance
        process_service: ProcessService instance
        cleanup_service: CleanupService instance
        on_settings: Callback for settings menu item
        
    Returns:
        pystray.Icon instance
    """
    # Create icon image
    image = create_tray_icon_image()
    
    # Get projects for quick launch (all projects, not just favorites)
    projects = config_manager.load_projects()
    
    # Create menu items
    menu_items = []

    tool_registry = ToolRegistry()
    services = {"cleanup_service": cleanup_service, "cleanup": cleanup_service}
    context = {"config_manager": config_manager}
    tool_registry.register_from_config(config_manager.tools or {}, services, context)

    def get_tool_handler(tool_id: str):
        handler = tool_registry.get_handler(tool_id)
        if handler:
            return handler
        logger.warning(f"Tray tool handler missing for {tool_id}")
        return lambda: (False, "Tool not configured")
    
    # Open App Launcher
    menu_items.append(
        pystray.MenuItem(
            'Open App Launcher',
            lambda icon, item: show_window(app_instance)
        )
    )
    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Quick Launch submenu
    if projects:
        quick_launch_items = []
        for project in projects[:20]:  # Limit to 20 projects
            project_name = project.get('name', 'Unnamed')
            quick_launch_items.append(
                pystray.MenuItem(
                    project_name,
                    lambda icon, item, p=project: launch_project(p, process_service)
                )
            )
        menu_items.append(
            pystray.MenuItem('Quick Launch', pystray.Menu(*quick_launch_items))
        )
    else:
        menu_items.append(
            pystray.MenuItem('Quick Launch', None, enabled=False)
        )
    
    # Utilities submenu
    utilities_items = [
        pystray.MenuItem(
            'Empty Recycle Bin',
            lambda icon, item: run_utility(
                get_tool_handler("empty_recycle_bin"),
                "Empty Recycle Bin"
            )
        ),
        pystray.MenuItem(
            'Clear Temp Files',
            lambda icon, item: run_utility(
                get_tool_handler("clear_temp_files"),
                "Clear Temp Files"
            )
        ),
        pystray.MenuItem(
            'Flush DNS',
            lambda icon, item: run_utility(
                get_tool_handler("flush_dns"),
                "Flush DNS"
            )
        ),
        pystray.MenuItem(
            'Clear Prefetch',
            lambda icon, item: run_utility(
                get_tool_handler("clear_prefetch"),
                "Clear Prefetch"
            )
        ),
        pystray.MenuItem(
            'Clear RAM Standby',
            lambda icon, item: run_utility(
                get_tool_handler("clear_standby_ram"),
                "Clear RAM Standby"
            )
        ),
        pystray.MenuItem(
            'Restart Explorer',
            lambda icon, item: run_utility(
                get_tool_handler("restart_explorer"),
                "Restart Explorer"
            )
        ),
    ]
    menu_items.append(
        pystray.MenuItem('Utilities', pystray.Menu(*utilities_items))
    )
    
    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Settings
    settings_callback = on_settings if on_settings else lambda: show_settings(app_instance)
    menu_items.append(
        pystray.MenuItem(
            'Settings',
            lambda icon, item: settings_callback()
        )
    )
    
    # Exit
    menu_items.append(
        pystray.MenuItem(
            'Exit',
            lambda icon, item: exit_app(app_instance)
        )
    )
    
    # Create menu
    menu = pystray.Menu(*menu_items)
    
    # Create icon with default action (left-click) to show window
    icon = pystray.Icon(
        "App Launcher",
        image,
        "James's Project Launcher",
        menu,
        default_action=lambda icon: show_window(app_instance)
    )
    
    return icon


def show_window(app_instance):
    """Show and restore the main window"""
    if app_instance:
        try:
            app_instance.after(0, lambda: _show_window_safe(app_instance))
        except Exception as e:
            logger.error(f"Error showing window: {e}")


def _show_window_safe(app_instance):
    """Thread-safe window show operation"""
    try:
        app_instance.deiconify()
        app_instance.lift()
        app_instance.focus_force()
        app_instance.update()
    except Exception as e:
        logger.error(f"Error in _show_window_safe: {e}")


def launch_project(project, process_service):
    """Launch a project from tray menu"""
    try:
        success, message = process_service.launch_project(project)
        if success:
            logger.info(f"Launched project: {project.get('name', 'Unknown')}")
        else:
            logger.warning(f"Failed to launch project: {message}")
    except Exception as e:
        logger.error(f"Error launching project: {e}")


def run_utility(utility_func, name):
    """Run a utility function and show notification"""
    try:
        result = utility_func()
        if isinstance(result, tuple):
            success, message = result
            if success:
                show_notification("Success", f"{name}: {message}")
            else:
                show_notification("Error", f"{name}: {message}")
        else:
            show_notification("Info", f"{name} completed")
    except Exception as e:
        logger.error(f"Error running utility {name}: {e}")
        show_notification("Error", f"{name} failed: {str(e)}")


def show_settings(app_instance):
    """Show settings"""
    show_window(app_instance)
    if hasattr(app_instance, 'open_settings'):
        app_instance.after(0, app_instance.open_settings)


def exit_app(app_instance):
    """Exit the application"""
    if app_instance:
        try:
            # Stop the tray icon first
            if hasattr(app_instance, 'tray_icon') and app_instance.tray_icon:
                app_instance.tray_icon.stop()
            
            # Then quit the app
            app_instance.after(0, lambda: _quit_app_safe(app_instance))
        except Exception as e:
            logger.error(f"Error exiting app: {e}")


def _quit_app_safe(app_instance):
    """Thread-safe app quit operation"""
    try:
        if hasattr(app_instance, 'quit_app'):
            app_instance.quit_app()
        else:
            app_instance.quit()
            app_instance.destroy()
    except Exception as e:
        logger.error(f"Error in _quit_app_safe: {e}")


def show_notification(title, message):
    """
    Show a Windows notification
    
    Args:
        title: Notification title
        message: Notification message
    """
    try:
        # Use pystray's notification if available
        # Note: pystray notifications may not work on all systems
        # For Windows, we can use win10toast or similar
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(title, message, duration=3, threaded=True)
        except ImportError:
            # Fallback: just log it
            logger.info(f"Notification: {title} - {message}")
    except Exception as e:
        logger.debug(f"Could not show notification: {e}")


def run_tray_icon(icon):
    """Run the tray icon in a separate thread"""
    try:
        icon.run()
    except Exception as e:
        logger.error(f"Error running tray icon: {e}")


def start_tray_icon(app_instance, config_manager, process_service, cleanup_service, on_settings=None):
    """
    Start the system tray icon in a background thread
    
    Args:
        app_instance: Main AppLauncher instance
        config_manager: ConfigManager instance
        process_service: ProcessService instance
        cleanup_service: CleanupService instance
        on_settings: Callback for settings menu item
        
    Returns:
        pystray.Icon instance
    """
    try:
        icon = create_tray_icon(
            app_instance,
            config_manager,
            process_service,
            cleanup_service,
            on_settings
        )
        
        # Run tray icon in a separate thread
        # Note: pystray.run() blocks, so we run it in a separate thread
        tray_thread = threading.Thread(
            target=run_tray_icon,
            args=(icon,),
            daemon=True  # Daemon thread so it exits when main thread exits
        )
        tray_thread.start()
        
        logger.info("System tray icon started")
        return icon
    except Exception as e:
        logger.error(f"Failed to start tray icon: {e}")
        return None
