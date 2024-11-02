import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip

class XMLParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FCPXML Parser")
        
        # Button to load the XML
        self.load_button = tk.Button(root, text="Load XML", command=self.load_xml)
        self.load_button.pack(pady=10)
        
        # Display area for chapter markers
        self.chapter_display = tk.Text(root, wrap="word", width=60, height=20)
        self.chapter_display.pack(pady=10)
        
        # Button to copy chapter markers to clipboard
        self.copy_button = tk.Button(root, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(pady=10)

        self.chapter_data = ""

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
                self.root.update()
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
                        for chapter_marker in asset_clip.findall('chapter-marker'):
                            start = chapter_marker.get('start')
                            value = chapter_marker.get('value')
                            if start and value:
                                marker_text = f"{start} - {value}\n"
                                self.chapter_data += marker_text
                                self.chapter_display.insert(tk.END, marker_text)
            
            # If no chapter data was found, show a message
            if not self.chapter_data:
                self.chapter_display.insert(tk.END, "No chapter markers found.")
            self.root.update()  # Update display after insertion

        except ET.ParseError:
            messagebox.showerror("Parse Error", "Failed to parse the XML file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
