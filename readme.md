# Reddit Wallpaper

This script selects an image from a subreddit (or subreddits) of your choosing, downloads it, and sets it as your wallpaper. It should work on windows, and on linux setups where ```feh``` is available to set wallpaper and ```xrandr``` is available to check screen resolution. Python ```requests``` is the only other dependency.


A configuration file will be created when the script is first run, looking like so:

```json
{
    "subreddits": [
        "earthporn"
    ],
    "resolution": "system",
    "download_folder": "images",
    "selection": "random",
    "backup_image": ""
}
```

To customise the script, you can edit these fields:
* ```subreddits``` contains a list of subreddits to pull images from. These can just be a subreddit name, in which case images will be pulled from hot, or they can be of the form ```"subname/<view>"``` where ```<view>``` is one of:
    - ```new```
    - ```rising```
    - ```controversial```
    - ```day```
    - ```week```
    - ```month```
    - ```year```
    - ```all```
* ```resolution``` defines the minimum image resolution; by default, when set to ```"system"```, this will be determined automatically based on screen resolution. Otherwise, a dictionary must be provided, of the form
```json
{
    "width": 1920,
    "height": 1080
}
```
* ```download_folder``` is the folder downloaded images are saved to. By default, this is a folder called "images" in the installation folder.
* ```selection``` determines how the image is chosen; by default, the front page of each subreddit is joined and a random image is chosen from this. Two other modes can also be used: ```"top"``` will use the image with the highest score and ```"score"``` will select randomly weighted by score.
* ```backup_image``` is the image used if no image of sufficient resolution is found. It can either be an absolute path (```"C:\path\to\image```, ```"~/path/to/image"```, etc) or a path relative to the download folder (```"image"```, ```"../image"```, etc).

If you plan on using the script with a polybar setup, the following module may be of use:

```
[module/wallpaper]
type = custom/script
exec = echo "⏬"
click-left = "python ~/path/to/reddit_wp.py &"
```

If you plan on using the script on windows, the included file ```reddit_wp.vbs``` may be useful. It should run the script for you, and can be easily run at startup through the following method:
* press ```Super + R``` to open the Run dialog.
* enter ```shell:startup``` and press OK.
* create a shortcut to ```reddit_wp.vbs``` in the startup folder.
