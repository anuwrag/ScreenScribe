import os
import shutil
import zipfile

def create_release_package():
    # Version number
    version = "1.0.0"  # Update this for each release
    
    # Create release directory
    release_dir = f"ScreenScribe-v{version}"
    os.makedirs(release_dir, exist_ok=True)
    
    # Copy executable and dependencies
    shutil.copy("dist/ScreenScribe.exe", release_dir)
    
    # Copy additional files
    files_to_copy = [
        "README.md",
        "requirements.txt",
        "LICENSE"  # if you have one
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, release_dir)
    
    # Create installation instructions
    with open(f"{release_dir}/INSTALL.txt", "w") as f:
        f.write("""ScreenScribe Installation Instructions:

1. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to: C:\\Program Files\\Tesseract-OCR

2. Install wkhtmltopdf:
   - Download from: https://wkhtmltopdf.org/downloads.html
   - Install to: C:\\Program Files\\wkhtmltopdf

3. Add to System PATH:
   - C:\\Program Files\\Tesseract-OCR
   - C:\\Program Files\\wkhtmltopdf\\bin

4. Run ScreenScribe.exe
""")
    
    # Create ZIP file
    zip_filename = f"ScreenScribe-v{version}-windows.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, os.path.join(release_dir, arcname))
    
    print(f"Release package created: {zip_filename}")

if __name__ == "__main__":
    create_release_package()