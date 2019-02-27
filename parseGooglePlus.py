import json
import glob
import re
from datetime import datetime
from shutil import copyfile
import html2text
import os
import html.parser as htmlparser

parser = htmlparser.HTMLParser()
h = html2text.HTML2Text()
h.body_width = 0

data_dir = 'Takeout JSON/Google+ Stream/'
save_dir = 'githubio/'

excluded = [
    'https://plus.google.com/+ColinSullender/posts/56oheSVB6Ed',
    'https://plus.google.com/+ColinSullender/posts/2RhVjpdDt4a',
    'https://plus.google.com/+ColinSullender/posts/KHrRMDdCN4b',
    'https://plus.google.com/+ColinSullender/posts/9LDJT3vJxMM',
    'https://plus.google.com/+ColinSullender/posts/Wwtx3CAdfQ3',
    'https://plus.google.com/+ColinSullender/posts/R3irMmt2Got',
    'https://plus.google.com/+ColinSullender/posts/d7dztSFycUc',
    'https://plus.google.com/+ColinSullender/posts/cxzj36XofTR',
    'https://plus.google.com/+ColinSullender/posts/9zftLgAQUku',
    'https://plus.google.com/+ColinSullender/posts/hXGHasPstTv',
    'https://plus.google.com/+ColinSullender/posts/5JvZUbugAZs',
    'https://plus.google.com/+ColinSullender/posts/HRxAXBw43Bj',
    'https://plus.google.com/+ColinSullender/posts/K5GHgnBPMGg'
]

# Create the output directory for the posts
markdown_dir = os.path.join(save_dir, '_posts/')
if not os.path.exists(markdown_dir):
    os.makedirs(markdown_dir)

# Create the output directory for the images
img_dir = os.path.join(save_dir, 'assets/img/')
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

# Iterate through the post JSON
posts = glob.glob(data_dir + 'Posts/*.json')
for post in posts:

    with open(post) as fp:
        data = json.load(fp)

    # Check that the post is in a collection, has linked media, and is not in the excluded list
    if 'collectionAcl' in data['postAcl'] and 'media' in data and data['url'] not in excluded:

        # Check that the post is in the 'Science GIFs' collection
        if data['postAcl']['collectionAcl']['collection']['displayName'] == 'Science GIFs':
                           
            content = data['content'].split('<br>')

            # Extract the title from the first line and strip the HTML tags
            title = re.sub('<[^<]+?>', '', parser.unescape(content[0])).strip()

            # Strip plus signs (e.g. +SpaceX) and any trailing periods
            title = re.sub(r'\+\b', '', title).rstrip('.')

            # Extract the timestamp and format as YYYY-MM-DD
            creationTime = datetime.strptime(data['creationTime'], '%Y-%m-%d %H:%M:%S%z')
            date = creationTime.strftime('%Y-%m-%d')

            # Assemble the filename for Jekyll (YEAR-MONTH-DAY-title.md)
            pattern = re.compile(r'([^\s\w]|_)+')
            filename = date + '-' + '-'.join(pattern.sub('', title).split())

            # Format the markdown text
            output = '---\n'
            output += 'layout: post\n'
            output += 'title:  "' + title + '"\n'
            output += '---\n\n'
            output += h.handle('<br>'.join(content[2:]))
            output += '[View Original Post on Google+](' + data['url'] + ')\n\n'
            output += '![' + title + '](' + '/assets/img/' + filename + '.gif)\n'

            # Write the markdown file to the appropriate location
            post_save_path = os.path.join(markdown_dir, filename + '.md')
            with open(post_save_path, 'w') as fp:
                fp.write(output)

            # Copy the gif to the appropriate location
            media = data_dir + data['media']['localFilePath'].split('../')[1]
            img_save_path = os.path.join(img_dir, filename + '.gif')
            copyfile(media, img_save_path)

            print('{} - {}'.format(date, title))