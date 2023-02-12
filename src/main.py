"""
The desktop main class.

Created by Jaydon Walters
"""

import downloader
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

logging.basicConfig(level=logging.DEBUG)


class DesktopApp(tk.Tk):
    """
    A Tk object for the GUI.

    TODO: Implement a startup check to see if Instagram is responding
    TODO: Implement multithreading when downloading posts
    TODO: Allow download from carousels
    TODO: Improve GUI layout
    TODO: Change theme
    TODO: Add "Paste from clipboard" button
    TODO: Add button icons
    """

    def __init__(self):
        super().__init__()
        # Set properties
        self.resizable(False, False)
        self.title("InstaSaver: Instagram Post Downloader")

        # URL input widgets
        self.url_frame = None               # Frame to group widgets together
        self.url_input = None               # Entry field to type the URL
        self.url_sv = None                  # StringVar to hold contents of URL entry field
        self.clear_url_button = None        # Button to clear URL entry field
        self.get_post_button = None         # Button to fetch post at URL

        # Preview post widgets
        self.preview_frame = None           # Frame to group widgets together

        # Download options widgets
        self.options_frame = None           # Frame to group widgets together
        self.dir_input = None               # Entry field to type the directory
        self.directory_sv = None            # StringVar to hold contents of directory entry field
        self.browse_button = None           # Button to browse directory
        self.audio_only_checkbox = None     # Checkbox to download audio only from video posts
        self.audio_only_iv = None           # IntVar to hold contents of "audio only" checkbox
        self.audio_types = ["wav", "mp3"]   # List of supported audio formats
        self.audio_type_selection = None    # Dropdown list containing the supported audio formats
        self.selected_audio_type_sv = None  # StringVar to hold the currently selected audio format

        # Download post widgets
        self.download_frame = None          # Frame to group widgets together
        self.ready_label = None             # Label to notify when post is ready to be downloaded
        self.download_button = None         # Button to download post

        # Create GUI
        self.create_gui()

    def create_gui(self) -> None:
        """
        Creates GUI elements and lays them out on-screen.
        """
        # Title label
        ttk.Label(self, text="InstaSaver").grid(column=0, row=0)

        # URL input widgets - Creation
        self.url_frame = tk.Frame(self, padx=20, pady=5)
        self.url_sv = tk.StringVar()
        self.url_sv.trace_add("write", self.make_get_button_available)
        self.url_input = ttk.Entry(self.url_frame, width=50, textvariable=self.url_sv)
        self.clear_url_button = ttk.Button(self.url_frame, text="Clear",
                                           command=lambda: self.clear_input_contents(self.url_sv))
        self.get_post_button = ttk.Button(self.url_frame, text="Get post", command=self.get_post, state="disabled")

        # URL input widgets - Layout
        self.url_frame.grid(row=1, column=0)
        ttk.Label(self.url_frame, text="URL:").grid(row=0, column=0)
        self.url_input.grid(row=0, column=1, padx=5)
        self.clear_url_button.grid(row=0, column=2)
        self.get_post_button.grid(row=1, column=0, columnspan=3)

        # Download options widgets - Creation
        self.options_frame = tk.Frame(self, padx=20, pady=5)
        self.directory_sv = tk.StringVar()
        self.directory_sv.trace_add("write", self.make_get_button_available)
        self.dir_input = ttk.Entry(self.options_frame, width=50, textvariable=self.directory_sv)
        self.browse_button = ttk.Button(self.options_frame, text="Browse", command=self.browse_directory)
        self.audio_only_iv = tk.IntVar()
        self.audio_only_checkbox = ttk.Checkbutton(self.options_frame, text="Download audio only",
                                                   variable=self.audio_only_iv, command=self.toggle_audio_type_selector)
        self.selected_audio_type_sv = tk.StringVar()
        self.audio_type_selection = ttk.OptionMenu(self.options_frame, self.selected_audio_type_sv, self.audio_types[0],
                                                   *self.audio_types)

        # Download options widgets - Layout
        self.options_frame.grid(row=2, column=0)
        ttk.Label(self.options_frame, text="Download options:").grid(row=0, column=0, columnspan=3)
        ttk.Label(self.options_frame, text="Directory:").grid(column=0, row=1)
        self.dir_input.grid(column=1, row=1)
        self.browse_button.grid(column=2, row=1)
        self.audio_only_checkbox.grid(column=0, row=2, columnspan=2)
        self.audio_type_selection.grid(column=2, row=2)

        # Download post widgets - Creation
        self.download_frame = tk.Frame(self, padx=20, pady=5)
        self.download_button = ttk.Button(self.download_frame, text="DOWNLOAD", command=self.download, state="disabled")

        # Download post widgets - Layout
        self.download_frame.grid(row=3, column=0)
        self.download_button.grid(column=0, row=6, columnspan=3)

        # Hide widgets
        self.options_frame.grid_remove()
        self.download_frame.grid_remove()

    def browse_directory(self) -> str:
        """
        Prompt user to choose directory for file download
        :return: The selected file path
        """
        filepath = filedialog.askdirectory()
        self.dir_input.insert(0, filepath)
        return filepath

    def get_post(self) -> None:
        """
        Prepare the post for download

        TODO: Add low-res image preview
        """
        # Display download options based on the file type
        if downloader.get_media_type(self.url_sv.get()) == "mp4":
            # Show "audio only" checkbox
            self.audio_only_checkbox.config(state="normal")
            self.audio_only_checkbox.grid()
            # Show audio selector dropdown
            self.audio_type_selection.grid()
        else:
            # Hide "audio only" checkbox
            self.audio_only_checkbox.grid_remove()
            self.audio_only_checkbox.config(state="disabled")
            # Hide audio selector dropdown
            self.audio_type_selection.grid_remove()

        # Display "ready to download" message
        self.ready_label.grid()
        # Enable download button
        self.download_button.config(state="normal")

    def toggle_audio_type_selector(self) -> None:
        """
        Toggle the dropdown list for the audio type
        """
        if self.audio_only_iv.get() == 1:
            # Enable type selector
            self.audio_type_selection.config(state="normal")
        else:
            # Disable type selector
            self.audio_type_selection.config(state="disabled")

    def download(self) -> None:
        """
        Fetch the URL and directory from input fields and attempt to download the Instagram post
        """
        # Get URL
        url = self.url_input.get()
        # Get file path
        filepath = self.dir_input.get()

        try:
            # Check for audio only
            logging.debug("Check for audio only...\n\t%s\n\t%s", self.audio_only_checkbox["state"],
                          self.audio_only_iv.get())
            if self.audio_only_checkbox["state"] == "normal" and self.audio_only_iv.get() == 1:
                logging.debug("Downloading audio (%s) only...", self.selected_audio_type_sv.get())
                # Download audio only
                downloader.download_instagram_post(url, filepath, self.selected_audio_type_sv.get())
            else:
                logging.debug("Downloading video/audio...")
                downloader.download_instagram_post(url, filepath)
            tk.messagebox.showinfo("Success!", "File successfully downloaded.")
            # Reset screen
            self.clear_input_contents()
        except FileExistsError:
            tk.messagebox.showerror("Download error!", "There seems to be an error with the download.")

    def clear_input_contents(self, widget: tk.StringVar = None) -> None:
        """
        Clears the contents of the provided widget. If none, the function clears all Entry widgets
        :param widget: The widget to clear
        :return: None
        """
        if widget is None:
            self.url_sv.set("")
            self.directory_sv.set("")
            # Remove ready message
            self.ready_label.grid_remove()
            # Focus on URL entry
            self.url_input.focus_set()
        else:
            widget.set("")

    def make_get_button_available(self, *args) -> None:
        if self.url_sv.get() != "" and self.directory_sv.get() != "":
            # Enable get post button
            self.get_post_button.config(state="normal")
        else:
            # Disable buttons
            self.get_post_button.config(state="disabled")
            self.download_button.config(state="disabled")
            # Hide other options
            self.audio_only_checkbox.grid_remove()
            self.audio_type_selection.grid_remove()

    # TODO: Add notice on startup
    # def issue_notice(self, show: bool = True) -> None:
    #     warning_message = "This application is still under development. This means that there are bugs and errors " \
    #                       "that could occur. In the event of a bug/error, try restarting the application. If that " \
    #                       "doesn't work then feel free to contact me."


if __name__ == '__main__':
    # Run GUI
    DesktopApp().mainloop()
