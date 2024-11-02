import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip
from tkinter import font as tkfont

class XMLParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinalTimeCode")
        self.root.geometry("500x400")  # Set a fixed window size
        
        # Set a custom font for buttons
        self.custom_font = tkfont.Font(family="Arial", size=12)

        # Frame for buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Button to load the XML
        self.load_button = tk.Button(button_frame, text="Load XML", command=self.load_xml, font=self.custom_font, bg="#444444", fg="white")
        self.load_button.pack(side=tk.LEFT, padx=10)

        # Button to copy chapter markers to clipboard
        self.copy_button = tk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, font=self.custom_font, bg="#444444", fg="white")
        self.copy_button.pack(side=tk.LEFT, padx=10)

        # Display area for chapter markers
        self.chapter_display = tk.Text(root, wrap="word", width=60, height=20, bg="#222222", fg="white", insertbackground='white')
        self.chapter_display.pack(pady=10)

        self.chapter_data = ""

        # Set color for the text area
        self.chapter_display.tag_configure("tag_name", foreground="yellow")
        self.hourly_length = False
        # self.chapter_data = ""

    def check_timestamps(self, asset_clip):
        for chapter_marker in asset_clip.findall('chapter-marker'):
            time_str = chapter_marker.get('start')
            if time_str:
                if 's' in time_str:
                    time_str = time_str.replace('s', '').strip()  # Remove 's'
                    if '/' in time_str:
                        # Handle the format with frames (e.g., '1073/15')
                        seconds, frames = time_str.split('/')
                        total_seconds = int(seconds) / int(frames)  # Convert frames to seconds
                    else:
                        # Pure seconds format
                        total_seconds = float(time_str)

                    # Format total seconds to HH
                    hours = int(total_seconds // 3600)

                    if hours > 0:
                        self.hourly_length = True

    def load_xml(self):
        # Clear previous data in both variables and text display
        self.chapter_display.delete(1.0, tk.END)
        self.chapter_data = ""

        file_path = filedialog.askopenfilename(filetypes=[("FCPXML Files", "*.fcpxml")])
        if not file_path:
            messagebox.showwarning("No file selected", "Please select a valid FCPXML file.")
            return

        try:
            # Load and parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract project information
            library = root.find('library')
            if library is None:
                self.chapter_display.insert(tk.END, "No library element found in XML.")
                self.chapter_display.update_idletasks()  # Force update for MacOS
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
                                # Use after method for better compatibility on MacOS
                                self.root.after(0, lambda text=marker_text: self.chapter_display.insert(tk.END, text))
            
            # If no chapter data was found, show a message
            if not self.chapter_data:
                self.chapter_display.insert(tk.END, "No chapter markers found.")
            self.chapter_display.update_idletasks()  # Final forced update

        except ET.ParseError:
            messagebox.showerror("Parse Error", "Failed to parse the XML file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def format_time(self, time_str):
        """Convert time from FCPXML format to HH:MM:SS or MM:SS."""
        try:
            if 's' in time_str:
                time_str = time_str.replace('s', '').strip()  # Remove 's'
                if '/' in time_str:
                    # Handle the format with frames (e.g., '1073/15')
                    seconds, frames = time_str.split('/')
                    total_seconds = int(seconds) / int(frames)  # Convert frames to seconds
                else:
                    # Pure seconds format
                    total_seconds = float(time_str)
                
                # Format total seconds to HH:MM:SS or MM:SS
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                
                if self.hourly_length:
                    return f"{hours:02}:{minutes:02}:{seconds:02}"  # HH:MM:SS format
                else:
                    return f"{minutes:02}:{seconds:02}"  # MM:SS format, omit hours
            else:
                return time_str  # Return the original string if no 's' present
        except Exception as e:
            print(f"Error in time conversion: {e}")
            return time_str  # Return original string in case of error

    def copy_to_clipboard(self):
        if self.chapter_data:
            pyperclip.copy(self.chapter_data)
            messagebox.showinfo("Copied", "Chapter markers copied to clipboard!")
        else:
            messagebox.showwarning("No Data", "No chapter markers to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLParserApp(root)
    root.mainloop()
