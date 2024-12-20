# How to use:

### Windows Instructions:

1. Install Conda Envirement: `conda create --name ScreenScribe python=3.12`
2. Activate Conda Envirement: `conda activate ScreenScribe`
3. Install requirements.txt: `pip install -r requirements.txt`
4. Install wkhtmltopdf on Windows: `https://wkhtmltopdf.org/downloads.html`
5. Install Tesseract OCR on Windows: `https://github.com/UB-Mannheim/tesseract/wiki`
6. Add Tesseract OCR to PATH: `set PATH=%PATH%;"C:\Program Files\Tesseract-OCR"`    
7. Add wkhtmltopdf to PATH: `set PATH=%PATH%;"C:\Program Files\wkhtmltopdf\bin"`
8. Run the script: `python main.py`

# Screenshot:
![Screenshot](screenshot.png)

# Example Output PDF:
![Instructions to Download from Microsoft Store](installation_steps.pdf)

## Known Issues:
1. If using second monitor, the apps on the second monitor will not be captured and shows a blank screen.
2. The keystrokes are not recorded correctly. 
3. The text around the clicked region is not captured correctly. 

## Future Improvements:
1. Add support for other operating systems. 
