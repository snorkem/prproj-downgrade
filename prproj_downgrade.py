#!/usr/bin/env python3.8
import gzip
import bs4
import subprocess
import sys
from bs4 import BeautifulSoup
import fire
import os
from pathlib import Path
# End imports
packages = ['BeautifulSoup4', 'fire', 'lxml']  # Non-native required packages.


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
        exit(1)


def handle_exceptions(exception):  # Receives an exception and does error handling.
    if exception == FileNotFoundError:
        print('Invalid file path. Check your path and file name.')
    elif exception == ModuleNotFoundError:
        print('Missing python module(s)! Trying to automatically install...\n')
        try:
            for package in packages:
                install(package)
        except:
            print('Failed. Check python environment for missing modules.\n')
            exit(1)
    elif exception == bs4.FeatureNotFound:
        print('Trying to install lxml parser...')
        try:
            install('lxml')
        except:
            print('Failed to install lxml parser.Quiting...\n')
            exit(1)
    elif exception == BufferError:
        print('Buffer error... how on earth did you do this?')
        exit(1)


def project_info(prproj_in):  # Fetches the project version from the target .prproj file.
    try:
        root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')
            exit(-1)  # If not a valid Adobe Premiere file, exit.
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


def downgrade(prproj_in, version='1'):  # Main functionality of the program. Downgrades target prproj files.
    """
    Downgrade Adobe Premiere Pro project files.

    Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
    Downgraded files should be able to open with any newer version of Premiere.
    Author: Alex Fichera
    Version: 0.3
    :param prproj_in: path to Premiere Pro project file
    :param version: Optional. Specify what version to downgrade to. Defaults to version '1'.
    """
    new_version = version
    new_name = (prproj_in + '_DOWNGRADED' + '(v.' + str(new_version) + ').prproj')
    root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
    try:
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')
            exit(-1)  # If not a valid Adobe Premiere file, exit.
        else:  # Otherwise... continue on to unzip and parse the xml file with BeautifulSoup.
            with gzip.open(prproj_in, 'rt') as f:
                file_content = f.read()  # Put file contents into variable as string text
                soup = BeautifulSoup(file_content, 'xml')  # create soup object
                print('Current project version: ' +
                      soup.Project.find_next()['Version'])  # Printing current project version.
                soup.Project.find_next()['Version'] = new_version  # Change project version number to 1
                print('Downgraded project version to: ' +
                      str(soup.Project.find_next()['Version']))  # Print new current version.
                if os.path.exists(new_name):
                    print('Output file already exists at this location. Please move or rename.')
                    exit(-1)
                else:
                    with gzip.open(new_name, 'wt') as f_out:
                        f_out.write(soup.prettify())  # Turn soup object to string for final writing to gzip file.
                        print('Downgrade Complete. New file: ' + new_name)  # Change file extension.
    except:
        exception = sys.exc_info()
        handle_exceptions(exception[0])


if __name__ == '__main__':
    fire.Fire()