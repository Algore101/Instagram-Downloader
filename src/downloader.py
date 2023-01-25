"""
This library is an extension of instagramy, used to download public Instagram content

Created by Jaydon Walters
"""

import os
from instagramy.plugins.download import download_post
from instagramy import InstagramPost
from pathlib import Path
from moviepy.editor import VideoFileClip

# Constants
DOWNLOADS_FOLDER = str(Path.home() / "Downloads")


def convert_video_to_audio(video_path, output_ext="mp3", delete_video: bool = False):
    """
    Convert video file to audio.
    :param video_path: The file path to the video
    :param output_ext: The audio extension
    :param delete_video: Whether to delete the original file
    """
    # Remove the extension of the video
    filename, _ = os.path.splitext(video_path)
    # Create audio file
    with VideoFileClip(video_path) as clip:
        clip.audio.write_audiofile(f"{filename}.{output_ext}")

    # Delete video
    if os.path.exists(video_path) and delete_video:
        os.remove(video_path)


def get_post_code(url: str) -> str:
    """
    Fetch the post code from the URL
    :param url: The post URL
    :return: The code identifying the Instagram post
    """
    # Split URL
    url_list = url.split("/")
    url_list.remove("")

    # Check if the link is a valid Instagram link
    if url_list[1] != "www.instagram.com":
        raise Exception("Link is not an Instagram link")

    # Check for type of post
    if url_list[2] != "p" and url_list[2] != "reel":
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


def download_instagram_post(url: str, filepath: str = DOWNLOADS_FOLDER, extension: str = None) -> None:
    """
    Downloads an Instagram post
    :param url: The URL of the post
    :param filepath: The location to download the file to
    :param extension: The file extension of the post. If left blank, the extension is automatically determined
    :return: `True` if file has downloaded successfully, `False` otherwise
    """
    post = get_post_object(url)
    if extension is None:
        # Automatically determine extension
        file_name = f"{post.author}_{post.post_id}.{get_media_type(url)}"
    elif extension == "wav" or extension == "mp3":
        # Keep file as mp4 and convert after downloading
        file_name = f"{post.author}_{post.post_id}.mp4"
    else:
        file_name = f"{post.author}_{post.post_id}.{extension}"

    # Download file
    if filepath == "":
        filepath = DOWNLOADS_FOLDER
    download_post(post.post_id, filepath=f"{(Path(filepath) / file_name)}")

    # Check if file is audio
    if extension == "wav" or extension == "mp3":
        convert_video_to_audio(str(Path(filepath) / file_name), output_ext=extension, delete_video=True)
        # Change extension back to selected extension
        file_name = f"{post.author}_{post.post_id}.{extension}"

    # Check for file
    if not os.path.exists(str(Path(filepath) / file_name)):
        raise FileExistsError("An unexpected error occurred")
