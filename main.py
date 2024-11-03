import xml.etree.ElementTree as ET
import tkinter as tk
import os
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform

class XMLParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinalTimeCode")
        
        # Configure macOS-specific settings
        if platform.system() == 'Darwin':  # macOS
            self.root.createcommand('tk::mac::Quit', self.root.destroy)
            self.root.createcommand('tk::mac::ShowPreferences', self.show_preferences)
        
        # Configure styling
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TFrame', background='systemWindowBackgroundColor')
        
        # Main container with padding
        main_container = ttk.Frame(root, padding="12")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Button frame with modern layout
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        button_frame.columnconfigure(1, weight=1)  # Space between buttons
        
        # Modern buttons with proper spacing
        self.load_button = ttk.Button(
            button_frame, 
            text="Load XML", 
            command=self.load_xml,
            style='TButton'
        )
        self.load_button.grid(row=0, column=0, padx=(0, 6))
        
        self.copy_button = ttk.Button(
            button_frame, 
            text="Copy to Clipboard", 
            command=self.copy_to_clipboard,
            style='TButton'
        )
        self.copy_button.grid(row=0, column=2, padx=(6, 0))
        
        # Text display with native appearance
        text_frame = ttk.Frame(main_container)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Scrollbar configuration
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.chapter_display = tk.Text(
            text_frame,
            wrap="word",
            undo=True,
            height=20,
            font=('SF Pro Text', 13),  # macOS system font
            borderwidth=1,
            relief="solid",
            yscrollcommand=scrollbar.set
        )
        self.chapter_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.configure(command=self.chapter_display.yview)
        
        # Configure grid weights for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Initialize variables
        self.chapter_data = ""
        self.hourly_length = False
        
        # Set minimum window size
        root.minsize(500, 400)

    def show_preferences(self):
        # Placeholder for preferences dialog
        messagebox.showinfo("Preferences", "Preferences dialog would show here")

    def check_timestamps(self, asset_clip):
        for chapter_marker in asset_clip.findall('chapter-marker'):
            time_str = chapter_marker.get('start')
            if time_str:
                if 's' in time_str:
                    time_str = time_str.replace('s', '').strip()
                    if '/' in time_str:
                        seconds, frames = time_str.split('/')
                        total_seconds = int(seconds) / int(frames)
                    else:
                        total_seconds = float(time_str)
                    
                    hours = int(total_seconds // 3600)
                    if hours > 0:
                        self.hourly_length = True

    def load_xml(self):
        self.hourly_length = False
        self.chapter_display.delete(1.0, tk.END)
        self.chapter_data = ""
        
        # Ask for the directory, assuming it's an FCPXMLD bundle
        dir_path = filedialog.askdirectory(
        title="Select FCPXMLD Bundle",
        parent=self.root
    )
    
        if not dir_path:
            return

        file_path = f"{dir_path}/info.fcpxml"
    
        if not os.path.isfile(file_path):
            messagebox.showerror("File Error", "info.fcpxml not found in the selected directory.", parent=self.root)
            return
            
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            library = root.find('library')
            if library is None:
                self.chapter_display.insert(tk.END, "No library element found in XML.")
                return
                
            for event in library.findall('event'):
                for project in event.findall('project'):
                    sequence = project.find('sequence')
                    if sequence is None:
                        continue
                        
                    spine = sequence.find('spine')
                    if spine is None:
                        continue
                        
                    for asset_clip in spine.findall('asset-clip'):
                        self.check_timestamps(asset_clip)
                        for chapter_marker in asset_clip.findall('chapter-marker'):
                            start = chapter_marker.get('start')
                            value = chapter_marker.get('value')
                            if start and value:
                                formatted_start = self.format_time(start)
                                marker_text = f"{formatted_start} - {value}\n"
                                self.chapter_data += marker_text
                                self.chapter_display.insert(tk.END, marker_text)
            
            if not self.chapter_data:
                self.chapter_display.insert(tk.END, "No chapter markers found.")
                
        except ET.ParseError:
            messagebox.showerror("Parse Error", "Failed to parse the XML file.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

    def format_time(self, time_str):
        try:
            if 's' in time_str:
                time_str = time_str.replace('s', '').strip()
                if '/' in time_str:
                    seconds, frames = time_str.split('/')
                    total_seconds = int(seconds) / int(frames)
                else:
                    total_seconds = float(time_str)
                
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                
                if self.hourly_length:
                    return f"{hours:02}:{minutes:02}:{seconds:02}"
                else:
                    return f"{minutes:02}:{seconds:02}"
            return time_str
            
        except Exception as e:
            print(f"Error in time conversion: {e}")
            return time_str

    def copy_to_clipboard(self):
        if self.chapter_data:
            # Use pbcopy for macOS clipboard with UTF-8 encoding
            process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
            process.communicate(self.chapter_data.encode('utf-8'))
            messagebox.showinfo("Success", "Chapter markers copied to clipboard!", parent=self.root)
        else:
            messagebox.showwarning("No Data", "No chapter markers to copy.", parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLParserApp(root)
    root.mainloop()
    #pyinstaller --onefile --windowed --icon=./resources/icon.icns --name FinalTimeCode --debug=all main.py

    