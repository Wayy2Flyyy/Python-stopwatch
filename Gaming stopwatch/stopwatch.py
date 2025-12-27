import tkinter as tk
from tkinter import ttk, messagebox
import time
import psutil
from datetime import datetime
import json
import os

class StopwatchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Stopwatch")
        self.root.geometry("700x700")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, False)
        
        # Stopwatch state
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.lap_times = []
        self.lap_count = 0
        
        # Task tracking
        self.selected_task = None
        self.task_start_time = None
        self.session_history = []
        self.history_file = "task_history.json"
        self.load_history()
        
        # Common applications and keywords
        self.app_keywords = [
            'game', 'steam', 'epic', 'origin', 'uplay', 'battle',
            'minecraft', 'roblox', 'fortnite', 'valorant', 'league',
            'dota', 'csgo', 'overwatch', 'apex', 'gta', 'pubg',
            'cod', 'warzone', 'fifa', 'nba', 'madden', 'rocket',
            'discord', 'obs', 'twitch', 'code', 'studio', 'chrome',
            'firefox', 'edge', 'excel', 'word', 'powerpoint', 'photoshop',
            'spotify', 'slack', 'teams', 'zoom', 'blender', 'unity',
            'rider', 'pycharm', 'intellij', 'eclipse', 'notepad++'
        ]
        
        # System processes to exclude
        self.excluded_processes = [
            'svchost', 'system', 'registry', 'smss', 'csrss', 'wininit',
            'services', 'lsass', 'winlogon', 'dwm', 'conhost', 'fontdrvhost',
            'taskhostw', 'sihost', 'ctfmon', 'explorer', 'searchhost',
            'startmenuexperiencehost', 'runtimebroker', 'applicationframehost',
            'systemsettings', 'shellexperiencehost', 'textinputhost',
            'securityhealthservice', 'msedgewebview2', 'backgroundtaskhost',
            'dashost', 'audiodg', 'wudfhost', 'spoolsv', 'dllhost',
            'searchprotocolhost', 'searchfilterhost', 'searchindexer',
            'microsoftedgeupdate', 'taskeng', 'consent', 'userinit',
            'winstore', 'lockapp', 'gamebarpresencewriter', 'widget',
            'widgetservice', 'csrss', 'lsass', 'sppsvc', 'wlanext',
            'nvcontainer', 'nvdisplay.container', 'igfxem', 'igfxtray',
            'python', 'pythonw'  # Exclude Python to avoid showing the stopwatch itself
        ]
        
        self.setup_ui()
        self.update_time()
        self.update_running_apps()
        
    def load_history(self):
        """Load task history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.session_history = json.load(f)
            except:
                self.session_history = []
    
    def save_history(self):
        """Save task history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.session_history, f, indent=2)
        except:
            pass
    
    def get_running_apps(self):
        """Get list of running user applications (excluding system processes)"""
        apps = {}
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
                try:
                    name = proc.info['name']
                    if not name or not name.endswith('.exe'):
                        continue
                    
                    # Remove .exe extension
                    display_name = name[:-4]
                    
                    # Skip if in excluded list
                    if display_name.lower() in self.excluded_processes:
                        continue
                    
                    # Only include processes with a window or known apps
                    # Filter out most system processes
                    if self.is_user_app(proc, display_name):
                        apps[display_name] = proc.info
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except:
            pass
        return apps
    
    def is_user_app(self, proc, app_name):
        """Check if process is a user-facing application"""
        try:
            # Check if it's a known priority app
            if self.is_priority_app(app_name):
                return True
            
            # Get the executable path
            exe = proc.info.get('exe')
            if not exe:
                return False
            
            exe_lower = exe.lower()
            
            # Exclude Windows system directories
            system_paths = [
                'c:\\windows\\system32',
                'c:\\windows\\syswow64',
                'c:\\windows\\winsxs',
                'c:\\program files\\windows',
                'c:\\program files (x86)\\windows'
            ]
            
            if any(path in exe_lower for path in system_paths):
                return False
            
            # Include if in common app directories
            app_paths = [
                'program files',
                'users\\',
                'appdata',
                'steam',
                'epic games'
            ]
            
            if any(path in exe_lower for path in app_paths):
                return True
            
            return False
            
        except:
            return False
    
    def is_priority_app(self, app_name):
        """Check if application is a priority/common app"""
        app_lower = app_name.lower()
        return any(keyword in app_lower for keyword in self.app_keywords)
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="⏱️ TASK STOPWATCH", 
            font=("Arial", 20, "bold"),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        title_label.pack(pady=15)
        
        # Task selection frame
        task_frame = tk.LabelFrame(
            self.root,
            text="Application Selection",
            font=("Arial", 12, "bold"),
            fg='#ffaa00',
            bg='#1a1a1a',
            relief=tk.RAISED,
            bd=2
        )
        task_frame.pack(pady=10, padx=40, fill=tk.X)
        
        # Dropdown and refresh button
        select_frame = tk.Frame(task_frame, bg='#1a1a1a')
        select_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.task_var = tk.StringVar()
        self.task_dropdown = ttk.Combobox(
            select_frame,
            textvariable=self.task_var,
            font=("Arial", 11),
            state='readonly',
            width=35
        )
        self.task_dropdown.pack(side=tk.LEFT, padx=5)
        self.task_dropdown.bind('<<ComboboxSelected>>', self.on_task_selected)
        
        refresh_btn = tk.Button(
            select_frame,
            text="🔄 Refresh",
            font=("Arial", 10, "bold"),
            bg='#0066cc',
            fg='white',
            command=self.update_running_apps,
            relief=tk.RAISED,
            bd=2
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Selected task label
        self.selected_label = tk.Label(
            task_frame,
            text="No application selected",
            font=("Arial", 10),
            fg='#888888',
            bg='#1a1a1a'
        )
        self.selected_label.pack(pady=5)
        
        # Time display frame
        time_frame = tk.Frame(self.root, bg='#2a2a2a', relief=tk.RAISED, bd=3)
        time_frame.pack(pady=15, padx=40, fill=tk.X)
        
        self.time_label = tk.Label(
            time_frame,
            text="00:00:00.00",
            font=("Digital-7 Mono", 42, "bold"),
            fg='#00ffff',
            bg='#2a2a2a',
            pady=15
        )
        self.time_label.pack()
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=15)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(
            button_frame,
            text="START",
            font=("Arial", 13, "bold"),
            bg='#00aa00',
            fg='white',
            activebackground='#00dd00',
            width=9,
            height=2,
            command=self.start_stop,
            relief=tk.RAISED,
            bd=3
        )
        self.start_stop_btn.grid(row=0, column=0, padx=8)
        
        # Lap button
        self.lap_btn = tk.Button(
            button_frame,
            text="LAP",
            font=("Arial", 13, "bold"),
            bg='#0066cc',
            fg='white',
            activebackground='#0088ff',
            width=9,
            height=2,
            command=self.record_lap,
            relief=tk.RAISED,
            bd=3,
            state=tk.DISABLED
        )
        self.lap_btn.grid(row=0, column=1, padx=8)
        
        # Reset button
        self.reset_btn = tk.Button(
            button_frame,
            text="RESET",
            font=("Arial", 13, "bold"),
            bg='#cc0000',
            fg='white',
            activebackground='#ff0000',
            width=9,
            height=2,
            command=self.reset,
            relief=tk.RAISED,
            bd=3
        )
        self.reset_btn.grid(row=0, column=2, padx=8)
        
        # Lap times frame
        lap_frame = tk.Frame(self.root, bg='#1a1a1a')
        lap_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)
        
        lap_title = tk.Label(
            lap_frame,
            text="Session Laps",
            font=("Arial", 12, "bold"),
            fg='#ffaa00',
            bg='#1a1a1a'
        )
        lap_title.pack()
        
        # Scrollable lap times list
        list_frame = tk.Frame(lap_frame, bg='#2a2a2a', relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lap_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 10),
            bg='#2a2a2a',
            fg='#ffffff',
            selectbackground='#0066cc',
            yscrollcommand=scrollbar.set,
            height=6
        )
        self.lap_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lap_listbox.yview)
        
        # History button
        history_btn = tk.Button(
            self.root,
            text="📊 View History",
            font=("Arial", 11, "bold"),
            bg='#664400',
            fg='white',
            command=self.show_history,
            relief=tk.RAISED,
            bd=2
        )
        history_btn.pack(pady=10)
    
    def update_running_apps(self):
        """Update the dropdown with running applications"""
        apps = self.get_running_apps()
        
        # Separate priority apps from other apps
        priority_apps = []
        other_apps = []
        
        for app_name in sorted(apps.keys()):
            if self.is_priority_app(app_name):
                priority_apps.append(app_name)
            else:
                other_apps.append(app_name)
        
        # Combine lists (priority apps first)
        all_apps = priority_apps + other_apps
        
        self.task_dropdown['values'] = all_apps
        if all_apps and not self.task_var.get():
            self.task_dropdown.current(0)
    
    def on_task_selected(self, event=None):
        """Handle task selection"""
        selected = self.task_var.get()
        if selected:
            self.selected_label.config(
                text=f"Selected: {selected}",
                fg='#00ff00'
            )
    
    def format_time(self, seconds):
        """Format time as HH:MM:SS.ms"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 100)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:02d}"
    
    def update_time(self):
        """Update the time display"""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
        
        time_str = self.format_time(self.elapsed_time)
        self.time_label.config(text=time_str)
        
        # Update every 10ms
        self.root.after(10, self.update_time)
    
    def start_stop(self):
        """Toggle start/stop"""
        if not self.running:
            # Start
            selected = self.task_var.get()
            if selected:
                self.selected_task = selected
                self.task_start_time = datetime.now()
            
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.start_stop_btn.config(text="STOP", bg='#cc6600', activebackground='#ff8800')
            self.lap_btn.config(state=tk.NORMAL)
            self.task_dropdown.config(state=tk.DISABLED)
        else:
            # Stop
            self.running = False
            self.start_stop_btn.config(text="START", bg='#00aa00', activebackground='#00dd00')
            self.lap_btn.config(state=tk.DISABLED)
            self.task_dropdown.config(state='readonly')
            
            # Save session to history
            if self.selected_task and self.elapsed_time > 0:
                session = {
                    'task': self.selected_task,
                    'start_time': self.task_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'duration': self.elapsed_time,
                    'duration_formatted': self.format_time(self.elapsed_time),
                    'laps': len(self.lap_times)
                }
                self.session_history.append(session)
                self.save_history()
    
    def record_lap(self):
        """Record a lap time"""
        if self.running:
            self.lap_count += 1
            lap_time = self.elapsed_time
            
            # Calculate split time (time since last lap)
            if self.lap_times:
                split_time = lap_time - self.lap_times[-1]
            else:
                split_time = lap_time
            
            self.lap_times.append(lap_time)
            
            # Format and display
            lap_str = f"Lap {self.lap_count:02d}:  {self.format_time(lap_time)}  (+{self.format_time(split_time)})"
            self.lap_listbox.insert(tk.END, lap_str)
            self.lap_listbox.see(tk.END)  # Auto-scroll to latest
            
            # Highlight fastest and slowest laps
            if len(self.lap_times) > 1:
                self.highlight_laps()
    
    def highlight_laps(self):
        """Highlight fastest (green) and slowest (red) lap splits"""
        if len(self.lap_times) < 2:
            return
        
        # Calculate split times
        splits = [self.lap_times[0]]
        for i in range(1, len(self.lap_times)):
            splits.append(self.lap_times[i] - self.lap_times[i-1])
        
        fastest_idx = splits.index(min(splits))
        slowest_idx = splits.index(max(splits))
        
        # Clear previous highlights
        for i in range(self.lap_listbox.size()):
            self.lap_listbox.itemconfig(i, bg='#2a2a2a', fg='#ffffff')
        
        # Apply highlights
        self.lap_listbox.itemconfig(fastest_idx, fg='#00ff00')
        self.lap_listbox.itemconfig(slowest_idx, fg='#ff4444')
    
    def reset(self):
        """Reset the stopwatch"""
        self.running = False
        self.elapsed_time = 0
        self.start_time = 0
        self.lap_times = []
        self.lap_count = 0
        
        self.time_label.config(text="00:00:00.00")
        self.start_stop_btn.config(text="START", bg='#00aa00', activebackground='#00dd00')
        self.lap_btn.config(state=tk.DISABLED)
        self.lap_listbox.delete(0, tk.END)
        self.task_dropdown.config(state='readonly')
    
    def show_history(self):
        """Show session history in a new window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Task Session History")
        history_window.geometry("700x500")
        history_window.configure(bg='#1a1a1a')
        
        title = tk.Label(
            history_window,
            text="📊 Task Session History",
            font=("Arial", 16, "bold"),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        title.pack(pady=15)
        
        # Stats frame
        stats_frame = tk.Frame(history_window, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        stats_frame.pack(pady=10, padx=20, fill=tk.X)
        
        if self.session_history:
            total_time = sum(s['duration'] for s in self.session_history)
            total_sessions = len(self.session_history)
            
            stats_text = f"Total Sessions: {total_sessions}  |  Total Time: {self.format_time(total_time)}"
            stats_label = tk.Label(
                stats_frame,
                text=stats_text,
                font=("Arial", 12, "bold"),
                fg='#00ffff',
                bg='#2a2a2a',
                pady=10
            )
            stats_label.pack()
        
        # History list frame
        list_frame = tk.Frame(history_window, bg='#2a2a2a', relief=tk.SUNKEN, bd=2)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 10),
            bg='#2a2a2a',
            fg='#ffffff',
            selectbackground='#0066cc',
            yscrollcommand=scrollbar.set
        )
        history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=history_listbox.yview)
        
        # Populate history
        if self.session_history:
            for i, session in enumerate(reversed(self.session_history), 1):
                task_name = session.get('task', session.get('game', 'Unknown'))
                entry = f"{i}. {session['start_time']} | {task_name[:30]:<30} | {session['duration_formatted']} | {session['laps']} laps"
                history_listbox.insert(tk.END, entry)
        else:
            history_listbox.insert(tk.END, "No task sessions recorded yet.")
        
        # Clear history button
        clear_btn = tk.Button(
            history_window,
            text="🗑️ Clear History",
            font=("Arial", 11, "bold"),
            bg='#cc0000',
            fg='white',
            command=lambda: self.clear_history(history_window),
            relief=tk.RAISED,
            bd=2
        )
        clear_btn.pack(pady=15)
    
    def clear_history(self, window):
        """Clear session history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all session history?"):
            self.session_history = []
            self.save_history()
            window.destroy()
            messagebox.showinfo("Success", "Session history cleared!")

def main():
    root = tk.Tk()
    app = StopwatchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="⏱️ GAMING STOPWATCH", 
            font=("Arial", 20, "bold"),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        title_label.pack(pady=20)
        
        # Time display frame
        time_frame = tk.Frame(self.root, bg='#2a2a2a', relief=tk.RAISED, bd=3)
        time_frame.pack(pady=20, padx=40, fill=tk.X)
        
        self.time_label = tk.Label(
            time_frame,
            text="00:00:00.00",
            font=("Digital-7 Mono", 48, "bold"),
            fg='#00ffff',
            bg='#2a2a2a',
            pady=20
        )
        self.time_label.pack()
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=20)
        
        # Start/Stop button
        self.start_stop_btn = tk.Button(
            button_frame,
            text="START",
            font=("Arial", 14, "bold"),
            bg='#00aa00',
            fg='white',
            activebackground='#00dd00',
            width=10,
            height=2,
            command=self.start_stop,
            relief=tk.RAISED,
            bd=3
        )
        self.start_stop_btn.grid(row=0, column=0, padx=10)
        
        # Lap button
        self.lap_btn = tk.Button(
            button_frame,
            text="LAP",
            font=("Arial", 14, "bold"),
            bg='#0066cc',
            fg='white',
            activebackground='#0088ff',
            width=10,
            height=2,
            command=self.record_lap,
            relief=tk.RAISED,
            bd=3,
            state=tk.DISABLED
        )
        self.lap_btn.grid(row=0, column=1, padx=10)
        
        # Reset button
        self.reset_btn = tk.Button(
            button_frame,
            text="RESET",
            font=("Arial", 14, "bold"),
            bg='#cc0000',
            fg='white',
            activebackground='#ff0000',
            width=10,
            height=2,
            command=self.reset,
            relief=tk.RAISED,
            bd=3
        )
        self.reset_btn.grid(row=0, column=2, padx=10)
        
        # Lap times frame
        lap_frame = tk.Frame(self.root, bg='#1a1a1a')
        lap_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)
        
        lap_title = tk.Label(
            lap_frame,
            text="Lap Times",
            font=("Arial", 14, "bold"),
            fg='#ffaa00',
            bg='#1a1a1a'
        )
        lap_title.pack()
        
        # Scrollable lap times list
        list_frame = tk.Frame(lap_frame, bg='#2a2a2a', relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lap_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 11),
            bg='#2a2a2a',
            fg='#ffffff',
            selectbackground='#0066cc',
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.lap_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lap_listbox.yview)
        
    def format_time(self, seconds):
        """Format time as HH:MM:SS.ms"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 100)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:02d}"
    
    def update_time(self):
        """Update the time display"""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
        
        time_str = self.format_time(self.elapsed_time)
        self.time_label.config(text=time_str)
        
        # Update every 10ms
        self.root.after(10, self.update_time)
    
    def start_stop(self):
        """Toggle start/stop"""
        if not self.running:
            # Start
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.start_stop_btn.config(text="STOP", bg='#cc6600', activebackground='#ff8800')
            self.lap_btn.config(state=tk.NORMAL)
        else:
            # Stop
            self.running = False
            self.start_stop_btn.config(text="START", bg='#00aa00', activebackground='#00dd00')
            self.lap_btn.config(state=tk.DISABLED)
    
    def record_lap(self):
        """Record a lap time"""
        if self.running:
            self.lap_count += 1
            lap_time = self.elapsed_time
            
            # Calculate split time (time since last lap)
            if self.lap_times:
                split_time = lap_time - self.lap_times[-1]
            else:
                split_time = lap_time
            
            self.lap_times.append(lap_time)
            
            # Format and display
            lap_str = f"Lap {self.lap_count:02d}:  {self.format_time(lap_time)}  (+{self.format_time(split_time)})"
            self.lap_listbox.insert(tk.END, lap_str)
            self.lap_listbox.see(tk.END)  # Auto-scroll to latest
            
            # Highlight fastest and slowest laps
            if len(self.lap_times) > 1:
                self.highlight_laps()
    
    def highlight_laps(self):
        """Highlight fastest (green) and slowest (red) lap splits"""
        if len(self.lap_times) < 2:
            return
        
        # Calculate split times
        splits = [self.lap_times[0]]
        for i in range(1, len(self.lap_times)):
            splits.append(self.lap_times[i] - self.lap_times[i-1])
        
        fastest_idx = splits.index(min(splits))
        slowest_idx = splits.index(max(splits))
        
        # Clear previous highlights
        for i in range(self.lap_listbox.size()):
            self.lap_listbox.itemconfig(i, bg='#2a2a2a', fg='#ffffff')
        
        # Apply highlights
        self.lap_listbox.itemconfig(fastest_idx, fg='#00ff00')
        self.lap_listbox.itemconfig(slowest_idx, fg='#ff4444')
    
    def reset(self):
        """Reset the stopwatch"""
        self.running = False
        self.elapsed_time = 0
        self.start_time = 0
        self.lap_times = []
        self.lap_count = 0
        
        self.time_label.config(text="00:00:00.00")
        self.start_stop_btn.config(text="START", bg='#00aa00', activebackground='#00dd00')
        self.lap_btn.config(state=tk.DISABLED)
        self.lap_listbox.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = StopwatchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
