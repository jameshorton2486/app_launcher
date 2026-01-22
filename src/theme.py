"""
Theme system for App Launcher
Defines color palette and CustomTkinter theme configuration
"""

# Color palette (dark mode)
COLORS = {
    'bg_primary': '#1a1a2e',      # Main background
    'bg_secondary': '#16213e',     # Cards/panels
    'bg_tertiary': '#0f3460',      # Hover states
    'accent_primary': '#6c5ce7',   # Purple accent (buttons, highlights)
    'accent_secondary': '#00cec9', # Cyan accent (links, icons)
    'accent_success': '#00b894',   # Green (success, git clean)
    'accent_warning': '#fdcb6e',   # Yellow (warnings, git dirty)
    'accent_danger': '#d63031',    # Red (errors, delete)
    'text_primary': '#ffffff',     # Main text
    'text_secondary': '#b2bec3',   # Muted text
    'text_muted': '#636e72',       # Disabled text
    'border': '#2d3436',           # Borders
}

def apply_theme(app, mode=None, accent_color=None):
    """
    Apply theme to CustomTkinter app
    
    Args:
        app: CustomTkinter CTk instance
        mode: Theme mode ('dark', 'light', 'system') - if None, reads from config
        accent_color: Accent color hex string - if None, reads from config
    """
    import customtkinter as ctk
    
    # Get mode from config if not provided
    if mode is None:
        try:
            from src.config_manager import ConfigManager
            config = ConfigManager()
            mode = config.get_setting('theme.mode', 'dark')
        except:
            mode = 'dark'
    
    # Set appearance mode (system mode is supported by CustomTkinter)
    ctk.set_appearance_mode(mode)
    
    # Set default color theme
    ctk.set_default_color_theme("blue")
    
    # Configure custom colors
    # Note: CustomTkinter uses a different color system, so we'll apply these
    # through widget-specific configurations
    
    # If accent color is provided, we could apply it, but CustomTkinter's
    # color system is limited, so we'll keep using the default blue theme
    # and apply custom colors through widget configurations
