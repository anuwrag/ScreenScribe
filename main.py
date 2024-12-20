import os
import time
import keyboard
import pyautogui
from PIL import Image, ImageDraw
from pynput import mouse, keyboard as keyboard_listener
from markdown2 import markdown
import pdfkit
import pytesseract
import threading
from tkinter import ttk

class InstallationRecorder:
    def __init__(self):
        self.working_directory = None
        self.screenshots_dir = None
        self.markdown_file = None
        self.recording = False
        self.step_counter = 1
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_typed_text = ""
        self.cancel_requested = False

    def set_working_directory(self, directory):
        """Sets the working directory and creates necessary subdirectories with timestamp."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.working_directory = os.path.join(directory, timestamp)
        os.makedirs(self.working_directory, exist_ok=True)
        self.screenshots_dir = os.path.join(self.working_directory, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.markdown_file = os.path.join(self.working_directory, f"installation_steps_{timestamp}.md")

    def start_recording(self):
        """Starts recording mouse clicks, keyboard events, and screenshots."""
        # Create new timestamped directory before starting
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.working_directory = os.path.join(os.path.dirname(self.working_directory), timestamp)
        os.makedirs(self.working_directory, exist_ok=True)
        
        # Create new screenshots directory
        self.screenshots_dir = os.path.join(self.working_directory, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Update markdown file path with new timestamp
        self.markdown_file = os.path.join(self.working_directory, f"installation_steps_{timestamp}.md")
        
        # Start recording
        self.recording = True
        self.step_counter = 1
        self.last_typed_text = ""
        
        # Initialize new markdown file
        with open(self.markdown_file, "w", encoding='utf-8') as f:
            f.write("# Software Installation Steps\n\n")
        
        # Start listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()
        self.keyboard_listener = keyboard_listener.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def stop_recording(self):
        """Stops recording mouse clicks and keyboard events."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.recording = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def on_click(self, x, y, button, pressed):
        """Handles mouse click events."""
        if pressed and self.recording:
            try:
                # Get active window info
                window = pyautogui.getActiveWindow()
                if window is None:
                    print("No active window found")
                    return

                # Capture only the active window
                screenshot = pyautogui.screenshot(region=(
                    window.left, window.top, 
                    window.width, window.height
                ))

                # Resize image if too large (max width 800px while maintaining aspect ratio)
                max_width = 800
                if screenshot.width > max_width:
                    aspect_ratio = screenshot.height / screenshot.width
                    new_width = max_width
                    new_height = int(max_width * aspect_ratio)
                    screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Save screenshot
                screenshot_path = os.path.join(self.screenshots_dir, f"step_{self.step_counter}.png")
                screenshot.save(screenshot_path, optimize=True, quality=85)  # Compress image

                # Adjust click coordinates relative to window
                relative_x = x - window.left
                relative_y = y - window.top

                # Scale coordinates if image was resized
                if screenshot.width != window.width:
                    scale_factor = screenshot.width / window.width
                    relative_x = int(relative_x * scale_factor)
                    relative_y = int(relative_y * scale_factor)

                # Annotate screenshot
                self.annotate_screenshot(screenshot_path, relative_x, relative_y)

                # Get window title
                window_title = window.title

                # Get clicked element text (using OCR - needs improvement)
                clicked_text = self.get_text_around_click(relative_x, relative_y, screenshot)

                # Write to markdown file
                with open(self.markdown_file, "a", encoding='utf-8') as f:
                    f.write(f"## Step {self.step_counter}: {window_title}\n\n")
                    if clicked_text:
                        f.write(f"Clicked on: **{clicked_text}**\n\n")
                    # Add HTML styling to center and constrain image
                    f.write(f'<div style="text-align: center;"><img src="{screenshot_path}" style="max-width: 100%; height: auto;"></div>\n\n')

                self.step_counter += 1
            except Exception as e:
                print(f"Error recording click: {e}")
                import traceback
                traceback.print_exc()

    def annotate_screenshot(self, image_path, x, y):
            """Annotates the screenshot with an 'x' at the click location."""
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            draw.text((x - 5, y - 5), "x", fill="red")  # Using 'x' as annotation
            image.save(image_path)

    def get_text_around_click(self, x, y, screenshot):
        """Grabs the text around the click region using pytesseract."""
        try:
            width, height = screenshot.size
            left = max(0, x - 50)
            top = max(0, y - 20)
            right = min(width, x + 50)
            bottom = min(height, y + 20)

            if right <= left:
                right = left + 1

            cropped_image = screenshot.crop((left, top, right, bottom))

            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            text = pytesseract.image_to_string(cropped_image)
            return text.strip()
        except Exception as e:
            print(f"Error performing OCR: {e}")
            return ""

    def on_key_press(self, key):
        """Handles keyboard press events."""
        if self.recording:
            try:
                if key == keyboard_listener.Key.enter:
                    with open(self.markdown_file, "a", encoding='utf-8') as f:
                        f.write(f"**Typed:** {self.last_typed_text}\n\n")
                    self.last_typed_text = ""
                elif key == keyboard_listener.Key.ctrl_l or key == keyboard_listener.Key.ctrl_r:
                    # Handle Ctrl key combinations (e.g., Ctrl+C, Ctrl+V)
                    # TODO: Implement logic to detect and record Ctrl key combinations
                    pass
                else:
                    try:
                        self.last_typed_text += key.char
                    except AttributeError:
                        # Handle special keys (e.g., backspace, space)
                        self.last_typed_text += f"[{key.name}]"
            except Exception as e:
                print(f"Error recording key press: {e}")

    def convert_to_pdf(self):
        """Converts the markdown file to PDF."""
        self.cancel_requested = False
        if self.markdown_file:
            try:
                print("Starting PDF conversion...")
                
                print("Reading markdown file...")
                encodings = ['utf-8', 'latin-1', 'cp1252']
                markdown_content = None
                
                for encoding in encodings:
                    try:
                        with open(self.markdown_file, "r", encoding=encoding) as f:
                            markdown_content = f.read()
                            print(f"Successfully read file using {encoding} encoding")
                            break
                    except UnicodeDecodeError:
                        print(f"Failed to read with {encoding} encoding, trying next...")
                        continue
                
                if markdown_content is None:
                    raise Exception("Could not read the markdown file with any supported encoding")

                print("Converting markdown to HTML...")
                # Add CSS for image handling
                css = """
                <style>
                    img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
                    body { max-width: 1000px; margin: 0 auto; padding: 20px; }
                </style>
                """
                html = css + markdown(markdown_content)

                pdf_file = os.path.join(self.working_directory, "installation_steps.pdf")
                
                print("Setting up wkhtmltopdf configuration...")
                wkhtmltopdf_path = 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
                if not os.path.exists(wkhtmltopdf_path):
                    print(f"ERROR: wkhtmltopdf not found at {wkhtmltopdf_path}")
                    return
                    
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                
                # Add options for better image handling
                options = {
                    'enable-local-file-access': None,
                    'encoding': 'UTF-8',
                    'image-quality': 85,
                    'margin-top': '20mm',
                    'margin-right': '20mm',
                    'margin-bottom': '20mm',
                    'margin-left': '20mm',
                    'quiet': None
                }
                
                if self.cancel_requested:
                    print("Conversion cancelled by user")
                    return
                    
                pdfkit.from_string(html, pdf_file, configuration=config, options=options)
                print(f"PDF successfully saved to {pdf_file}")

            except Exception as e:
                print(f"Error converting to PDF: {str(e)}")
                traceback.print_exc()

