"""
This code is used to download Instagram posts.

It makes use of the instagramy library for the downloading, but contains additional functions for ease of use.
"""

import logging
import os
import time

from instagramy.plugins.download import download_post
from instagramy import InstagramPost
from pathlib import Path
from moviepy.editor import VideoFileClip

# Constants
# SESSION_ID = os.environ.get("PASTE_YOUR_SESSION_ID_HERE")
DOWNLOADS_FOLDER = str(Path.home() / "Downloads")


def convert_video_to_audio(video_path, output_ext="mp3", delete_video: bool = False):
    """
    Convert video file to audio.
    :param video_path: The file path to the video
    :param output_ext: The audio extension
    :param delete_video: Whether to delete the original file
    """
    # Remove the extension of the video
    logging.debug("Extracting audio from file...")
    filename, extension = os.path.splitext(video_path)
    # Create audio file
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(f"{filename}.{output_ext}")

    # Wait before deleting file
    time.sleep(1)

    # Delete video
    # if os.path.exists(filename) and delete_video:
    #     logging.debug("Deleting video file...")
    #     os.remove(video_path)


def get_post_code(url: str) -> str:
    """
    Fetch the post code from the URL
    :param url: The URL of the post
    :return: The code identifying the Instagram post
    """
    # Split URL
    url_list = url.split("/")
    url_list.remove("")

    # Check if the link is a valid Instagram link
    if url_list[1] != "www.instagram.com":
        raise Exception("Link is not an Instagram link")

    # Check for type of post
    if url_list[2] == "p" or url_list[2] == "reel":
        logging.debug("URL is valid. Fetching ID...")
    else:
        raise Exception("Invalid Instagram link")

    return url_list[3]


def get_post_object(url: str) -> InstagramPost:
    """
    Creates a post object
    :param url: The URL of the post
    :return: An object containing the post attributes
    """
    return InstagramPost(get_post_code(url))


def get_media_type(url: str) -> str:
    """
    Identifies the file format of the post.
    :param url: The URL of the post
    :return: The file format of the post
    """
    # Create post object
    post = get_post_object(url)

    # Get extension
    if post.type_of_post == "GraphImage":
        return "png"
    elif post.type_of_post == "GraphVideo":
        return "mp4"
    else:
        raise TypeError(f"Unsupported file type: {post.type_of_post}")


def download_instagram_post(url: str, filepath: str = DOWNLOADS_FOLDER, extension: str = None) -> bool:
    """
    Downloads an Instagram post
    :param url: The URL of the post
    :param filepath: The location to download the file to
    :param extension: The file extension of the post. If left blank, the extension is automatically determined
    :return: True if file has downloaded successfully, False otherwise
    """
    post = get_post_object(url)
    if extension is None:
        file_name = f"{post.author}_{post.post_id}.{get_media_type(url)}"
    elif extension == "wav" or extension == "mp3":
        # Keep file as mp4 and convert after downloading
        file_name = f"{post.author}_{post.post_id}.mp4"
    else:
        file_name = f"{post.author}_{post.post_id}.{extension}"

    # Download file
    if filepath == "":
        filepath = DOWNLOADS_FOLDER
    logging.debug("Downloading %s to path %s...", file_name, filepath)
    download_post(post.post_id, filepath=f"{(Path(filepath) / file_name)}")

    # Check if file is audio
    if extension == "wav" or extension == "mp3":
        convert_video_to_audio(str(Path(filepath) / file_name), output_ext=extension, delete_video=True)

    # Check for file
    if os.path.exists(str(Path(filepath) / file_name)):
        logging.debug("File downloaded successfully!")
    else:
        logging.debug("An unexpected error occurred.")
        raise FileExistsError("An unexpected error occurred")
