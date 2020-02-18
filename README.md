# prproj_downgrade
Simple script for downgrading Adobe Premiere Pro project files to version 1. Tested on Macs only at this time.
Downgraded files should be able to open with any version of Premiere. There are a few of these tools out there already, but I wanted to try writing my own.

The script should install any non-standard python modules automatically using 'pip' if they are not detected when you run it for the first time. Written for Python 3.5+.

by Alex Fichera.

# Usage
`prproj_downgrade.py downgrade <path-to-file>`  

or:

`prproj_downgrade.py info <path-to-file>`

or, to watch a directory for new project files:

`prproj_downgrade.py watch <path-to-watch-directory> <path-to-output-directory>`

If you want to change the suffix of the downgraded project file name:

`prproj_downgrade.py downgrade <path-to-file> --suffix=YOUR_SUFFIX_HERE`