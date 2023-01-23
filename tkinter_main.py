"""
The desktop main class.

This class creates the GUI using Tkinter.
"""

from downloader import *
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

logging.basicConfig(level=logging.DEBUG)


class DesktopApp(tk.Tk):
    """
    A Tk object for the GUI.
    """

    def __init__(self):
        super().__init__()
        # Set properties
        self.resizable(False, False)
        self.title("Instagram Post Downloader")

        # Main frame to hold other widgets
        self.main_frame = None

        # Input fields
        self.url_input = None
        self.url = None
        self.dir_input = None
        self.directory = None

        # Audio only option for videos
        self.audio_only = None
        self.audio_only_checkbox = None

        # Audio type
        self.audio_types = ["wav", "mp3"]
        self.selected_audio_type = None
        self.audio_type_selection = None

        # Buttons
        self.browse_button = None
        self.download_button = None
        self.clear_url_button = None
        self.get_post_button = None

        # Create GUI
        self.create_gui()

    def create_gui(self) -> None:
        """
        Creates GUI elements and packs them on-screen.
        """
        # Create main frame for holding all widgets
        self.main_frame = tk.Frame(self, width=800, height=600, padx=20, pady=20)
        self.main_frame.pack()

        # Create widgets to do with the URL
        self.url = tk.StringVar()  # Stores the text of the URL input field
        self.url.trace_add("write", self.make_get_button_available)
        self.url_input = ttk.Entry(self.main_frame, width=50, textvariable=self.url)  # URL input
        self.clear_url_button = ttk.Button(self.main_frame, text="Clear",
                                           command=lambda: self.clear_input_contents(self.url))  # Clear URL button

        # Create widgets to do with the directory
        self.directory = tk.StringVar()  # Stores the text of the directory input field
        self.directory.trace_add("write", self.make_get_button_available)
        self.dir_input = ttk.Entry(self.main_frame, width=50, textvariable=self.directory)  # Directory input
        self.browse_button = ttk.Button(self.main_frame, text="Browse",
                                        command=self.browse_directory)  # Browse directory button

        # Create get post button
        self.get_post_button = ttk.Button(self.main_frame, text="Get post", command=self.get_post, state="disabled")

        # Create "audio only" checkbox
        self.audio_only = tk.IntVar()  # Stores the value of the checkbox
        self.audio_only_checkbox = ttk.Checkbutton(self.main_frame, text="Download audio only",
                                                   variable=self.audio_only, command=self.toggle_audio_type_selector)

        # Create audio type selector
        self.selected_audio_type = tk.StringVar()
        self.audio_type_selection = ttk.OptionMenu(self.main_frame, self.selected_audio_type, self.audio_types[0],
                                                   *self.audio_types)

        # Create download button
        self.download_button = ttk.Button(self.main_frame, text="DOWNLOAD", command=self.download, state="disabled")

        # Layout widgets
        # Pack title label
        ttk.Label(self.main_frame, text="Post Downloader").grid(column=0, row=0, columnspan=3)  # Title label

        # Pack URL widgets
        ttk.Label(self.main_frame, text="URL:").grid(column=0, row=1)  # URL label
        self.url_input.grid(column=1, row=1, padx=5)  # URL input
        self.clear_url_button.grid(column=2, row=1)  # Clear URL button

        # Pack directory widgets
        ttk.Label(self.main_frame, text="Directory:").grid(column=0, row=2)  # Directory label
        self.dir_input.grid(column=1, row=2)  # Directory input
        self.browse_button.grid(column=2, row=2)  # Pick directory button

        # Pack widgets related to downloading
        self.get_post_button.grid(column=0, row=3, columnspan=3)  # Get post button
        self.audio_only_checkbox.grid(column=0, row=4, columnspan=2)  # Audio only checkbox
        self.audio_type_selection.grid(column=2, row=4)  # Audio type dropdown menu
        self.download_button.grid(column=0, row=5, columnspan=3)  # Download button

        # Hide widgets
        self.audio_only_checkbox.grid_remove()
        self.audio_only_checkbox.config(state="disabled")
        self.audio_type_selection.grid_remove()
        self.audio_type_selection.config(state="disabled")

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
        """
        # Get URL
        url = self.url.get()

        # Display download options based on the file type
        if get_media_type(url) == "mp4":
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

        # Enable download button
        self.download_button.config(state="normal")

    def toggle_audio_type_selector(self) -> None:
        """
        Toggle the dropdown list for the audio type
        """
        if self.audio_only.get() == 1:
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
                          self.audio_only.get())
            if self.audio_only_checkbox["state"] == "normal" and self.audio_only.get() == 1:
                logging.debug("Downloading audio (%s) only...", self.selected_audio_type.get())
                # Download audio only
                download_instagram_post(url, filepath, self.selected_audio_type.get())
            else:
                logging.debug("Downloading video/audio...")
                download_instagram_post(url, filepath)
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
            self.url.set("")
            self.directory.set("")
        else:
            widget.set("")

    def make_get_button_available(self, *args) -> None:
        if self.url.get() != "" and self.directory.get() != "":
            # Enable get post button
            self.get_post_button.config(state="normal")
        else:
            # Disable buttons
            self.get_post_button.config(state="disabled")
            self.download_button.config(state="disabled")
            # Hide other options
            self.audio_only_checkbox.grid_remove()
            self.audio_type_selection.grid_remove()

    def issue_notice(self, show: bool = True) -> None:
        warning_message = "This application is still under development. This means that there are bugs and errors " \
                          "that could occur. In the event of a bug/error, try restarting the application. If that " \
                          "doesn't work then feel free to contact me."


if __name__ == '__main__':
    # Run GUI
    DesktopApp().mainloop()
