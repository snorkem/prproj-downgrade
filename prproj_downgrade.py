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
    #if sys.platform == 'win32' or sys.platform == 'cygwin':
    else:
        print('Error.')
        exit(1)


def main(prproj_in, downgrade_to='1'):
    """
    Downgrade Adobe Premiere Pro project files.

    Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.\n
    Downgraded files should be able to open with any newer version of Premiere.
    Author: Alex Fichera
    Version: 0.3
    :param prproj_in: path to Premiere Pro project file
    :param downgrade_to: Optional. Specify what version to downgrade to. Defaults to version '1'.
    """
    root, ext = os.path.splitext(prproj_in)
    if ext != '.prproj':
        print('Invalid filetype. Must have valid .prproj extension.')
        exit(-1)
    try:
        with gzip.open(prproj_in, 'rt') as f:
            file_content = f.read()  # put file contents into variable as string text
            soup = BeautifulSoup(file_content, 'xml')  # create soup object
            print('Current project version: ' +
                  soup.Project.find_next()['Version'])
            soup.Project.find_next()['Version'] = downgrade_to  # Change project version number to 1
            print('Downgraded project version to: ' +
                  soup.Project.find_next()['Version'])  # Print current version 1
            if os.path.exists(prproj_in + '_DOWNGRADED.prproj'):
                print('Output file already exists at this location. Please move or rename.')
                exit(-1)
            else:
                with gzip.open(prproj_in + '_DOWNGRADED.prproj', 'wt') as f_out:
                    f_out.write(soup.prettify())
                    print('Downgrade Complete. New file: ' + prproj_in + '_DOWNGRADED.prproj')
    except FileNotFoundError:
        print('Invalid file path. Check your path and file name.')
    except ModuleNotFoundError as e:
        print('Missing python module(s)! Trying to automatically install...\n')
        try:
            install('BeautifulSoup4')
            install('fire')
            install('lxml')
        except:
            print('Failed. Check python environment for missing modules.\n')
    except bs4.FeatureNotFound:
        print('Trying to install lxml parser...')
        try:
            install('lxml')
        except:
            print('Failed...\n')


if __name__ == '__main__':
    fire.Fire(main)

