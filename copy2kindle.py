import plistlib
import sys
from os.path import expanduser
import argparse
import os
import zipfile
import shutil
import subprocess

calibreCommand = "/Applications/calibre.app/Contents/console.app/Contents/MacOS/ebook-convert"
tempDir = "/tmp/"
kindlePath = "/Volumes/Kindle/documents/"

def zip_dir(path, zipFile):
	with zipfile.ZipFile(zipFile, 'w', zipfile.ZIP_DEFLATED) as bookzip:
 	   for root, dirs, files in os.walk(path):
    	   	for file in files:
        	   	bookzip.write(os.path.join(root, file))

def change_plist_format(plist, targetFormat):
	devnull = open(os.devnull, 'wb')
	plistReformat = [ "plutil", "-convert", targetFormat, plist ]
	ret = subprocess.call(plistReformat, stdout = devnull, stderr = subprocess.STDOUT)

	if ret != 0:
		print "Something went wrong while reformatting %s to %s format" % (plist, targetFormat)
		sys.exit(2)

def copy_to_kindle(bookName):
	mobiName = bookName.replace(".epub", ".mobi")
	if not os.path.exists(kindlePath):
		print "Kindle does not seem to be connected; the converted book is available in %s" % (tempDir + mobiName)
		return

	print "Copying converted ebook to Kindle"
	shutil.copyfile(tempDir + mobiName, kindlePath + mobiName)

def convert_book(bookName):
	print "Converting to mobi format"
	mobiName = bookName.replace(".epub", ".mobi")
	devnull = open(os.devnull, 'wb')
	ret = subprocess.call([calibreCommand, tempDir + bookName, tempDir + mobiName], stdout=devnull, stderr=subprocess.STDOUT)
	if ret != 0:
		print "Something went wrong with conversion"

def process_book(book):
	bookName = book['BKDisplayName']
	if os.path.isdir(book['path']):
		print "Rezipping epub"
		zip_dir(book['path'], tempDir + bookName)
	else:
		shutil.copyfile(book['path'], tempDir + bookName)

	convert_book(bookName)
	copy_to_kindle(bookName)

def print_op():
	print "book number to copy it to Kindle, (n) next page, (q) to quit"

def handle_input(books):
	while True:
		ch = sys.stdin.readline().rstrip('\n').lower()
		if ch == "q":
			return False
		elif ch.isdigit():
			print "Processing book %s" % (books[int(ch) - 1]['BKDisplayName'])
			process_book(books[int(ch) - 1])
			print "Done"
		else:
			return True

def iter_books(plist, filter = None):
	change_plist_format(plist, "xml1")
	books=plistlib.readPlist(plist)['Books']
	filter = filter.lower() if filter else None

	for i, book in enumerate(books):
		if not ".epub" in book['BKDisplayName'].lower():
			continue
		if filter:
			if not filter in book['BKDisplayName'].lower():
				continue
		print "%i:  %s" % ((i + 1), book['BKDisplayName'])
		if (i  % 10) == 0 and i != 0:
			print_op()
			if not handle_input(books):
				break
			
	if (i % 10) != 0:
		print_op()
		handle_input(books)

	change_plist_format(plist, "binary1")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--plist-file', default=expanduser("~") + "/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/Books.plist",
			    help="iBooks property list file",
			    required=False)
	parser.add_argument('-n', '--book-name', default=None,
			    help="Partial book name; matched with Python \'in\' operand",
			    required=False)

	args = vars(parser.parse_args())

	iter_books(args['plist_file'], args["book_name"])