# Example usage with basic GUI using Tkinter
import tkinter as tk
from tkinter import filedialog

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        working_directory_label.config(text=directory)
        recorder.set_working_directory(directory)
        start_button.config(state=tk.NORMAL)

def start_recording():
    recorder.start_recording()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_recording():
    recorder.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def cancel_conversion():
    recorder.cancel_requested = True
    pdf_button.config(state=tk.NORMAL, text="Convert to PDF")
    progress_bar.pack_forget()
    cancel_button.pack_forget()
    
def convert_to_pdf():
    def conversion_thread():
        try:
            recorder.convert_to_pdf()
        except Exception as e:
            print(f"Error in conversion thread: {e}")
        finally:
            pdf_button.config(state=tk.NORMAL, text="Convert to PDF")
            progress_bar.pack_forget()
            cancel_button.pack_forget()
            root.update()

    pdf_button.config(state=tk.DISABLED, text="Converting...")
    progress_bar.pack()
    cancel_button.pack()
    root.update()

    thread = threading.Thread(target=conversion_thread)
    thread.daemon = True
    thread.start()

recorder = InstallationRecorder()

root = tk.Tk()
root.title("Installation Recorder")
root.minsize(400, 200)  # Set minimum width to 400px

working_directory_label = tk.Label(root, text="Select working directory:")
working_directory_label.pack()

browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.pack()

start_button = tk.Button(root, text="Start Recording", command=start_recording, state=tk.DISABLED)
start_button.pack()

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, state=tk.DISABLED)
stop_button.pack()

pdf_button = tk.Button(root, text="Convert to PDF", command=convert_to_pdf)
pdf_button.pack()

progress_bar = ttk.Progressbar(
    root, 
    mode='indeterminate',
    length=200
)
progress_bar.pack_forget()  # Hide initially

cancel_button = tk.Button(root, text="Cancel Conversion", command=cancel_conversion)
cancel_button.pack()
cancel_button.pack_forget()  # Hide initially

# Start progress bar animation
progress_bar.start(10)

root.mainloop()