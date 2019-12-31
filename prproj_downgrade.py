import gzip
import bs4
import subprocess
import sys
from bs4 import BeautifulSoup
import fire
import os


def install(package):
    if sys.platform == 'darwin':
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    # if sys.platform == 'win32' or sys.platform == 'cygwin':   # Check for windows machine. May be be unnecessary.
    else:
        print('Error.')
        exit(1)


def get_project_version(prproj_in):
    with gzip.open(prproj_in, 'rt') as f:
        file_content = f.read()  # put file contents into variable as string text
        soup = BeautifulSoup(file_content, 'xml')  # create soup object
        print('Current project version: ' +
              soup.Project.find_next()['Version'])


def handle_exceptions(exception):
    if exception == FileNotFoundError:
        print('Invalid file path. Check your path and file name.')
    elif exception == ModuleNotFoundError:
        print('Missing python module(s)! Trying to automatically install...\n')
        try:
            install('BeautifulSoup4')
            install('fire')
            install('lxml')
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


def downgrade(prproj_in, version='1'):
    """
    Downgrade Adobe Premiere Pro project files.

    Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
    Downgraded files should be able to open with any newer version of Premiere.
    Author: Alex Fichera
    Version: 0.3
    :param prproj_in: path to Premiere Pro project file
    :param new_version: Optional. Specify what version to downgrade to. Defaults to version '1'.
    """
    new_version = version
    root, ext = os.path.splitext(prproj_in)
    try:
        if ext != '.prproj':
            print('Invalid filetype. Must have valid .prproj extension.')
            exit(-1)
        else:

            with gzip.open(prproj_in, 'rt') as f:
                file_content = f.read()  # put file contents into variable as string text
                soup = BeautifulSoup(file_content, 'xml')  # create soup object
                print('Current project version: ' +
                      soup.Project.find_next()['Version'])
                soup.Project.find_next()['Version'] = new_version  # Change project version number to 1
                print('Downgraded project version to: ' +
                      str(soup.Project.find_next()['Version']))  # Print current version 1
                if os.path.exists(prproj_in + '_DOWNGRADED.prproj'):
                    print('Output file already exists at this location. Please move or rename.')
                    exit(-1)
                else:
                    with gzip.open(prproj_in + '_DOWNGRADED.prproj', 'wt') as f_out:
                        f_out.write(soup.prettify())
                        print('Downgrade Complete. New file: ' + prproj_in + '_DOWNGRADED.prproj')
    except:
        exception = sys.exc_info()
        handle_exceptions(exception[0])


if __name__ == '__main__':
    fire.Fire()

