import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'name-%s%' % 'name_of_your_executable file',
    '--onefile',
    '--windowed',
    os.path.join('/path/to/your/script/', 'your script.py'), """your script and path to the script"""
])