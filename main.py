import xml.etree.ElementTree as ET
import tkinter as tk
import os
from tkinter import ttk, messagebox, filedialog
import subprocess
import platform
import sys
from tkinter import font as tkfont
from tkinterdnd2 import TkinterDnD, DND_FILES

class XMLParserApp:
    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title("FinalTimeCode")
        
        # Define file types for dialogs
        self.file_types = [
            ('Final Cut Pro XML Library', '*.fcpxmld'),
            ('All files', '*.*')
        ]
        
        # Configure macOS-specific settings
        if platform.system() == 'Darwin':
            try:
                self.root.createcommand('tk::mac::Quit', self.root.destroy)
                self.root.createcommand('tk::mac::ShowPreferences', self.show_preferences)
                self.root.createcommand('::tk::mac::OpenDocument', self.handle_file_open)
            except:
                pass  # Ignore if commands aren't available
        
        # Configure styling
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TFrame', background='systemWindowBackgroundColor')
        
        # Main container with padding
        main_container = ttk.Frame(root, padding="12")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Button frame with modern layout - now just for copy button
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 12))
        button_frame.columnconfigure(0, weight=1)
        
        # Copy button - centered
        self.copy_button = ttk.Button(
            button_frame, 
            text="Copy to Clipboard", 
            command=self.copy_to_clipboard,
            style='TButton'
        )
        self.copy_button.grid(row=0, column=0)
        
        # Create the drop zone frame
        self.drop_frame = ttk.Frame(main_container, style='Drop.TFrame')
        self.drop_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        self.drop_frame.columnconfigure(0, weight=1)
        self.drop_frame.rowconfigure(0, weight=1)
        
        # Style for the drop zone
        self.style.configure('Drop.TFrame', borderwidth=2, relief='dashed')
        
        # Drop zone label
        self.drop_label = ttk.Label(
            self.drop_frame,
            text="Drop FCPXMLD file here\nor double-click to open",
            justify='center',
            font=tkfont.Font(size=13)
        )
        self.drop_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Text display frame
        text_frame = ttk.Frame(main_container)
        text_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Scrollbar configuration
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.chapter_display = tk.Text(
            text_frame,
            wrap="word",
            undo=True,
            height=15,
            font=('SF Pro Text', 13),
            borderwidth=1,
            relief="solid",
            yscrollcommand=scrollbar.set
        )
        self.chapter_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.configure(command=self.chapter_display.yview)
        
        # Configure grid weights for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # Initialize variables
        self.chapter_data = ""
        self.hourly_length = False
        
        # Set minimum window size
        root.minsize(500, 400)

        # Setup drag and drop
        self.setup_drag_drop()
        
        # Click handling
        self.drop_frame.bind('<Button-1>', self.on_click)
        self.drop_label.bind('<Button-1>', self.on_click)
        
        # Handle initial file if provided
        if initial_file:
            self.root.after(100, lambda: self.load_xml_file(initial_file))

    def setup_drag_drop(self):
        """Setup drag and drop for the drop frame"""
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_frame.dnd_bind('<<DragEnter>>', self.handle_drag_enter)
        self.drop_frame.dnd_bind('<<DragLeave>>', self.handle_drag_leave)

    def handle_drag_enter(self, event):
        """Handle drag enter event"""
        self.style.configure('Drop.TFrame', borderwidth=2, relief='solid')
        self.drop_label.configure(text="Release to load file")

    def handle_drag_leave(self, event):
        """Handle drag leave event"""
        self.style.configure('Drop.TFrame', borderwidth=2, relief='dashed')
        self.drop_label.configure(text="Drop FCPXMLD file here\nor double-click to open")

    def handle_drop(self, event):
        """Handle drop event"""
        self.style.configure('Drop.TFrame', borderwidth=2, relief='dashed')
        self.drop_label.configure(text="Drop FCPXMLD file here\nor double-click to open")
        
        file_path = event.data
        if platform.system() == 'Darwin':
            # On macOS, convert the file URI to a path
            if file_path.startswith('file://'):
                file_path = file_path[7:]
        elif platform.system() == 'Windows':
            # Handle Windows file path formatting
            file_path = file_path.strip('{}')  # Remove curly braces if present
            
        self.load_xml_file(file_path)

    def on_click(self, event):
        """Handle click on drop zone"""
        file_path = filedialog.askopenfilename(
            title="Select FCPXMLD Bundle",
            filetypes=self.file_types,
            parent=self.root
        )
        if file_path:
            self.load_xml_file(file_path)

    def handle_file_open(self, *args):
        """Handle file open events from macOS"""
        for file_path in args:
            self.load_xml_file(file_path)

    def show_preferences(self):
        """Show preferences dialog"""
        messagebox.showinfo("Preferences", "Preferences dialog would show here")

    def check_timestamps(self, asset_clip):
        """Check timestamps in asset clip"""
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

    def load_xml_file(self, file_path):
        """Load XML file from a given path"""
        self.hourly_length = False
        self.chapter_display.delete(1.0, tk.END)
        self.chapter_data = ""

        # Handle both directory and file paths
        if file_path.endswith('.fcpxmld'):
            dir_path = file_path
        else:
            dir_path = os.path.dirname(file_path)

        xml_path = os.path.join(dir_path, 'info.fcpxml')

        if not os.path.isfile(xml_path):
            messagebox.showerror("File Error", "info.fcpxml not found in the selected directory.", parent=self.root)
            return
            
        try:
            tree = ET.parse(xml_path)
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
        """Format time string to appropriate format"""
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
        """Copy chapter data to clipboard"""
        if self.chapter_data:
            if platform.system() == 'Darwin':
                process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
                process.communicate(self.chapter_data.encode('utf-8'))
            else:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.chapter_data)
            messagebox.showinfo("Success", "Chapter markers copied to clipboard!", parent=self.root)
        else:
            messagebox.showwarning("No Data", "No chapter markers to copy.", parent=self.root)

def main():
    root = TkinterDnD.Tk()
    root.geometry("400x300")
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = XMLParserApp(root, initial_file)
    root.mainloop()

if __name__ == "__main__":
    main()

#pyinstaller --onefile --windowed --icon=./resources/icon.icns --name FinalTimeCode --hidden-import=tkinterdnd2 --debug=all main.py