import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import os
import tempfile
import threading

CONFIG_FILE = "app_launcher_config.json"

# Modern Color Theme
THEME = {
    'bg_primary': '#1e1e2e',      # Dark blue-gray background
    'bg_secondary': '#2a2a3e',   # Slightly lighter for frames
    'bg_tertiary': '#3a3a4e',    # Even lighter for listbox
    'accent_primary': '#6c5ce7',  # Purple accent
    'accent_secondary': '#00d2d3', # Cyan accent
    'accent_success': '#00b894',   # Green for launch
    'accent_danger': '#d63031',    # Red for remove
    'text_primary': '#ffffff',     # White text
    'text_secondary': '#b8b8b8',   # Light gray text
    'text_muted': '#888888',       # Muted gray
    'border': '#4a4a5e',          # Border color
    'selection': '#6c5ce7',        # Selection highlight
    'hover': '#7d6ef0',           # Hover state
}


class AppLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("James's Project Launcher")
        self.root.geometry("700x550")
        self.root.configure(bg=THEME['bg_primary'])

        self.apps = self.load_apps()
        self.setup_theme()
        self.setup_ui()

    def setup_theme(self):
        """Configure ttk styles with modern theme."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure main frame style
        style.configure('Main.TFrame', background=THEME['bg_primary'])
        style.configure('Card.TFrame', background=THEME['bg_secondary'], relief='flat')
        
        # Configure label styles
        style.configure('Title.TLabel', 
                       background=THEME['bg_primary'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 24, 'bold'))
        style.configure('Subtitle.TLabel',
                       background=THEME['bg_primary'],
                       foreground=THEME['text_secondary'],
                       font=('Segoe UI', 11))
        
        # Configure button styles
        style.configure('Launch.TButton',
                       background=THEME['accent_success'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       borderwidth=0,
                       focuscolor='none')
        style.map('Launch.TButton',
                 background=[('active', '#00a085'), ('pressed', '#008f75')])
        
        style.configure('Add.TButton',
                       background=THEME['accent_primary'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       borderwidth=0,
                       focuscolor='none')
        style.map('Add.TButton',
                 background=[('active', THEME['hover']), ('pressed', '#5a4dd7')])
        
        style.configure('Remove.TButton',
                       background=THEME['accent_danger'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       borderwidth=0,
                       focuscolor='none')
        style.map('Remove.TButton',
                 background=[('active', '#c02020'), ('pressed', '#b01010')])
        
        style.configure('Save.TButton',
                       background=THEME['accent_primary'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=8,
                       borderwidth=0,
                       focuscolor='none')
        style.map('Save.TButton',
                 background=[('active', THEME['hover']), ('pressed', '#5a4dd7')])
        
        style.configure('Browse.TButton',
                       background=THEME['bg_tertiary'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 9),
                       padding=6,
                       borderwidth=0,
                       focuscolor='none')
        style.map('Browse.TButton',
                 background=[('active', '#4a4a5e'), ('pressed', '#5a5a6e')])
        
        # Configure entry styles
        style.configure('Modern.TEntry',
                       fieldbackground=THEME['bg_tertiary'],
                       foreground=THEME['text_primary'],
                       borderwidth=2,
                       relief='flat',
                       padding=8)
        style.map('Modern.TEntry',
                 bordercolor=[('focus', THEME['accent_primary'])])
        
        # Configure label styles for dialog
        style.configure('Dialog.TLabel',
                       background=THEME['bg_secondary'],
                       foreground=THEME['text_primary'],
                       font=('Segoe UI', 10))

    def setup_ui(self):
        """Setup the main UI components."""
        # Main container with padding
        self.frame = ttk.Frame(self.root, style='Main.TFrame', padding="30")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title section
        title_frame = ttk.Frame(self.frame, style='Main.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Project Dashboard", style='Title.TLabel')
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Manage and launch your applications", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor='w', pady=(5, 0))

        # Card frame for listbox
        card_frame = ttk.Frame(self.frame, style='Card.TFrame', padding="15")
        card_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        # Listbox with custom styling
        listbox_frame = tk.Frame(card_frame, bg=THEME['bg_tertiary'], relief='flat', bd=0)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(listbox_frame,
                                  height=12,
                                  font=('Segoe UI', 11),
                                  bg=THEME['bg_tertiary'],
                                  fg=THEME['text_primary'],
                                  selectbackground=THEME['selection'],
                                  selectforeground=THEME['text_primary'],
                                  selectborderwidth=0,
                                  activestyle='none',
                                  borderwidth=0,
                                  highlightthickness=0,
                                  relief='flat')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(bg=THEME['bg_tertiary'],
                        troughcolor=THEME['bg_secondary'],
                        activebackground=THEME['accent_primary'],
                        borderwidth=0,
                        highlightthickness=0)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.update_listbox()

        # Button frame
        btn_frame = ttk.Frame(self.frame, style='Main.TFrame')
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        launch_btn = ttk.Button(btn_frame, text="🚀 Launch", command=self.launch_app, style='Launch.TButton')
        launch_btn.pack(side=tk.LEFT, padx=(0, 10))

        add_btn = ttk.Button(btn_frame, text="➕ Add App", command=self.add_app_window, style='Add.TButton')
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        remove_btn = ttk.Button(btn_frame, text="🗑️ Remove", command=self.remove_app, style='Remove.TButton')
        remove_btn.pack(side=tk.LEFT)
        
        # Allow double-click to launch
        self.listbox.bind('<Double-Button-1>', lambda e: self.launch_app())

    def normalize_path(self, path):
        """Normalize and clean a file path."""
        if not path:
            return path
        return os.path.normpath(path.strip().strip('"').strip("'"))

    def load_apps(self):
        """Load apps from config file with error handling."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    apps = json.loads(content)
                    # Validate and clean up apps
                    valid_apps = []
                    for app in apps:
                        if isinstance(app, dict) and all(key in app for key in ['name', 'path', 'script']):
                            # Normalize paths and remove extra quotes
                            app['path'] = self.normalize_path(app['path'])
                            app['script'] = self.normalize_path(app['script'])
                            valid_apps.append(app)
                    return valid_apps
            except json.JSONDecodeError:
                messagebox.showerror("Error", f"Invalid JSON in {CONFIG_FILE}. File will be reset.")
                return []
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {str(e)}")
                return []
        return []

    def save_apps(self):
        """Save apps to config file with error handling."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.apps, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")

    def update_listbox(self):
        """Update the listbox with current apps."""
        self.listbox.delete(0, tk.END)
        for app in self.apps:
            # Format with icon and spacing for better visual appeal
            self.listbox.insert(tk.END, f"  📱 {app['name']}")
        
        # If no apps, show a message
        if not self.apps:
            self.listbox.insert(tk.END, "  No applications registered yet")
            self.listbox.itemconfig(0, {'fg': THEME['text_muted']})

    def browse_directory(self, entry_widget):
        """Browse for directory and update entry widget."""
        directory = filedialog.askdirectory()
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def browse_script(self, entry_widget):
        """Browse for script file and update entry widget."""
        script = filedialog.askopenfilename(
            title="Select Script File",
            filetypes=[("All Files", "*.*"), ("Python", "*.py"), ("PowerShell", "*.ps1"), ("Batch", "*.bat"), ("Executable", "*.exe")]
        )
        if script:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, script)

    def add_app_window(self):
        """Open window to add a new app."""
        add_win = tk.Toplevel(self.root)
        add_win.title("Register New Project")
        add_win.transient(self.root)
        add_win.grab_set()
        add_win.geometry("550x350")
        add_win.configure(bg=THEME['bg_primary'])
        
        # Main frame with theme
        main_frame = ttk.Frame(add_win, style='Main.TFrame', padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="➕ Register New Project", style='Title.TLabel')
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # App Name field
        name_label = ttk.Label(form_frame, text="App Name:", style='Dialog.TLabel')
        name_label.grid(row=0, column=0, padx=10, pady=12, sticky="e")
        name_ent = ttk.Entry(form_frame, width=35, style='Modern.TEntry', font=('Segoe UI', 10))
        name_ent.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        name_ent.focus()
        form_frame.columnconfigure(1, weight=1)

        # Directory field
        dir_label = ttk.Label(form_frame, text="Directory:", style='Dialog.TLabel')
        dir_label.grid(row=1, column=0, padx=10, pady=12, sticky="e")
        dir_ent = ttk.Entry(form_frame, width=35, style='Modern.TEntry', font=('Segoe UI', 10))
        default_path = os.path.expanduser("~")
        dir_ent.insert(0, default_path)
        dir_ent.grid(row=1, column=1, padx=10, pady=12, sticky="ew")
        browse_dir_btn = ttk.Button(form_frame, text="Browse", command=lambda: self.browse_directory(dir_ent), style='Browse.TButton')
        browse_dir_btn.grid(row=1, column=2, padx=5, pady=12)

        # Script field
        script_label = ttk.Label(form_frame, text="Script:", style='Dialog.TLabel')
        script_label.grid(row=2, column=0, padx=10, pady=12, sticky="e")
        script_ent = ttk.Entry(form_frame, width=35, style='Modern.TEntry', font=('Segoe UI', 10))
        script_ent.grid(row=2, column=1, padx=10, pady=12, sticky="ew")
        browse_script_btn = ttk.Button(form_frame, text="Browse", command=lambda: self.browse_script(script_ent), style='Browse.TButton')
        browse_script_btn.grid(row=2, column=2, padx=5, pady=12)

        # Button frame
        btn_frame = ttk.Frame(main_frame, style='Main.TFrame')
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        def save():
            """Validate and save the new app."""
            name = name_ent.get().strip()
            path = dir_ent.get().strip()
            script = script_ent.get().strip()

            # Validation
            if not name:
                messagebox.showerror("Validation Error", "App name cannot be empty.")
                return

            if not path:
                messagebox.showerror("Validation Error", "Directory path cannot be empty.")
                return

            if not os.path.isdir(path):
                messagebox.showerror("Validation Error", f"Directory does not exist: {path}")
                return

            if not script:
                messagebox.showerror("Validation Error", "Script path cannot be empty.")
                return

            if not os.path.isfile(script):
                messagebox.showerror("Validation Error", f"Script file does not exist: {script}")
                return

            # Check for duplicate names
            if any(app['name'].lower() == name.lower() for app in self.apps):
                if not messagebox.askyesno("Duplicate Name", f"An app named '{name}' already exists. Overwrite?"):
                    return
                # Remove existing app with same name
                self.apps = [app for app in self.apps if app['name'].lower() != name.lower()]

            # Normalize paths
            path = self.normalize_path(path)
            script = self.normalize_path(script)

            self.apps.append({"name": name, "path": path, "script": script})
            self.save_apps()
            self.update_listbox()
            add_win.destroy()
            messagebox.showinfo("Success", f"App '{name}' added successfully.")

        save_btn = ttk.Button(btn_frame, text="💾 Save Project", command=save, style='Save.TButton')
        save_btn.pack(side=tk.RIGHT)
        
        # Allow Enter key to save
        add_win.bind('<Return>', lambda e: save())

    def escape_powershell_path(self, path):
        """Escape a path for use in PowerShell commands."""
        # Replace single quotes with escaped single quotes and wrap in single quotes
        return path.replace("'", "''")

    def launch_app(self):
        """Launch the selected app."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an app to launch.")
            return

        try:
            app = self.apps[selection[0]]
            script = self.normalize_path(app['script'])
            folder = self.normalize_path(app['path'])

            # Validate paths exist
            if not os.path.isdir(folder):
                messagebox.showerror("Error", f"Directory does not exist: {folder}")
                return

            if not os.path.isfile(script):
                messagebox.showerror("Error", f"Script file does not exist: {script}")
                return

            # Determine file extension
            script_ext = os.path.splitext(script)[1].lower()
            
            # Create startup info to hide console window (for cmd.exe calls)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Build command based on file type
            if script_ext == ".ps1":
                # PowerShell script - use WindowStyle Hidden and NoProfile to suppress console
                script_escaped = self.escape_powershell_path(script)
                folder_escaped = self.escape_powershell_path(folder)
                # Use -NoProfile to skip profile loading (faster, less output)
                # Use -WindowStyle Hidden to hide the PowerShell window
                # Use -NonInteractive to prevent prompts
                cmd = [
                    'powershell.exe',
                    '-NoProfile',
                    '-NonInteractive',
                    '-ExecutionPolicy', 'Bypass',
                    '-WindowStyle', 'Hidden',
                    '-Command',
                    f"Set-Location -LiteralPath '{folder_escaped}'; & '{script_escaped}'"
                ]
                # Use CREATE_NO_WINDOW flag for additional hiding
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            elif script_ext == ".py":
                # Python script - use pythonw.exe directly (no console window)
                # pythonw.exe is specifically designed to run Python scripts without console
                pythonw_path = os.path.join(os.path.dirname(os.__file__), 'pythonw.exe')
                if not os.path.exists(pythonw_path):
                    # Fallback: try to find pythonw in PATH
                    pythonw_path = 'pythonw.exe'
                subprocess.Popen([pythonw_path, script], cwd=folder, creationflags=subprocess.CREATE_NO_WINDOW)
            elif script_ext == ".bat" or script_ext == ".cmd":
                # Batch script - use VBScript wrapper to hide console window
                # Create a temporary VBScript that runs the batch file hidden
                vbs_script = tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False, encoding='utf-8')
                vbs_script.write(f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{folder.replace(chr(92), chr(92)+chr(92))}"
WshShell.Run "cmd.exe /c ""{script.replace(chr(92), chr(92)+chr(92))}""", 0, False
Set WshShell = Nothing''')
                vbs_script.close()
                # Run VBScript (which will be hidden)
                subprocess.Popen(['wscript.exe', vbs_script.name], creationflags=subprocess.CREATE_NO_WINDOW)
                # Clean up VBScript after a delay (non-blocking)
                def cleanup_vbs():
                    import time
                    time.sleep(2)
                    try:
                        os.unlink(vbs_script.name)
                    except:
                        pass
                threading.Thread(target=cleanup_vbs, daemon=True).start()
            elif script_ext == ".exe":
                # Executable - launch directly without console wrapper
                subprocess.Popen([script], cwd=folder, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # Default: try to execute directly with hidden console
                subprocess.Popen([script], cwd=folder, creationflags=subprocess.CREATE_NO_WINDOW)
        except (KeyError, IndexError):
            messagebox.showerror("Error", "Invalid app selection.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch app: {str(e)}")

    def remove_app(self):
        """Remove the selected app."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an app to remove.")
            return

        try:
            app_name = self.apps[selection[0]]['name']
            if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{app_name}'?"):
                self.apps.pop(selection[0])
                self.save_apps()
                self.update_listbox()
                messagebox.showinfo("Success", f"App '{app_name}' removed successfully.")
        except IndexError:
            messagebox.showerror("Error", "Invalid app selection.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove app: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = AppLauncher(root)
    root.mainloop()