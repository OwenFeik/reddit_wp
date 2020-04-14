import requests
import os
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
            self.score = post_json['score']
        except:
            raise ValueError('Unable to extract necessary information from post.')

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

def get_images(url):
    resp = requests.get(url, headers = {'user-agent': 'bot'})
    if not resp.status_code == 200:
        raise SubredditAccessError(f'Couldn\'t reach {url}')

    data = [i['data'] for i in resp.json()['data']['children']]
    images = []
    for post in data:
        if post.get('post_hint') == 'image':
            try:
                images.append(Image(post))
            except ValueError:
                pass
    
    return images

def get_url(subreddit_string):
    view = re.search(r'(?<=/)(day|week|month|year|all)(?=:|$)', subreddit_string)
    quantity = re.search(r'(?<=:)\d+$', subreddit_string)
    
    queries = {}
    if view:
        view = view.group(0)
        subreddit_string = subreddit_string.replace(f'/{view}', '/top')
        queries['t'] = view
    if quantity:
        quantity = quantity.group(0)
        subreddit_string = subreddit_string.replace(f':{quantity}', '')
        queries['limit'] = str(min(int(quantity), 100))

    if queries:
        query_string = '?'
        for q in queries:
            query_string += f'{q}={queries[q]}&'
        query_string = query_string[:-1] # Cut off trailing ampersand
        return f'https://reddit.com/r/{subreddit_string}.json{query_string}'
    else:
        return f'https://reddit.com/r/{subreddit_string}.json'

def set_wallpaper(file):
    if os.name == 'nt':
        # https://stackoverflow.com/a/38053141
        # Way to check if windows is 64 or 32-bit
        if 'PROGRAMFILES(X86)' in os.environ: # 64-bit Windows
            sys_paramaters_info = ctypes.windll.user32.SystemParametersInfoW
        else: # 32-bit Windows
            sys_paramaters_info = ctypes.windll.user32.SystemParametersInfoA 

        # SPI_SETDESKTOPWALLPAPER = 20
        resp = sys_paramaters_info(20, 0, os.path.abspath(file), 3)
        if not resp:
            raise ctypes.WinError('Failed to set wallpaper.')
    elif os.name == 'posix':
        os.system(f'feh --bg-fill {os.path.abspath(file)}')

def get_config(config_file = 'config.json'):
    try:
        config = json.load(open(config_file, 'r'))
    except FileNotFoundError:
        config = {
            'subreddits': ['earthporn/all'],
            'resolution': 'system',
            'download_folder': 'images',
            'selection': 'random',
            'backup_image': ''
        }
        json.dump(config, open(config_file, 'w'), indent = 4)

    if config['resolution'] == 'system':
        config['resolution'] = get_resolution()

    if os.name == 'posix':
        config['download_folder'] = os.path.expanduser(config['download_folder'])
        config['backup_image'] = os.path.expanduser(config['backup_image'])

    return config

def get_resolution():
    if os.name == 'nt':
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
    elif os.name == 'posix':
        # https://stackoverflow.com/a/3598320
        # Using xrandr, grab resolution of each monitor
        resp = os.popen('xrandr | grep "\\*" | cut -d" " -f4').read()
        # Use largest monitor for minumum w/h
        width = height = 0
        for m in resp.split('\n'):
            if m == '':
                continue
            w, h = m.split('x')
            w = int(w)
            h = int(h)
            if w > width:
                width = w
            if h > height:
                height = h

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

def choose_image(images, rule):
    if rule == 'random':
        return random.choice(images)
    elif rule == 'top':
        return max(images, key = lambda i: i.score)
    elif rule == 'score':
        scores = [i.score for i in images]
        return random.choices(images, weights = scores, k = 1)[0]
    elif rule == 'rough':
        scores = [i.score ** 0.5 for i in images]
        return random.choices(images, weights = scores, k = 1)[0]
        
def main():
    try:
        scriptpath = os.path.abspath(__file__)
        os.chdir(os.path.dirname(scriptpath))
        log_message('App started.')

        config = get_config()
        log_message('Loaded config.')
        
        images = []
        for subreddit in config['subreddits']:
            try:
                images.extend(get_images(get_url(subreddit)))
            except Exception as e:
                log_message(f'Failed to retrieve post list from /r/{subreddit}: ({e})')
        images = filter_images(config['resolution'], images)
        
        if not images:
            log_message(f'No images retrieved, defaulting to backup.')
            if config['backup_image']:
                path = config['backup_image']
                if os.name == 'nt':
                    if not (len(path) >= 2 and re.match(r'[A-Z]:', path[:2])):
                        path = f"{config['download_folder']}/{path}"
                elif os.name == 'posix':
                    if path[0] != '/':
                        path = f"{config['download_folder']}/{path}"
            else:
                log_message(f'No backup image set. Exiting.')
                raise SystemExit
        else:
            image = choose_image(images, config['selection'])
            try:
                path = download_image(image, config['download_folder'])
            except Exception as e:
                log_message(f'Failed to download {image.url} ({e}). Trying another image.')
                images.remove(image)
                image = choose_image(images, config['selection'])
                path = download_image(image, config['download_folder'])
            log_message(f'Downloaded image ({image.url}).')
        
        set_wallpaper(path)
        log_message(f'Set wallpaper to {os.path.abspath(path)}.')
    except Exception as e:
        log_message(f'Ran into a problem: {e}')

if __name__ == '__main__':
    main()
