import os
import time
import keyboard
import pyautogui
from PIL import Image, ImageDraw
from pynput import mouse, keyboard as keyboard_listener
from markdown2 import markdown
from pdfkit import from_string
import pytesseract

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
        self.recording = True
        self.step_counter = 1
        self.last_typed_text = ""
        with open(self.markdown_file, "w") as f:
            f.write("# Software Installation Steps\n\n")
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
                # Capture screenshot
                screenshot = pyautogui.screenshot()
                screenshot_path = os.path.join(self.screenshots_dir, f"step_{self.step_counter}.png")
                screenshot.save(screenshot_path)

                # Annotate screenshot
                self.annotate_screenshot(screenshot_path, x, y)

                # Get window title
                window_title = pyautogui.getActiveWindowTitle()

                # Get clicked element text (using OCR - needs improvement)
                clicked_text = self.get_text_around_click(x, y)

                # Write to markdown file
                with open(self.markdown_file, "a") as f:
                    f.write(f"## Step {self.step_counter}: {window_title}\n\n")
                    if clicked_text:
                        f.write(f"Clicked on: **{clicked_text}**\n\n")
                    f.write(f"![Step {self.step_counter} Screenshot]({screenshot_path})\n\n")

                self.step_counter += 1
            except Exception as e:
                print(f"Error recording click: {e}")

    def annotate_screenshot(self, image_path, x, y):
        """Annotates the screenshot with a red circle at the click location."""
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        radius = 10
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="red")
        image.save(image_path)

    def get_text_around_click(self, x, y):
        """Grabs the text around the click region using pytesseract."""
        try:
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
            left = max(0, x - 50)
            top = max(0, y - 20)
            right = min(width, x + 50)
            bottom = min(height, y + 20)
            cropped_image = screenshot.crop((left, top, right, bottom))
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
                    with open(self.markdown_file, "a") as f:
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
        if self.markdown_file:
            try:
                with open(self.markdown_file, "r") as f:
                    html = markdown(f.read())
                pdf_file = os.path.join(self.working_directory, "installation_steps.pdf")
                from_string(html, pdf_file)
                print(f"PDF saved to {pdf_file}")
            except Exception as e:
                print(f"Error converting to PDF: {e}")

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

def convert_to_pdf():
    recorder.convert_to_pdf()

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

root.mainloop()