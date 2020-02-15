# !/usr/bin/env python3.8
"""
Downgrade Adobe Premiere Pro project files.

Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
Downgraded files should be able to open with any newer version of Premiere.
Version: 1.0
# by Alex Fichera.
Example Usage: prproj_downgrade.py downgrade <path-to-file>
or:            prproj_downgrade.py info <path-to-file>
"""

# --- Begin imports --- #
# Importing sys first to create install function
import sys
import subprocess
try:  # Trying to do the rest of the imports. We will need these all later.
    import shutil
    import time
    import gzip
    import re
    import fire
    import os
    import pyfiglet
    from colorama import init
    from termcolor import cprint
    from tqdm import tqdm
    from tqdm import trange
    from progress.spinner import PixelSpinner
    from pathlib import Path
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print('One or more non-standard modules not found. Attempting to install...')
    packages = ['fire', 'tqdm', 'colorama', 'termcolor', 'pyfiglet', 'progress', 'watchdog']  # Non-native required packages.
    for p in packages:
        if sys.platform == 'darwin':
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', p])
            except Exception as e:
                print('Encountered exception: ' + str(e))
                print('Error installing modules. Quiting.')
        elif sys.platform == 'win32' or sys.platform == 'cygwin':  # Check for windows machine. May be be unnecessary.
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', p])
            except Exception as e:
                print('Encountered exception: ' + str(e) + '\nError installing modules. Quiting.')
        else:
            print('Error installing modules. Quiting.')
            exit()
    print('\n...\nSuccess!\nExiting program. Should now work if you run it again.')
# --- End of imports --- #
# --- Begin class definitions --- #


class MyEventHandler(FileSystemEventHandler):
    # Define event handler for watchdog module.
    # This will be called when user wants to watch a given directory for changes.
    def __init__(self, watch_dir, output_dir):
        self.watch_dir = watch_dir
        self.output_dir = output_dir

        if os.path.exists(self.output_dir) is False:
            os.mkdir(self.output_dir)
        elif os.path.exists(self.watch_dir) is False:
            print('Watch directory not found. Check your path.')
            exit()

    def on_modified(self, event):
        files = [(self.watch_dir + f) for f in os.listdir(self.watch_dir) if (os.path.isfile(os.path.join(self.watch_dir, f)))
                 if (os.path.join(self.watch_dir, f).endswith('.prproj'))]
        if len(files) > 0:
            latest_file = max(files, key=os.path.getmtime)
            print('latest file is: ' + latest_file)
            if latest_file:
                print(latest_file)
                downgrade(latest_file, output_dir=self.output_dir)
                os.rename(latest_file, latest_file + '.processed')
                latest_file = None
        else:
            return
# --- End class definitions --- #


def handle_exceptions(exception):  # Receives an exception type and does error handling.
    if exception[0] == FileNotFoundError:
        print('Invalid file path. Check your path and file name.')
    elif exception[0] == BufferError:
        print('Buffer error... how on earth did you do this?')
    else:
        print('An unknown error occured.')
        print("Full exception: \n" + str(exception) +
              '\nTraceback Line: ' + str(exception[-1].tb_lineno))


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
        print('Compressing file. Almost Done...')
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
        pbar = tqdm(tmp.readlines(), unit_scale=True, unit='Lines') # Initiallize project bar to the readLines iterator
        pbar.set_description('Reading project File...')
        for line in pbar:  # Use tqdm to initialize a progress bar as we write the file line by line.
            if is_project_objectID(line) is True:
                print('Changing project version to "1"')
                lines.append(parse_line(line))  # Once we get to the line that starts with project objectID, we replace.
            else:
                lines.append(line)
        try:
            tmp.seek(0), tmp.truncate(0)
            # tmp.writelines(lines)  # without progress bar, write all lines with this.
            with tqdm(lines, unit_scale=True, unit='Lines') as write_pbar:
                write_pbar.set_description('Writing new project File...')
                for line in write_pbar:
                    tmp.write(''.join(line))
        except:
            exception = sys.exc_info()
            handle_exceptions(exception)


def downgrade(prproj_in, output_dir=''):  # Main functionality of the program. Downgrades target prproj files.
    """
    Downgrade Adobe Premiere Pro project files.

    Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
    Downgraded files should be able to open with any newer version of Premiere.
    Author: Alex Fichera
    Version: 0.8
    :param prproj_in: path to Premiere Pro project file
    :param output_dir: optional, destination output directory
    """
    new_version = '1'
    root, ext = os.path.splitext(prproj_in)  # Checking if file extension is correct.
    src_file_name = os.path.basename(root)
    new_name = ((root if output_dir == '' else output_dir) + src_file_name +
                '_DOWNGRADED' + '(v.' + str(new_version) + ').prproj')
    print('new_name is: {new_name}'.format(new_name=new_name))
    temp_name = os.path.split(root)[0] + '/prproj_downgrade.tmp'

    try:
        if output_dir == '':
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
            print('Cleaning up temp file {temp_name}...'.format(temp_name=temp_name))
            os.remove(temp_name)
            print('Success! Project file downgraded at: ' + new_name)
    except:
        exception = sys.exc_info()
        handle_exceptions(exception)


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
                    version = re.search(r'Adobe\sPremiere\sPro\sCC\s\d\d\d\d', line)
                elif build_line_search in line:
                    build_version = re.search(r'\d\d[\.]\d[.]\d', line)
            if version and build_version:
                print('Project Created in: ' + version.group() + '\n' + 'Build Version: ' + build_version.group())
            else:
                print('Project info not found.')
    except:
        exception = sys.exc_info()
        handle_exceptions(exception)


def watch(watch_dir, output_dir):
    """
    :param watch_dir: Directory to watch for new Premiere Pro project files.
    :param output_dir: Directory to place downgraded Premiere Pro project files.
    :return:
    """
    event_handler = MyEventHandler(watch_dir, output_dir)  # instantiate event handler class from begining of file
    observer = Observer()
    observer.schedule(event_handler, path=watch_dir, recursive=False)  # set the observer parameters
    observer.start()  # start watching the directory
    try:
        with PixelSpinner('...Watching target directory...') as bar:
            while True:
                time.sleep(0.06)
                bar.next()
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == '__main__':
    fire.Fire({
        'project_info': info,
        'downgrade': downgrade,
        'watch': watch
    })