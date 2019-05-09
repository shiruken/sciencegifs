import os
import json
import glob
import re
import requests
import time
import subprocess

# Refresh Imgur access token
tokens = json.load(open('tokens.json'))
url = 'https://api.imgur.com/oauth2/token'
payload = {'refresh_token': tokens['refresh_token'],
           'client_id': tokens['client_id'],
           'client_secret': tokens['client_secret'],
           'grant_type': 'refresh_token'}
response = requests.post(url, data=payload)
access_token = response.json()['access_token']

temp_path = os.path.join(os.getcwd(), 'temp.gif')
posts = sorted(glob.glob('_posts/*md'))
for i, post in enumerate(posts):

    # Read in the post text
    with open(post, "r") as f:
        content = f.read()
        
    # Extract the path to the image file    
    content = content.splitlines()
    img_embed_line = content[-1]
    img_url = re.findall(r'\((.*?)\)', img_embed_line)[-1]

    # Skip to the next file already an Imgur URL
    if 'i.imgur.com' in img_url:
        continue
    
    # If the filesize is larger than 10 MB, try to use gifsicle to reduce 
    # the filesize for uploading to Imgur
    img_path_full = os.path.join(os.getcwd(), img_url[1:])
    filesize = os.path.getsize(img_path_full)
    if filesize >= 1024*1024*10:

        print(f'{img_url} is {filesize/1024/1024:0.1f} MB, attempting to optimize the GIF')

        # Count the number of frames and duration of each frame
        cmd = ['gifsicle', img_path_full, '-I']
        out = subprocess.check_output(cmd)
        n_frames = int(re.findall(rb'(\d+) images', out)[0])
        frame_duration = re.findall(rb'delay (\d+\.\d+)', out)
        if frame_duration: # Hundredths of a second
            frame_duration = int(float(frame_duration[0]) * 100)
        else:
            frame_duration = 10

        # Try reducing the filesize using gifsicle
        # Initially only attempt to reduce the image dimensions and the lossiness
        # If that's unsuccessful, try removing frames
        resize_width = 500
        lossy = 20
        delay = frame_duration
        frame_list = []
        frame_step = 1
        while filesize >= 1024*1024*10:

            if not frame_list:
                print(f'Optimizing with width={resize_width} and lossy={lossy}')
            else:
                print(f'Optimizing using every {frame_step} frames, width={resize_width}, and lossy={lossy}')

            cmd = ['gifsicle', img_path_full, '-O3', f'-d{delay}']
            cmd += frame_list
            cmd += ['--resize-width', f'{resize_width}', f'--lossy={lossy}', '-o', temp_path]
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            filesize = os.path.getsize(temp_path)

            if resize_width > 400:
                resize_width -= 25

            if lossy < 50:
                lossy += 5
            else:
                resize_width = 500
                lossy = 20
                frame_step += 1
                frame_list = [f'#{x}' for x in range(0, n_frames + 1, 2)]
                delay = frame_duration*frame_step

                if frame_step > 5:
                    break

        if filesize >= 1024*1024*10:
            print(f'Only reduced filesize to {filesize / 1024 / 1024:0.1f} MB. Skipping')
            continue
        else:
            print(f'Reduced filesize to {filesize / 1024 / 1024:0.1f} MB')
            img_path_full = temp_path

    # Upload the file to Imgur
    with open(img_path_full, 'rb') as fp:
        image = fp.read()
    url = 'https://api.imgur.com/3/image'
    data = {'image': image}
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        imgur_url = response.json()['data']['link']

        # Update the post text with the new Imgur URL and save
        content[-1] = img_embed_line.replace(img_url, imgur_url) + '\n'
        content = '\n'.join(content)
        with open(post, 'w') as fp:
            fp.write(content)
        print(f'Updated {img_url} to {imgur_url}')
    else:
        print(f'Failed to upload {img_path_full} to Imgur: {response.status_code}')

# Remove the temp file
if os.path.isfile(temp_path):
    os.remove(temp_path)
