import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import threading
import yt_dlp
import subprocess
import sys
from pprint import pprint

class VideoDownloader:
    def __init__(self, url, format, save_location, include_subtitles, progress_callback):
        self.url = url
        self.format = format
        self.save_location = save_location
        self.include_subtitles = include_subtitles
        self.progress_callback = progress_callback

    def download_video(self):
        # Debug prints
        print(f"Debug - URL: {self.url}")
        print(f"Debug - Save location: {self.save_location}")

        # Input validation
        if not self.url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        if not self.save_location:
            messagebox.showerror("Error", "Please choose a save location.")
            return

        # Progress hook function
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)

                percentage = int((downloaded_bytes / total_bytes) * 100) if total_bytes else 0
                speed_kbps = speed / 1024 if speed else 0

                self.progress_callback(
                    f"Downloading: {percentage}% | Speed: {speed_kbps:.2f} KB/s | ETA: {eta} sec",
                    percentage
                )
            elif d['status'] == 'finished':
                self.progress_callback("Download completed!", 100)

        # Format selection logic
        if self.format == 'best':
            video_format = "bestvideo+bestaudio/best"
        else:
            res_value = self.format.split('p')[0]
            video_format = f"bestvideo[height<={res_value}]+bestaudio/best"

        # Download options
        ydl_opts = {
            'format': video_format,
            'outtmpl': os.path.join(self.save_location, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'merge_output_format': 'mp4',
        }

        # Add subtitle options if requested
        if self.include_subtitles:
            ydl_opts.update({
                'writesubtitles': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'vtt',
                'writeautomaticsub': True,
            })

        try:
            print("Video download options:", ydl_opts)  # Debug print
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                video_file = ydl.prepare_filename(info_dict)
                video_file = os.path.splitext(video_file)[0] + '.mp4'

                # Check if subtitles are available
                if self.include_subtitles and 'requested_subtitles' in info_dict:
                    vtt_subtitles_file = os.path.join(self.save_location, f"{os.path.splitext(video_file)[0]}.en.vtt")
                    srt_subtitles_file = os.path.join(self.save_location, f"{os.path.splitext(video_file)[0]}.en.srt")
                    if os.path.exists(vtt_subtitles_file):
                        self.convert_vtt_to_srt(vtt_subtitles_file, srt_subtitles_file)
                        self.merge_subtitles_with_video(video_file, srt_subtitles_file)

            messagebox.showinfo("Success", "Video downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def convert_vtt_to_srt(self, vtt_file, srt_file):
        command = ['ffmpeg', '-i', vtt_file, srt_file]
        try:
            self.progress_callback("Converting subtitles...", 0)
            print(f"Running command: {' '.join(command)}")  # Debug print
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command output: {result.stdout}")  # Debug print
            print(f"Command error: {result.stderr}")  # Debug print
            os.remove(vtt_file)  # Remove the original VTT file
            self.progress_callback("Subtitles converted successfully!", 100)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")  # Debug print
            messagebox.showerror("Error", f"An error occurred while converting subtitles: {str(e)}")
            self.progress_callback("Failed to convert subtitles.", 0)

    def merge_subtitles_with_video(self, video_file, subtitles_file):
        output_file = os.path.splitext(video_file)[0] + '_with_subtitles.mp4'
        command = [
            'ffmpeg', '-i', video_file, '-i', subtitles_file,
            '-c', 'copy', '-c:s', 'mov_text', output_file
        ]
        try:
            self.progress_callback("Merging subtitles with video...", 0)
            print(f"Running command: {' '.join(command)}")  # Debug print
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command output: {result.stdout}")  # Debug print
            print(f"Command error: {result.stderr}")  # Debug print
            os.remove(video_file)  # Remove the original video file
            os.rename(output_file, video_file)  # Rename the final file to the original name
            self.progress_callback("Subtitles merged successfully!", 100)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")  # Debug print
            messagebox.showerror("Error", f"An error occurred while merging subtitles: {str(e)}")
            self.progress_callback("Failed to merge subtitles.", 0)
class AudioDownloader:
    def __init__(self, url, format, save_location, include_subtitles, include_poster, progress_callback):
        self.url = url
        self.format = format
        self.save_location = save_location
        self.include_subtitles = include_subtitles
        self.include_poster = include_poster
        self.progress_callback = progress_callback

    def download_audio(self):
        # Debug prints
        print(f"Debug - URL: {self.url}")
        print(f"Debug - Save location: {self.save_location}")

        # Input validation
        if not self.url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        if not self.save_location:
            messagebox.showerror("Error", "Please choose a save location.")
            return

        # Progress hook function
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)

                percentage = int((downloaded_bytes / total_bytes) * 100) if total_bytes else 0
                speed_kbps = speed / 1024 if speed else 0

                self.progress_callback(
                    f"Downloading: {percentage}% | Speed: {speed_kbps:.2f} KB/s | ETA: {eta} sec",
                    percentage
                )

            elif d['status'] == 'finished':
                self.progress_callback("Download completed!", 100)

        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join(self.save_location, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.format,
                'preferredquality': '0',
            }],
            'writethumbnail': self.include_poster,
        }

        if self.include_subtitles:
            ydl_opts.update({
                'writesubtitles': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'vtt',
                'writeautomaticsub': True,
            })

        try:
            print("Audio download options:", ydl_opts)  # Debug print
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                audio_file = ydl.prepare_filename(info_dict)
                audio_file = os.path.splitext(audio_file)[0] + '.' + self.format

                if self.include_poster:
                    thumbnail_info = info_dict.get('thumbnails', [{}])[-1]
                    thumbnail_url = thumbnail_info.get('url')
                    if thumbnail_url:
                        thumbnail_file = os.path.join(self.save_location, 'thumbnail.webp')
                        jpeg_thumbnail_file = self.download_thumbnail(thumbnail_url, thumbnail_file)
                        if jpeg_thumbnail_file:
                            self.merge_poster_with_audio(audio_file, jpeg_thumbnail_file)

                # Check if subtitles are available
                if self.include_subtitles and 'requested_subtitles' in info_dict:
                    vtt_subtitles_file = os.path.join(self.save_location, f"{os.path.splitext(audio_file)[0]}.en.vtt")
                    srt_subtitles_file = os.path.join(self.save_location, f"{os.path.splitext(audio_file)[0]}.en.srt")
                    if os.path.exists(vtt_subtitles_file):
                        self.convert_vtt_to_srt(vtt_subtitles_file, srt_subtitles_file)
                        self.merge_subtitles_with_audio(audio_file, srt_subtitles_file)

            self.progress_callback("Download completed!", 100)
            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def convert_vtt_to_srt(self, vtt_file, srt_file):
        command = ['ffmpeg', '-i', vtt_file, srt_file]
        try:
            print(f"Running command: {' '.join(command)}")  # Debug print
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command output: {result.stdout}")  # Debug print
            print(f"Command error: {result.stderr}")  # Debug print
            os.remove(vtt_file)  # Remove the original VTT file
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")  # Debug print
            messagebox.showerror("Error", f"An error occurred while converting subtitles: {str(e)}")

    def merge_subtitles_with_audio(self, audio_file, subtitles_file):
        output_file = os.path.splitext(audio_file)[0] + '_with_subtitles.mp4'
        command = [
            'ffmpeg', '-i', audio_file, '-i', subtitles_file,
            '-c', 'copy', '-c:s', 'mov_text', output_file
        ]
        try:
            print(f"Running command: {' '.join(command)}")  # Debug print
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command output: {result.stdout}")  # Debug print
            print(f"Command error: {result.stderr}")  # Debug print
            os.remove(audio_file)  # Remove the original audio file
            os.rename(output_file, audio_file)  # Rename the final file to the original name
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")  # Debug print
            messagebox.showerror("Error", f"An error occurred while merging subtitles: {str(e)}")

    def download_thumbnail(self, url, path):
        try:
            with yt_dlp.YoutubeDL({'outtmpl': path}) as ydl:
                ydl.download([url])
            # Convert the downloaded thumbnail to JPEG
            jpeg_path = os.path.splitext(path)[0] + '.jpg'
            command = ['ffmpeg', '-i', path, jpeg_path]
            subprocess.run(command, check=True)
            os.remove(path)  # Remove the original webp file
            return jpeg_path
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while downloading the thumbnail: {str(e)}")
            return None

    def merge_poster_with_audio(self, audio_file, thumbnail_file):
        output_file = os.path.splitext(audio_file)[0] + '_final.' + self.format
        command = [
            'ffmpeg', '-i', audio_file, '-i', thumbnail_file,
            '-map', '0', '-map', '1', '-c', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Album cover"',
            '-metadata:s:v', 'comment="Cover (front)"', output_file
        ]
        try:
            print(f"Running command: {' '.join(command)}")  # Debug print
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command output: {result.stdout}")  # Debug print
            print(f"Command error: {result.stderr}")  # Debug print
            os.remove(audio_file)  # Remove the original audio file
            os.rename(output_file, audio_file)  # Rename the final file to the original name
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e.stderr}")  # Debug print
            messagebox.showerror("Error", f"An error occurred while merging poster: {str(e)}")
        finally:
            if os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)
