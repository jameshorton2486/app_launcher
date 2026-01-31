"""
Utility Button Component
Button with icon, title, loading spinner, and visual feedback
"""

import customtkinter as ctk
import sys
import os
import threading
import tkinter as tk

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.theme import COLORS


class UtilityButton(ctk.CTkFrame):
    """Button component for utilities with visual feedback and loading spinner"""
    
    def __init__(self, parent, icon: str, title: str, subtitle: str = "", command=None, tooltip: str = "", width=80, height=80, requires_admin=False, accent_color=None):
        """
        Initialize utility button
        
        Args:
            parent: Parent widget
            icon: Icon emoji or text
            title: Button title
            subtitle: Optional subtitle/description
            command: Command to execute (should return tuple[bool, str] or None)
            tooltip: Tooltip description
            width: Button width (default 80)
            height: Button height (default 80)
            requires_admin: Whether tool requires admin privileges
            accent_color: Accent color for this button (category color)
        """
        super().__init__(
            parent,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=14,
            border_width=2,
            border_color=COLORS['border_subtle'],
            width=width,
            height=height
        )
        
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.command = command
        self.tooltip = tooltip
        self.is_running = False
        self.requires_admin = requires_admin
        self.accent_color = accent_color or COLORS['accent_primary']
        
        self.setup_ui()
        
        # Add tooltip if provided
        if tooltip:
            self._create_tooltip()
    
    def setup_ui(self):
        """Set up the button UI"""
        # Admin badge container (positioned absolutely)
        if self.requires_admin:
            self.admin_badge = ctk.CTkLabel(
                self,
                text="🔒",
                font=('Segoe UI', 14),
                text_color=COLORS['warning'],
                fg_color='transparent'
            )
            self.admin_badge.place(relx=0.85, rely=0.1, anchor='ne')
        
        # Icon/Spinner container
        self.icon_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.icon_frame.pack(pady=(10, 4))
        
        # Icon label with accent color
        self.icon_label = ctk.CTkLabel(
            self.icon_frame,
            text=self.icon,
            font=('Segoe UI', 36),  # Larger, more attractive icons
            text_color=self.accent_color
        )
        self.icon_label.pack()
        
        # Loading spinner (hidden by default)
        self.spinner_label = ctk.CTkLabel(
            self.icon_frame,
            text="⟳",
            font=('Segoe UI', 24),
            text_color=COLORS['accent_warning']
        )
        
        # Success checkmark (hidden by default)
        self.success_label = ctk.CTkLabel(
            self.icon_frame,
            text="✓",
            font=('Segoe UI', 24),
            text_color=COLORS['accent_success']
        )
        
        # Error X (hidden by default)
        self.error_label = ctk.CTkLabel(
            self.icon_frame,
            text="✗",
            font=('Segoe UI', 24),
            text_color=COLORS['accent_danger']
        )
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=('Segoe UI', 10, 'bold'),
            text_color=COLORS['text_primary'],
            wraplength=70
        )
        self.title_label.pack(pady=(0, 2))
        
        # Subtitle
        if self.subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self,
                text=self.subtitle,
                font=('Segoe UI', 8),
                text_color=COLORS['text_secondary'],
                wraplength=70
            )
            self.subtitle_label.pack(pady=(0, 4))
        
        # Status message (hidden by default)
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=('Segoe UI', 8),
            text_color=COLORS['text_muted'],
            wraplength=70
        )
        self.status_label.pack(pady=(0, 4))
        
        # Bind click
        self.bind('<Button-1>', self.on_click)
        for widget in self.winfo_children():
            widget.bind('<Button-1>', self.on_click)
        
        # Hover effect
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        for widget in self.winfo_children():
            widget.bind('<Enter>', self.on_enter)
            widget.bind('<Leave>', self.on_leave)
    
    def _create_tooltip(self):
        """Create a tooltip for the button"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=self.tooltip,
                background=COLORS['bg_secondary'],
                foreground=COLORS['text_primary'],
                relief='solid',
                borderwidth=1,
                font=('Segoe UI', 9),
                padx=8,
                pady=4,
                wraplength=200
            )
            label.pack()
            self.tooltip_window = tooltip
        
        def on_leave(event):
            if hasattr(self, 'tooltip_window'):
                self.tooltip_window.destroy()
                delattr(self, 'tooltip_window')
        
        self.bind('<Enter>', on_enter)
        self.bind('<Leave>', on_leave)
    
    def on_enter(self, event=None):
        """Handle mouse enter"""
        if not self.is_running:
            self.configure(border_color=self.accent_color)
            self.configure(fg_color=COLORS['bg_hover'])
            # Elevate slightly on hover
            self.configure(corner_radius=16)
            # Brighten icon on hover
            self.icon_label.configure(text_color=self.accent_color)
    
    def on_leave(self, event=None):
        """Handle mouse leave"""
        if not self.is_running:
            self.configure(border_color=COLORS['border_subtle'])
            self.configure(fg_color=COLORS['bg_tertiary'])
            self.configure(corner_radius=14)
            self.icon_label.configure(text_color=self.accent_color)
    
    def on_click(self, event=None):
        """Handle button click"""
        if self.is_running or not self.command:
            return
        
        self.execute_command()
    
    def execute_command(self):
        """Execute the command with visual feedback"""
        self.is_running = True
        self.configure(border_color=COLORS['accent_warning'])
        self.configure(fg_color=COLORS['bg_tertiary'])
        
        # Hide icon, show spinner
        self.icon_label.pack_forget()
        self.spinner_label.pack()
        self.status_label.configure(text="Running...", text_color=COLORS['accent_warning'])
        self.status_label.pack()
        
        # Animate spinner
        self._animate_spinner()
        
        def run_command():
            try:
                result = self.command()
                if result is None:
                    # Command doesn't return result (like launching external apps)
                    self.after(0, lambda: self.set_success("Launched"))
                elif isinstance(result, tuple):
                    success, message = result
                    if success:
                        self.after(0, lambda: self.set_success(message))
                    else:
                        self.after(0, lambda: self.set_error(message))
                elif isinstance(result, bool):
                    # Just a boolean result
                    if result:
                        self.after(0, lambda: self.set_success("Completed"))
                    else:
                        self.after(0, lambda: self.set_error("Failed"))
                else:
                    self.after(0, lambda: self.set_success("Completed"))
            except Exception as e:
                self.after(0, lambda: self.set_error(str(e)))
        
        threading.Thread(target=run_command, daemon=True).start()
    
    def _animate_spinner(self):
        """Animate the loading spinner"""
        if not self.is_running:
            return
        
        # Rotate spinner character
        spinner_chars = ['⟳', '⟲', '⟳', '⟲']
        if hasattr(self, '_spinner_index'):
            self._spinner_index = (self._spinner_index + 1) % len(spinner_chars)
        else:
            self._spinner_index = 0
        
        self.spinner_label.configure(text=spinner_chars[self._spinner_index])
        self.after(200, self._animate_spinner)
    
    def set_success(self, message: str = "Success"):
        """Set success state"""
        self.is_running = False
        self.configure(border_color=COLORS['accent_success'])
        self.configure(fg_color=COLORS['bg_secondary'])
        
        # Hide spinner, show success checkmark
        self.spinner_label.pack_forget()
        self.error_label.pack_forget()
        self.success_label.pack()
        
        # Show message
        self.status_label.configure(text=message[:25], text_color=COLORS['accent_success'])
        
        # Reset after 3 seconds
        self.after(3000, self.reset_state)
    
    def set_error(self, message: str = "Error"):
        """Set error state"""
        self.is_running = False
        self.configure(border_color=COLORS['accent_danger'])
        self.configure(fg_color=COLORS['bg_secondary'])
        
        # Hide spinner, show error X
        self.spinner_label.pack_forget()
        self.success_label.pack_forget()
        self.error_label.pack()
        
        # Show message
        self.status_label.configure(text=message[:25], text_color=COLORS['accent_danger'])
        
        # Reset after 5 seconds
        self.after(5000, self.reset_state)
    
    def reset_state(self):
        """Reset button to default state"""
        self.is_running = False
        self.status_label.configure(text="")
        self.status_label.pack_forget()
        
        # Hide all feedback icons, show original icon
        self.spinner_label.pack_forget()
        self.success_label.pack_forget()
        self.error_label.pack_forget()
        self.icon_label.pack()
        
        self.configure(border_color=COLORS['border_subtle'])
        self.configure(fg_color=COLORS['bg_tertiary'])
        self.configure(corner_radius=12)
        
        if hasattr(self, '_spinner_index'):
            delattr(self, '_spinner_index')
