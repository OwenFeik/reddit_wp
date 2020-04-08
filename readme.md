# Reddit Wallpaper

This script selects an image from a subreddit (or subreddits) of your choosing, downloads it, and sets it as your wallpaper. Currently only windows is supported, though linux support will be added in the (near) future.


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
* ```subreddits``` contains a list of subreddits to pull images from.
* ```resolution``` defines the minimum image resolution; by default, when set to ```"system"```, this will be determined automatically based on screen resolution. Otherwise, a dictionary must be provided, of the form
```json
{
    "width": 1920,
    "height": 1080
}
```
* ```download_folder``` is the folder downloaded images are saved to. By default, this is a folder called "images" in the installation folder.
* ```selection``` determines how the image is chosen; by default, the front page of each subreddit is joined and a random image is chosen from this. Two other modes can also be used: ```"top"``` will use the image with the highest score and ```"score"``` will select randomly weighted by score.
* ```backup_image``` is the image used if no image of sufficient resolution is found.  
