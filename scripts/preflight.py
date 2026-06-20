#!/usr/bin/env python3
import shutil

items = ['pdftotext', 'ebook-convert', 'python', 'python3']

print('Tool checks')
for item in items:
    if shutil.which(item):
        print(item + ': OK')
    else:
        print(item + ': MISSING')
