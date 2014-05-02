# Copy epub from iBooks to Kindle

Usage: python copy2kindle.py [-p plist_file] [-n book_name]
* use -p to define non default iBooks property list file location
* use -n to define partial book name

If neither command line option is present the script will simple
list book names 10 at the time.

Calibre application must be installed to the computer, since the script
uses Calibre's command line tools for ebook conversion.

If Kindle is connected to computer the script will copy the converted ebook 
automatically. Otherwise the converted book is left to the temporary directory
(default: /tmp). 