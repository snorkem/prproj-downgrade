# !/usr/bin/env python3.8
"""
Downgrade Adobe Premiere Pro project files.

Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
Downgraded files should be able to open with any newer version of Premiere.
Version: 0.4
# by Alex Fichera.
Example Usage: prproj_downgrade.py downgrade <path-to-file>
or:            prproj_downgrade.py info <path-to-file>
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
        exit()


try:  # Trying to do the rest of the imports. We will need these all later.
    import gzip
    import re
    import fire
    import os
    import shutil
    import progress
    import pyfiglet
    from colorama import init
    from termcolor import cprint
    from tqdm import tqdm
    from tqdm import trange
    from pathlib import Path
except ImportError:
    print('Non-standard modules not found. Attempting to install...')
    packages = ['fire', 'tqdm', 'colorama', 'termcolor', 'pyfiglet']  # Non-native required packages.
    for p in packages:
        install(p)  # calling install function we created earlier...
    print('\n...\nSuccess!\nExiting program. Should now work if you run it again.')
# --- End of imports --- #


def handle_exceptions(exception):
    print("Full exception: \n" + str(exception)) # Receives an exception type and does error handling.
    if exception == FileNotFoundError:
        print('Invalid file path. Check your path and file name.')
    elif exception == ModuleNotFoundError:
        print('Missing python module(s)! Trying to automatically install...\n')
        try:
            for package in packages:
                install(package)
        except:
            print('Failed. Check python environment for missing modules.\n')
    elif exception == BufferError:
        print('Buffer error... how on earth did you do this?')
    else:
        print('An unknown error occured.')


def welcome():
    welcome = pyfiglet.Figlet(font='doom', justify='c', width=300)
    cprint(welcome.renderText("Prproj   Downgrade\n"), "magenta")
    cprint('by Alex Fichera', 'magenta')


def is_project_objectID(line):
    line_search_str = '<Project ObjectID='
    if line_search_str in line:
        return True
    else:
        return False


def info(prproj_in):  # Fetches the project version from the target .prproj file.
    try:
        root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')  # If not a valid Adobe Premiere file, exit.
            exit()
        with gzip.open(prproj_in, 'rt') as f:
            search_string = '<PresetPath>/Applications/'
            build_line_search = '<MZ.BuildVersion.Created>'
            lines = f.readlines()
            for line in lines:
                if search_string in line:
                    version = re.search(r'Adobe\sPremiere\sPro\s\d\d\d\d', line)
                elif build_line_search in line:
                    build_version = re.search(r'\d\d[\.]\d[.]\d', line)
            print('Project Created in: ' + version.group() + '\n' + 'Build Version: ' + build_version.group())
    except:
        exception = sys.exc_info()
        handle_exceptions(exception)


def unzip_file(f_in, f_out):
    # uses gzip to unzip a file by coping the binary data to a new file
    with gzip.open(f_in, 'rb') as f:
        print('Unzipping project file...')
        contents = f.read().decode('utf-8').rstrip()
        with open(f_out, 'w+b') as o:
            shutil.copyfileobj(f, o)
    return contents


def zip_file(f_in, new_name):
    # uses gzip to zip contents of one file into a new file.
    with open(f_in, 'rb') as f:
        f.seek(0)
        print('Compressing file. Almost Done!')
        with gzip.open(new_name, 'wb', compresslevel=6) as o:
            shutil.copyfileobj(f, o)


def parse_line(line):
    # Try to modify a given line passed as a string --- this should change the project version to '1'
    line_search_str = '<Project ObjectID='
    if line_search_str in line:
        r = re.compile(r'Version=\W\d\d\W\W')
        new_version_line = str(re.sub(r, 'Version="1">', line))
        return new_version_line
    else:
        print('Error! Tried to modify incorrect line.')


def modify_xml(tmp_file_out, xml_contents):
    lines = []  # create list and read in file line by line.
    with open(tmp_file_out, 'r+') as tmp:
        tmp.write(xml_contents), tmp.seek(0)
        pbar = tqdm(tmp.readlines()) # Initiallize project bar to the readLines iterator
        pbar.set_description('Reading Project File...'), print('Changing project version to "1"')
        for line in pbar:  # Use tqdm to initialize a progress bar as we write the file line by line.
            if is_project_objectID(line) is True:
                lines.append(parse_line(line))  # Once we get to the line that starts with project objectID, we replace.
            else:
                lines.append(line)
        try:
            tmp.seek(0), tmp.truncate(0)
            with trange(len(lines)) as pbar:
                for progress in pbar:  # update progress bar
                    pbar.set_description('Writing out file...')
                    tmp.write(''.join(lines[progress]))
        except:
            exception = sys.exc_info()
            handle_exceptions(exception)


def downgrade(prproj_in):  # Main functionality of the program. Downgrades target prproj files.
    """
    Downgrade Adobe Premiere Pro project files.

    Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
    Downgraded files should be able to open with any newer version of Premiere.
    Author: Alex Fichera
    Version: 0.8
    :param prproj_in: path to Premiere Pro project file
    """
    new_version = '1'
    root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
    new_name = (root + '_DOWNGRADED' + '(v.' + str(new_version) + ').prproj')
    temp_name = os.path.split(root)[0] + '/prproj_downgrade.tmp'
    try:
        welcome()
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')
            # If not a valid Adobe Premiere file, exit.
        elif os.path.exists(new_name):
            print('Output file already exists at this location. Please move or rename.')
        else:  # Otherwise... continue on to unzip and parse the xml file with BeautifulSoup.

            xml_contents = unzip_file(prproj_in, temp_name)
            modify_xml(temp_name, xml_contents)
            zip_file(temp_name, new_name)
            print('Cleaning up temp file "%s"...' % temp_name)
            os.remove(temp_name)
            print('Success! Project file downgraded at: ' + new_name)
    except:
        exception = sys.exc_info()
        handle_exceptions(exception)


if __name__ == '__main__':
    fire.Fire({
        'project_info': info,
        'downgrade': downgrade,
    })