class PlaylistDownloader:
    def __init__(self, url, format, save_location, include_subtitles, progress_callback):
        self.url = url
        self.format = format
        self.save_location = save_location
        self.include_subtitles = include_subtitles
        self.progress_callback = progress_callback

    def download_playlist(self):
        print(f"Debug - URL: {self.url}")
        print(f"Debug - Save location: {self.save_location}")

        # Input validation
        if not self.url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return
        if not self.save_location:
            messagebox.showerror("Error", "Please choose a save location.")
            return

        # Ensure the save location directory exists
        if not os.path.exists(self.save_location):
            os.makedirs(self.save_location)

        # Progress hook function
        def progress_hook(d):
            if d['status'] == 'downloading':
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes', 1)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)

                percentage = int((downloaded_bytes / total_bytes) * 100) if total_bytes else 0
                speed_kbps = speed / 1024 if speed else 0

                self.progress_callback(
                    f"Downloading: {percentage}% | Speed: {speed_kbps:.2f} KB/s | ETA: {eta} sec",
                    percentage
                )
            elif d['status'] == 'finished':
                self.progress_callback("Download completed!", 100)

        # Format selection logic
        if self.format == 'best':
            video_format = "bestvideo+bestaudio/best"
        else:
            res_value = self.format.split('p')[0]
            video_format = f"bestvideo[height<={res_value}]+bestaudio/best"

        # Download options
        ydl_opts = {
            'format': video_format,
            'outtmpl': os.path.join(self.save_location, '%(playlist_index)s - %(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'merge_output_format': 'mp4',
        }

        # Add subtitle options if requested
        if self.include_subtitles:
            ydl_opts.update({
                'writesubtitles': True,
                'subtitleslangs': ['en'],
                'subtitlesformat': 'vtt',
                'writeautomaticsub': True,
            })

        try:
            print("Playlist download options:", ydl_opts)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                for entry in info_dict.get('entries', []):  # Use get to avoid KeyErrors
                    pprint(entry)  # Debug entry structure
                    video_url = entry.get('original_url') or entry.get('webpage_url')
                    if not video_url:
                        print(f"Skipping video due to missing URL: {entry.get('title', 'Unknown Title')}")
                        continue

                    try:
                        print(f"Downloading video: {video_url}")
                        ydl.download([video_url])
                    except Exception as e:
                        print(f"Error downloading {video_url}: {str(e)}")
                        continue

            self.progress_callback("Download completed!", 100)
            messagebox.showinfo("Success", "Playlist downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
class AudioPlaylistDownloader:
    def __init__(self, url, audio_format, save_location, include_poster, progress_callback):
        self.url = url
        self.audio_format = audio_format
        self.save_location = save_location
        self.include_poster = include_poster
        self.progress_callback = progress_callback

    def download_playlist(self):
        if not self._validate_inputs():
            return

        ydl_opts = self._get_ydl_options()

        try:
            print("Debug - Starting playlist download with options:", ydl_opts)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                self._handle_playlist_entries(info_dict, ydl)
            self.progress_callback("Download completed!", 100)
            messagebox.showinfo("Success", "Playlist downloaded successfully!")
        except Exception as e:
            self._show_error(f"An error occurred during playlist download: {str(e)}")

    def _validate_inputs(self):
        if not self.url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return False
        if not self.save_location:
            messagebox.showerror("Error", "Please choose a save location.")
            return False
        return True

    def _get_ydl_options(self):
        return {
            'format': 'bestaudio',
            'outtmpl': os.path.join(self.save_location, '%(playlist_index)s - %(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format,
                'preferredquality': '0',
            }],
            'writethumbnail': self.include_poster,
        }

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes', 1)
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            percentage = int((downloaded_bytes / total_bytes) * 100) if total_bytes else 0
            speed_kbps = speed / 1024 if speed else 0

            self.progress_callback(
                f"Downloading: {percentage}% | Speed: {speed_kbps:.2f} KB/s | ETA: {eta} sec",
                percentage
            )
        elif d['status'] == 'finished':
            self.progress_callback("Download completed!", 100)

    def _handle_playlist_entries(self, info_dict, ydl):
        for entry in info_dict.get('entries', []):
            audio_file = ydl.prepare_filename(entry)
            audio_file = os.path.splitext(audio_file)[0] + '.' + self.audio_format

            if self.include_poster:
                thumbnail_url = self._get_thumbnail_url(entry)
                if thumbnail_url:
                    thumbnail_file = os.path.join(self.save_location, 'thumbnail.webp')
                    jpeg_thumbnail_file = self._download_thumbnail(thumbnail_url, thumbnail_file)
                    if jpeg_thumbnail_file:
                        self._merge_poster_with_audio(audio_file, jpeg_thumbnail_file)

    def _get_thumbnail_url(self, entry):
        thumbnails = entry.get('thumbnails', [{}])
        return thumbnails[-1].get('url', None)

    def _download_thumbnail(self, url, path):
        try:
            with yt_dlp.YoutubeDL({'outtmpl': path}) as ydl:
                ydl.download([url])

            jpeg_path = os.path.splitext(path)[0] + '.jpg'
            self._convert_thumbnail_to_jpeg(path, jpeg_path)
            return jpeg_path
        except Exception as e:
            self._show_error(f"An error occurred while downloading the thumbnail: {str(e)}")
            return None

    def _convert_thumbnail_to_jpeg(self, input_path, output_path):
        try:
            command = [get_ffmpeg_path(), '-i', input_path, output_path]
            subprocess.run(command, check=True)
            os.remove(input_path)
        except Exception as e:
            self._show_error(f"An error occurred during thumbnail conversion: {str(e)}")

    def _merge_poster_with_audio(self, audio_file, thumbnail_file):
        output_file = os.path.splitext(audio_file)[0] + '_final.' + self.audio_format
        command = [
            get_ffmpeg_path(), '-i', audio_file, '-i', thumbnail_file,
            '-map', '0', '-map', '1', '-c', 'copy', '-id3v2_version', '3',
            '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (front)"',
            output_file
        ]

        try:
            print(f"Debug - Merging poster with audio using command: {' '.join(command)}")
            subprocess.run(command, check=True)
            os.remove(audio_file)
            os.rename(output_file, audio_file)
        except Exception as e:
            self._show_error(f"An error occurred during merging poster with audio: {str(e)}")
        finally:
            if os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)

    def _show_error(self, message):
        print("Error:", message)  # Debug print
        messagebox.showerror("Error", message)



