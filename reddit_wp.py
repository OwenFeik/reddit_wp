import os
import requests
import random
import json
import time
import re
if os.name == 'nt':
    import ctypes

class Image():
    def __init__(self, post_json):
        try:
            self.url = post_json['url']
            self.width = post_json['preview']['images'][0]['source']['width']
            self.height = post_json['preview']['images'][0]['source']['height']
            self.id = post_json['id']
        except:
            raise ValueError

class ImageNotFoundError(Exception):
    pass

class SubredditAccessError(Exception):
    pass

def download_image(image, download_folder = 'images'):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    try:
        ext = get_file_extension(image.url)
    except:
        raise ImageNotFoundError(f'Image has no file extension.')

    path = f'{download_folder}/{image.id}{ext}'
    if os.path.exists(path):
        return path

    resp = requests.get(image.url)
    if not resp.status_code == 200:
        raise ImageNotFoundError(f'Couldn\'t retrieve {image.url}')

    data = resp.content
    with open(path, 'wb') as f:
        f.write(data)

    return path

def get_images(subreddit = 'earthporn'):
    resp = requests.get(f'https://reddit.com/r/{subreddit}.json', 
        headers = {'user-agent': 'bot'})
    if not resp.status_code == 200:
        raise SubredditAccessError(f'Couldn\'t reach /r/{subreddit}')

    data = [i['data'] for i in resp.json()['data']['children']]
    images = []
    for post in data:
        if post.get('post_hint') == 'image':
            try:
                images.append(Image(post))
            except ValueError:
                pass
    
    return images

def set_wallpaper(file):
    if os.name == 'nt':
        # https://stackoverflow.com/a/38053141
        if 'PROGRAMFILES(X86)' in os.environ: # 64-bit Windows
            sys_paramaters_info = ctypes.windll.user32.SystemParametersInfoW
        else: # 32-bit Windows
            sys_paramaters_info = ctypes.windll.user32.SystemParametersInfoA 

        # SPI_SETDESKTOPWALLPAPER = 20
        resp = sys_paramaters_info(20, 0, os.path.abspath(file), 3)
        if not resp:
            raise ctypes.WinError('Failed to set wallpaper.')
    else:
        os.system('feh something or other')

def get_config(config_file = 'config.json'):
    try:
        config = json.load(open(config_file, 'r'))
    except FileNotFoundError:
        config = {
            'subreddit': 'earthporn',
            'resolution': 'system',
            'download_folder': 'images'
        }
        json.dump(config, open(config_file, 'w'), indent = 4)

    if config['resolution'] == 'system':
        config['resolution'] = get_resolution()

    return config

def get_resolution():
    if os.name == 'nt':
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
    else:
        os.system('xrandr something or other')

    return {'width': width, 'height': height}

def filter_images(resolution, images):
    passed = []
    for i in images:
        if i.width >= resolution['width'] and \
        i.height >= resolution['height']:
            passed.append(i)
    return passed

def log_message(message):
    with open('.log', 'a') as f:
        timestring = time.strftime('%d/%m %T')
        f.write(f'<{timestring}> {message}\n')

def get_file_extension(url):
    ext = re.search(r'.[a-zA-Z]+$', url)
    if ext:
        return ext.group(0)
    else:
        raise ValueError('No file extension in supplied url.')

def main():
    try:
        log_message('App started.')
        config = get_config()
        log_message('Loaded config.')
        images = get_images(config['subreddit'])
        log_message(f"Downloaded post list from /r/{config['subreddit']}.")
        images = filter_images(config['resolution'], images)
        image = random.choice(images)
        try:
            path = download_image(image, config['download_folder'])
        except Exception as e:
            log_message(f'Failed to download {image.url} ({e}). Trying another image.')
            images.remove(image)
            image = random.choice(images)
            path = download_image(image, config['download_folder'])
        log_message(f'Downloaded image ({image.url}).')
        set_wallpaper(path)
        log_message(f'Set wallpaper to {path}.')
    except Exception as e:
        log_message(f'Ran into a problem: {e}')

if __name__ == '__main__':
    main()
