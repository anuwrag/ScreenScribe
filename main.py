import os
import time
import keyboard
import pyautogui
from PIL import Image, ImageDraw
from pynput import mouse
from markdown2 import markdown
from pdfkit import from_string

class InstallationRecorder:
    def __init__(self):
        self.working_directory = None
        self.screenshots_dir = None
        self.markdown_file = None
        self.recording = False
        self.step_counter = 1
        self.mouse_listener = None

    def set_working_directory(self, directory):
        """Sets the working directory and creates necessary subdirectories."""
        self.working_directory = directory
        self.screenshots_dir = os.path.join(self.working_directory, "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.markdown_file = os.path.join(self.working_directory, "installation_steps.md")

    def start_recording(self):
        """Starts recording mouse clicks and screenshots."""
        self.recording = True
        self.step_counter = 1
        with open(self.markdown_file, "w") as f:
            f.write("# Software Installation Steps\n\n")
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def stop_recording(self):
        """Stops recording mouse clicks."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.recording = False

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

                # Write to markdown file
                with open(self.markdown_file, "a") as f:
                    f.write(f"## Step {self.step_counter}: {window_title}\n\n")
                    f.write(f"Clicked at position ({x}, {y}).\n\n")
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

    def convert_to_pdf(self):
        """Converts the markdown file to PDF."""
        if self.markdown_file:
            try:
                with open(self.markdown_file, "r") as f:
                    html = markdown(f.read())
                pdf_file = os.path.join(self.working_directory, "installation_steps.pdf")
                config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')  # Replace with your path
                from_string(html, pdf_file, configuration=config)
                print(f"PDF saved to {pdf_file}")
            except Exception as e:
                print(f"Error converting to PDF: {e}")

import tkinter as tk
from tkinter import filedialog

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        working_directory_label.config(text=directory)
        recorder.set_working_directory(directory)
        # Enable start button after directory is selected
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

working_directory_label = tk.Label(root, text="Select working directory:")
working_directory_label.pack()

browse_button = tk.Button(root, text="Browse", command=browse_directory)
browse_button.pack()

start_button = tk.Button(root, text="Start Recording", command=start_recording, state=tk.DISABLED)  # Initially disabled
start_button.pack()

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, state=tk.DISABLED)
stop_button.pack()

pdf_button = tk.Button(root, text="Convert to PDF", command=convert_to_pdf)
pdf_button.pack()

root.mainloop()