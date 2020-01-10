# !/usr/bin/env python3.8
"""
Downgrade Adobe Premiere Pro project files.

Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
Downgraded files should be able to open with any newer version of Premiere.
Version: 0.4
# by Alex Fichera.
Example Usage: prproj_downgrade.py downgrade <path-to-file>
"""

# --- Begin imports --- #
# Importing sys first to create install function
import sys
import subprocess


def install(package):  # Install required modules if not present.
    if sys.platform == 'darwin':
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except Exception as e:
            print('Encountered exception: ' + str(e))
            print('Error installing modules. Quiting.')
    # if sys.platform == 'win32' or sys.platform == 'cygwin':   # Check for windows machine. May be be unnecessary.
    else:
        print('Error installing modules. Quiting.')


try:  # Trying to do the rest of the imports. We will need these all later.
    import gzip
    import bs4
    from bs4 import BeautifulSoup
    import fire
    import os
    import progress
    from tqdm import tqdm
    from pathlib import Path
except ImportError:
    print('Non-standard modules not found. Attempting to install...')
    packages = ['BeautifulSoup4', 'fire', 'lxml', 'tqdm']  # Non-native required packages.
    for p in packages:
        install(p)  # calling install function we created earlier...
    print('\n...\nSuccess!\nExiting program. Should now work if you run it again.')
# --- End of imports --- #


def handle_exceptions(exception):  # Receives an exception type and does error handling.
    if exception == FileNotFoundError:
        print('Invalid file path. Check your path and file name.')
    elif exception == ModuleNotFoundError:
        print('Missing python module(s)! Trying to automatically install...\n')
        try:
            for package in packages:
                install(package)
        except:
            print('Failed. Check python environment for missing modules.\n')
    elif exception == bs4.FeatureNotFound:
        print('Trying to install lxml parser...')
        try:
            install('lxml')
        except:
            print('Failed to install lxml parser.Quiting...\n')
    elif exception == BufferError:
        print('Buffer error... how on earth did you do this?')
    else:
        print('An unknown error occured.')


def project_info(prproj_in):  # Fetches the project version from the target .prproj file.
    try:
        root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')
            # If not a valid Adobe Premiere file, exit.
        with gzip.open(prproj_in, 'rt') as f:
            file_content = f.read()  # put file contents into variable as string text
            soup = BeautifulSoup(file_content, 'xml')  # create soup object
            pp_app_path_list = Path(soup.PresetPath.string).parts
            pp_app = ''.join(s for s in pp_app_path_list if 'Adobe Premiere Pro' in s and '.' not in s)
            print('Premiere Pro version: ' + pp_app)
            print('Current project file version: ' +
                  soup.Project.find_next()['Version'])
    except:
        exception = sys.exc_info()
        handle_exceptions(exception[0])


def downgrade(prproj_in):  # Main functionality of the program. Downgrades target prproj files.
    """
    Downgrade Adobe Premiere Pro project files.

    Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
    Downgraded files should be able to open with any newer version of Premiere.
    Author: Alex Fichera
    Version: 0.4
    :param prproj_in: path to Premiere Pro project file
    """
    new_version = '1'
    root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
    new_name = (root + '_DOWNGRADED' + '(v.' + str(new_version) + ').prproj')

    try:
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')
            # If not a valid Adobe Premiere file, exit.
        elif os.path.exists(new_name):
            print('Output file already exists at this location. Please move or rename.')
        else:  # Otherwise... continue on to unzip and parse the xml file with BeautifulSoup.
            with tqdm(total=100) as pbar:  # Initialize progress bar.
                with gzip.open(prproj_in, 'rt') as f:  # Decompress project file and open...
                    file_content = f.read()  # Put file contents into variable as string text
                    soup = BeautifulSoup(file_content, 'xml')  # create soup object
                    print('Current project version: ' +
                          soup.Project.find_next()['Version'])  # Printing current project version.
                    soup.Project.find_next()['Version'] = new_version  # Change project version number to 1
                    print('Downgraded project version to: ' +
                          str(soup.Project.find_next()['Version']))  # Print new current version.
                    pbar.update(80)
                    with gzip.open(new_name, 'wt') as f_out:
                        f_out.write(str(soup))  # Turn soup object to string for final writing to gzip file.
                        pbar.update(100)
                        print('Downgrade Complete. New file: ' + new_name)  # Change file extension.
    except:
        exception = sys.exc_info()
        handle_exceptions(exception[0])


if __name__ == '__main__':
    fire.Fire({
        'project_info': project_info,
        'downgrade': downgrade,
        'help': help,
    })
