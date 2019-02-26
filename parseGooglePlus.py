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
    'https://plus.google.com/+ColinSullender/posts/5JvZUbugAZs'
]

posts = glob.glob(data_dir + 'Posts/*.json')
for post in posts:

    with open(post) as fp:
        data = json.load(fp)

    if 'collectionAcl' in data['postAcl']:
        if data['postAcl']['collectionAcl']['collection']['displayName'] == 'Science GIFs':
            if all (k in data for k in ('content', 'media')):
                           
                content = data['content'].split('<br>')
                title = re.findall('<b>(.*?)</b>', content[0])

                if len(content) > 0 and len(title) > 0 and data['url'] not in excluded:
                    title = re.sub('<[^<]+?>', '', parser.unescape(title[0]).strip()).rstrip('.').lstrip('+')
                    date = datetime.strptime(data['creationTime'], '%Y-%m-%d %H:%M:%S%z').strftime('%Y-%m-%d')
                    pattern = re.compile(r'([^\s\w]|_)+')
                    filename = date + '-' + '-'.join(pattern.sub('', title).split(' '))

                    # Copy the gif to the appropriate location
                    media = data_dir + data['media']['localFilePath'].split('../')[1]
                    img_save_path = save_dir + 'assets/img/' + filename + '.gif'
                    copyfile(media, img_save_path)

                    # Format the markdown text
                    output = '---\n'
                    output += 'layout: post\n'
                    output += 'title:  "' + title + '"\n'
                    output += '---\n\n'
                    output += h.handle('<br>'.join(content[2:]))
                    output += '[View Original Post on Google+](' + data['url'] + ')\n\n'
                    output += '![' + title + '](' + '/assets/img/' + filename + '.gif)\n'

                    # Write the markdown file to the appropriate location
                    post_save_path = save_dir + '_posts/' + filename + '.md'
                    with open(post_save_path, 'w') as fp:
                        fp.write(output)

                    print(title)