def get_ffmpeg_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'ffmpeg.exe')
    else:
        return 'ffmpeg.exe'
class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Horizon Vid Downloader by @Umar Aslam v1.0")
        self.root.geometry("720x480")
        self.apply_dark_theme()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')

        self.video_download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.video_download_frame, text='Video Download')
        self.create_video_download_tab(self.video_download_frame)

        self.audio_download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_download_frame, text='Audio Download')
        self.create_audio_download_tab(self.audio_download_frame)

        self.playlist_download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.playlist_download_frame, text='Playlist Download')
        self.create_playlist_download_tab(self.playlist_download_frame)

        self.audio_playlist_download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.audio_playlist_download_frame, text='Audio Playlist Download')
        self.create_audio_playlist_download_tab(self.audio_playlist_download_frame)

    def apply_dark_theme(self):
        # Set background for the root window
        self.root.configure(bg="#333")

        # Create a style for ttk widgets
        style = ttk.Style()
        style.theme_use('clam')

        # Configure notebook and tabs
        style.configure('TNotebook', background='#333', borderwidth=0)
        style.configure('TNotebook.Tab', background='#444', foreground='#fff', padding=[5, 2])
        style.map('TNotebook.Tab', background=[('selected', '#555')])

        # Frames and progress bar styling
        style.configure('TFrame', background='#333')
        style.configure('TProgressbar', troughcolor='#333', background='#777')

        # Set dark theme for standard widgets (like Checkbuttons)
        widgets = self.root.winfo_children()
        for widget in widgets:
            if isinstance(widget, (tk.Button, tk.Entry, tk.Checkbutton, tk.OptionMenu)):
                widget.configure(bg="#444", fg="#fff", bd=0, highlightthickness=0)
            if isinstance(widget, tk.Checkbutton):
                widget.configure(selectcolor="#555")



    def create_video_download_tab(self, frame):
        self.label_font = ("Arial", 14)
        self.entry_font = ("Arial", 12)
        self.button_font = ("Arial", 12, "bold")

        self.video_url_label = tk.Label(frame, text="Enter Video URL:", bg="#333", fg="#fff", font=self.label_font)
        self.video_url_label.pack(pady=6)
        self.video_url_entry = tk.Entry(frame, width=60, bg="#444", fg="#fff", insertbackground="#fff", font=self.entry_font)
        self.video_url_entry.pack(pady=6)
        self.create_context_menu(self.video_url_entry)

        self.resolution_label = tk.Label(frame, text="Select Resolution:", bg="#333", fg="#fff", font=self.label_font)
        self.resolution_label.pack(pady=6)
        self.resolution_var = tk.StringVar(value='best')
        self.resolutions = ['144p', '360p','480', '720p', '1080p', '1440p', '2160p (4K)', 'best']
        self.resolution_menu = tk.OptionMenu(frame, self.resolution_var, *self.resolutions)
        self.resolution_menu.config(bg="#444", fg="#fff", font=self.entry_font)
        self.resolution_menu.pack(pady=6)

        self.video_save_location_button = tk.Button(
            frame, text="Choose Save Location", 
            command=lambda: self.choose_save_location(self.video_save_location_var),
            bg="#555", fg="#fff", font=self.button_font
        )
        self.video_save_location_button.pack(pady=6)

        self.video_save_location_var = tk.StringVar()

        # Subtitle Option for Video Tab
        self.video_subtitle_var = tk.BooleanVar(value=False)

        # Define the callback function
        def on_video_subtitle_toggle():
            if self.video_subtitle_var.get():
                print("Video subtitle will be downloaded.")
            else:
                print("Video subtitle will not be downloaded.")

        # Create the checkbox with the callback
        self.video_subtitle_check = tk.Checkbutton(
            frame,
            text="Include Subtitles",
            variable=self.video_subtitle_var,
            command=on_video_subtitle_toggle,  # Bind the callback correctly
            bg="#333",
            fg="#fff",
            selectcolor="#555",
            font=self.label_font
        )
        self.video_subtitle_check.pack(pady=6)

        self.download_button = tk.Button(
            frame, text="Download", command=self.start_video_download_thread, bg="#555", fg="#fff", font=self.button_font
        )
        self.download_button.pack(pady=12)

        self.video_progress_label = tk.Label(frame, text="", bg="#333", fg="#fff", font=self.label_font)
        self.video_progress_label.pack(pady=6)
        self.video_progress_bar = ttk.Progressbar(frame, length=480, mode="determinate")
        self.video_progress_bar.pack(pady=12)

    def create_audio_download_tab(self, frame):
        self.label_font = ("Arial", 14)
        self.entry_font = ("Arial", 12)
        self.button_font = ("Arial", 12, "bold")

        self.audio_url_label = tk.Label(frame, text="Enter Video URL:", bg="#333", fg="#fff", font=self.label_font)
        self.audio_url_label.pack(pady=6)
        self.audio_url_entry = tk.Entry(frame, width=60, bg="#444", fg="#fff", insertbackground="#fff", font=self.entry_font)
        self.audio_url_entry.pack(pady=6)
        self.create_context_menu(self.audio_url_entry)

        self.codec_label = tk.Label(frame, text="Select Audio Codec:", bg="#333", fg="#fff", font=self.label_font)
        self.codec_label.pack(pady=6)
        self.codec_var = tk.StringVar(value='mp3')
        self.codecs = ['mp3', 'aac', 'wav', 'flac']
        self.codec_menu = tk.OptionMenu(frame, self.codec_var, *self.codecs)
        self.codec_menu.config(bg="#444", fg="#fff", font=self.entry_font)
        self.codec_menu.pack(pady=6)

        self.audio_save_location_button = tk.Button(
            frame, text="Choose Save Location",
            command=lambda: self.choose_save_location(self.audio_save_location_var),
            bg="#555", fg="#fff", font=self.button_font
        )
        self.audio_save_location_button.pack(pady=6)

        self.audio_save_location_var = tk.StringVar()

        # Subtitle Option for Audio Tab
        self.audio_subtitle_var = tk.BooleanVar(value=False)

        # Define the callback function
        def on_audio_subtitle_toggle():
            if self.audio_subtitle_var.get():
                print("Audio subtitle will be downloaded.")
            else:
                print("Audio subtitle will not be downloaded.")

        # Create the checkbox with the callback
        self.audio_subtitle_check = tk.Checkbutton(
            frame,
            text="Include Subtitles",
            variable=self.audio_subtitle_var,
            command=on_audio_subtitle_toggle,  # Bind the callback correctly
            bg="#333",
            fg="#fff",
            selectcolor="#555",
            font=self.label_font
        )
        self.audio_subtitle_check.pack(pady=6)

        self.poster_var = tk.BooleanVar(value=False)
        self.poster_check = tk.Checkbutton(
            frame, text="Include Video Poster", variable=self.poster_var, bg="#333", fg="#fff",
            selectcolor="#555", font=self.label_font
        )
        self.poster_check.pack(pady=6)

        self.download_button = tk.Button(
            frame, text="Download", command=self.start_audio_download_thread, bg="#555", fg="#fff", font=self.button_font
        )
        self.download_button.pack(pady=12)

        self.audio_progress_label = tk.Label(frame, text="", bg="#333", fg="#fff", font=self.label_font)
        self.audio_progress_label.pack(pady=6)
        self.audio_progress_bar = ttk.Progressbar(frame, length=480, mode="determinate")
        self.audio_progress_bar.pack(pady=12)

    def create_playlist_download_tab(self, frame):
        self.label_font = ("Arial", 14)
        self.entry_font = ("Arial", 12)
        self.button_font = ("Arial", 12, "bold")

        self.playlist_url_label = tk.Label(frame, text="Enter YouTube Playlist URL:", bg="#333", fg="#fff", font=self.label_font)
        self.playlist_url_label.pack(pady=6)
        self.playlist_url_entry = tk.Entry(frame, width=60, bg="#444", fg="#fff", insertbackground="#fff", font=self.entry_font)
        self.playlist_url_entry.pack(pady=6)
        self.create_context_menu(self.playlist_url_entry)

        self.resolution_label = tk.Label(frame, text="Select Resolution:", bg="#333", fg="#fff", font=self.label_font)
        self.resolution_label.pack(pady=6)
        self.resolution_var = tk.StringVar(value='best')
        self.resolutions = ['144p', '360p','480', '720p', '1080p', '1440p', '2160p (4K)', 'best']
        self.resolution_menu = tk.OptionMenu(frame, self.resolution_var, *self.resolutions)
        self.resolution_menu.config(bg="#444", fg="#fff", font=self.entry_font)
        self.resolution_menu.pack(pady=6)

        self.playlist_save_location_button = tk.Button(
            frame, text="Choose Save Location",
            command=lambda: self.choose_save_location(self.playlist_save_location_var),
            bg="#555", fg="#fff", font=self.button_font
        )
        self.playlist_save_location_button.pack(pady=6)

        self.playlist_save_location_var = tk.StringVar()

        # Subtitle Option for Playlist Tab
        self.playlist_subtitle_var = tk.BooleanVar(value=False)

        # Define the callback function
        def on_playlist_subtitle_toggle():
            if self.playlist_subtitle_var.get():
                print("Playlist subtitles will be downloaded.")
            else:
                print("Playlist subtitles will not be downloaded.")

        # Create the checkbox with the callback
        self.playlist_subtitle_check = tk.Checkbutton(
            frame,
            text="Include Subtitles",
            variable=self.playlist_subtitle_var,
            command=on_playlist_subtitle_toggle,  # Bind the callback correctly
            bg="#333",
            fg="#fff",
            selectcolor="#555",
            font=self.label_font
        )
        self.playlist_subtitle_check.pack(pady=6)

        self.playlist_download_button = tk.Button(
            frame, text="Download Playlist", command=self.start_playlist_download_thread, bg="#555", fg="#fff", font=self.button_font
        )
        self.playlist_download_button.pack(pady=12)

        self.playlist_progress_label = tk.Label(frame, text="", bg="#333", fg="#fff", font=self.label_font)
        self.playlist_progress_label.pack(pady=6)
        self.playlist_progress_bar = ttk.Progressbar(frame, length=480, mode="determinate")
        self.playlist_progress_bar.pack(pady=12)

    def create_audio_playlist_download_tab(self, frame):
        self.label_font = ("Arial", 14)
        self.entry_font = ("Arial", 12)
        self.button_font = ("Arial", 12, "bold")

        self.audio_playlist_url_label = tk.Label(frame, text="Enter YouTube Playlist URL:", bg="#333", fg="#fff", font=self.label_font)
        self.audio_playlist_url_label.pack(pady=6)
        self.audio_playlist_url_entry = tk.Entry(frame, width=60, bg="#444", fg="#fff", insertbackground="#fff", font=self.entry_font)
        self.audio_playlist_url_entry.pack(pady=6)
        self.create_context_menu(self.audio_playlist_url_entry)

        self.codec_label = tk.Label(frame, text="Select Audio Codec:", bg="#333", fg="#fff", font=self.label_font)
        self.codec_label.pack(pady=6)
        self.codec_var = tk.StringVar(value='mp3')
        self.codecs = ['mp3', 'aac', 'wav', 'flac']
        self.codec_menu = tk.OptionMenu(frame, self.codec_var, *self.codecs)
        self.codec_menu.config(bg="#444", fg="#fff", font=self.entry_font)
        self.codec_menu.pack(pady=6)

        self.audio_playlist_save_location_button = tk.Button(
            frame, text="Choose Save Location",
            command=lambda: self.choose_save_location(self.audio_playlist_save_location_var),
            bg="#555", fg="#fff", font=self.button_font
        )
        self.audio_playlist_save_location_button.pack(pady=6)

        self.audio_playlist_save_location_var = tk.StringVar()

        self.poster_var = tk.BooleanVar(value=False)
        self.poster_check = tk.Checkbutton(
            frame, text="Include Video Poster", variable=self.poster_var, bg="#333", fg="#fff",
            selectcolor="#555", font=self.label_font
        )
        self.poster_check.pack(pady=6)

        self.audio_playlist_download_button = tk.Button(
            frame, text="Download Playlist", command=self.start_audio_playlist_download_thread, bg="#555", fg="#fff", font=self.button_font
        )
        self.audio_playlist_download_button.pack(pady=12)

        self.audio_playlist_progress_label = tk.Label(frame, text="", bg="#333", fg="#fff", font=self.label_font)
        self.audio_playlist_progress_label.pack(pady=6)
        self.audio_playlist_progress_bar = ttk.Progressbar(frame, length=480, mode="determinate")
        self.audio_playlist_progress_bar.pack(pady=12)

    def choose_save_location(self, var):
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)

    def start_video_download_thread(self):
        url = self.video_url_entry.get()
        resolution = self.resolution_var.get()
        save_location = self.video_save_location_var.get()
        include_subtitles = self.video_subtitle_var.get()

        downloader = VideoDownloader(url, resolution, save_location, include_subtitles, 
                                   lambda t, v: self.update_progress(self.video_progress_label, self.video_progress_bar, t, v))
        thread = threading.Thread(target=downloader.download_video)
        thread.daemon = True
        thread.start()

    def start_audio_download_thread(self):
        url = self.audio_url_entry.get()
        codec = self.codec_var.get()
        save_location = self.audio_save_location_var.get()
        include_subtitles = self.audio_subtitle_var.get()
        include_poster = self.poster_var.get()

        downloader = AudioDownloader(url, codec, save_location, include_subtitles, include_poster,
                                   lambda t, v: self.update_progress(self.audio_progress_label, self.audio_progress_bar, t, v))
        thread = threading.Thread(target=downloader.download_audio)
        thread.daemon = True
        thread.start()

    def start_playlist_download_thread(self):
        url = self.playlist_url_entry.get()
        resolution = self.resolution_var.get()
        save_location = self.playlist_save_location_var.get()
        include_subtitles = self.playlist_subtitle_var.get()

        downloader = PlaylistDownloader(url, resolution, save_location, include_subtitles,
                                        lambda t, v: self.update_progress(self.playlist_progress_label, self.playlist_progress_bar, t, v))
        thread = threading.Thread(target=downloader.download_playlist)
        thread.daemon = True
        thread.start()

    def start_audio_playlist_download_thread(self):
        url = self.audio_playlist_url_entry.get()
        codec = self.codec_var.get()
        save_location = self.audio_playlist_save_location_var.get()
        include_poster = self.poster_var.get()

        downloader = AudioPlaylistDownloader(url, codec, save_location, include_poster,
                                             lambda t, v: self.update_progress(self.audio_playlist_progress_label, self.audio_playlist_progress_bar, t, v))
        thread = threading.Thread(target=downloader.download_playlist)
        thread.daemon = True
        thread.start()

    def update_progress(self, label, progress_bar, text, value):
        label.config(text=text)
        progress_bar['value'] = value
        self.root.update_idletasks()

    def create_context_menu(self, widget):
        def paste_clipboard(event):
            widget.event_generate("<<Paste>>")

        widget.bind("<Button-3>", paste_clipboard)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()