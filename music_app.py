import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.widgets import Scale
from PIL import Image, ImageTk
import os
import random
import pygame
import time


def main():
    app = Application()
    app.mainloop()

# Music Manager class handles all music related indexing and returning song path on that index
class MusicManager():
    def __init__(self, music_files=None):
        self.music_files = music_files or []
        self.current_index = 0

    @classmethod
    def get_folder(cls):
        folder = filedialog.askdirectory(title="Select music folder") # For selecting music folder from my pc
        if folder:
            music_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith((".mp3", ".wav"))]
            return cls(music_files)
        return cls([]) # Return empty list if no folder found
    

    def get_all_files(self):
        return self.music_files


    def current_song(self):
        if self.music_files:
            return self.music_files[self.current_index]
        return None
    

    def next(self):
        if self.music_files:
            self.current_index = (self.current_index + 1) % len(self.music_files)
            return self.current_song()


    def prev(self):
        if self.music_files:
            self.current_index = (self.current_index - 1) % len(self.music_files)
            return self.current_song()
        

    def random_song(self):
        if self.music_files:
            self.current_index = random.randint(0, len(self.music_files) - 1)
            return self.current_song()
        
    
    def shuffle_list(self):
        random.shuffle(self.music_files)
        self.current_index = 0

# Application is a ttk.Window child class that is customized for functionalities of my music player
class Application(ttk.Window):
    def __init__(self):
        super().__init__(themename="vapor")
        self.title("Dilshad's Music Player")
        self.geometry("800x500")

        pygame.mixer.init()

        self.music_manager = MusicManager() # Object of MusicManager class for getting song path
        
        self.columnconfigure(0, weight=1) # SongListPanel takes 1 of 5 parts of horizontal space
        self.columnconfigure(1, weight=4) # ImagePanel takes 4 of 5 parts of horizontal space
        self.rowconfigure(0, weight=1) # Allows horizontal resizing of rows w.r.t. window

        self.frame_L = SongListPanel(self, self.music_manager) # First partition for Listing songs, left child class
        self.frame_L.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.frame_R = ImagePanel(self, self.music_manager) # Second partition for Background and buttons logic, i.e., features, right child class
        self.frame_R.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.is_playing = False # Flag for play/resume button logic
        self.is_paused = False # Flag for Pause/Resume button logic

        self.bind_all("<space>", self.toggle_play_pause) # Globally binds Space button that calls toggle_play_pause function 

    # Actual audio output using pygame.mixer.music
    def play_song(self):
        song = self.music_manager.current_song()
        if not song:
            return

        pygame.mixer.music.load(song) # Loads song to play
        pygame.mixer.music.play() # Plays loaded song
        self.is_playing = True
        self.is_paused = False
        self.frame_R.slider_used = False

        self.frame_R.progress_slider.set(0)
        self.frame_R.current_time = 0

        self.frame_L.highlight_current() # Current song is highlighted in Listbox
        self.frame_R.update_bg() # Next random bg image whenever music plays
        self.frame_R.update_play_button(self.is_playing) # Symbol and text of button updates according to above flags
        self.frame_R.timer_status(song) # Updates progress slider and current time/total time
    
    # Play and pause logic
    def toggle_play_pause(self, event=None):
        if not self.is_playing:
            self.play_song() # If song is not playing, pressing spacebar plays song
        elif self.is_paused:
            pygame.mixer.music.unpause() # If song is playing and is paused, spcaebar resumes song
            self.is_paused = False
            self.frame_R.update_play_button(True)
        else:
            pygame.mixer.music.pause() # If song is playing but not paused, spacebar pauses song
            self.is_paused = True
            self.frame_R.update_play_button(False)


    def next_song(self):
        self.music_manager.next()
        self.play_song()


    def prev_song(self):
        self.music_manager.prev()
        self.play_song()


    def shuffle(self, event=None):
        self.music_manager.shuffle_list()
        self.frame_L.refresh_list()
        self.play_song()
    

    def random(self, event=None):
        self.music_manager.random_song()
        self.play_song()

# ImagePanel handles background changes, image resizing, progress slider, time status, button updation, and button logic
class ImagePanel(ttk.Frame): # Customized ttk.Frame for music player
    def __init__(self, parent, music_manager):
        super().__init__(parent)
        self.parent = parent # Parent is Application class
        self.music_manager = music_manager # MusicManager obj from parent class for logical handling
        self.slider_used = False # slider flag for seek logic using slider
        self.timer_job = None # Keeps track of most recent recursive call of timer_status function

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        script_dir = os.path.dirname(os.path.abspath(__file__)) # Get current directory path
        self.bg_folder = os.path.join(script_dir, "bg_images") # Join path with bg_images from current directory

        # Loading all images
        self.bg_images = [
            os.path.join(self.bg_folder, f)
            for f in os.listdir(self.bg_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        self.image = Image.open(random.choice(self.bg_images)) if self.bg_images else Image.new("RGB", (600, 500)) # Random image for bg, else failsafe solid color bg

        self.canvas = tk.Canvas(self) # Declare a canvas for image resizing/drawing
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.bottom_frame = ttk.Frame(self) # Bottom frame for progress slider
        self.bottom_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.bottom_frame.columnconfigure(1, weight=1)

        self.time_label = ttk.Label(self, text="00:00 / 00:00", font=("Helvetica", 12), bootstyle="inverse-dark") # Timer status label

        # ttkbootstrap progress slider
        self.progress_slider = Scale(
            master=self.bottom_frame,
            orient='horizontal',
            from_=0,
            to=100,
            bootstyle="warning",
        )
        self.progress_slider.grid(row=0, column=1, sticky="ew") # Span entire horizontal length of frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Button initialization and command binding
        self.prev_btn = ttk.Button(self, text="⏮ Prev", bootstyle="info-toolbutton", padding=10, command=self.parent.prev_song)
        self.play_btn = ttk.Button(self, text="▶ Play", bootstyle="success-outline-toolbutton", padding=10, command=self.parent.toggle_play_pause)
        self.next_btn = ttk.Button(self, text="⏭ Next", bootstyle="info-toolbutton", padding=10, command=self.parent.next_song)
        self.shuffle_btn = ttk.Button(self, text="🔀 Shuffle", bootstyle="warning-outline-toolbutton", command=self.parent.shuffle)
        self.random_btn = ttk.Button(self, text="🎲 Random", bootstyle="warning-outline-toolbutton", command=self.parent.random)

        self.bind("<Configure>", self.resize_img) # Call resize_img function whenever window is resized
        self.progress_slider.bind("<ButtonRelease-1>", self.seek_song) # Bind seek_song to slider for jumping to desired song part
        # Left and Right keys to move backward and forward 5 seconds
        self.bind_all("<Right>", self.seek_forward)
        self.bind_all("<Left>", self.seek_backward)
        # S or s to shuffle song
        self.bind_all("<s>", self.parent.shuffle)
        self.bind_all("<S>", self.parent.shuffle)
        # R or r to play random song
        self.bind_all("<r>", self.parent.random)
        self.bind_all("<R>", self.parent.random)

    # Random background image from folder
    def update_bg(self):
        if not self.bg_images:
            return
        path = random.choice(self.bg_images)
        self.image = Image.open(path)

        self.resize_img()

    # Resize/redraw images on canvas when window resizes and adjust button positioning
    def resize_img(self, event=None):
        width = event.width if event else self.winfo_width()
        height = event.height if event else self.winfo_height()

        resized = self.image.resize((width, height), Image.Resampling.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        center_x = width // 2
        btn_y = int(height * 0.8)
        spacing = 80

        self.canvas.create_window(center_x - 2 * spacing, btn_y, window=self.prev_btn)
        self.canvas.create_window(center_x,               btn_y, window=self.play_btn)
        self.canvas.create_window(center_x + 2 * spacing, btn_y, window=self.next_btn)

        pad_x = 20
        pad_y = 20
        button_spacing = 110  # space between shuffle and random

        self.canvas.create_window(pad_x, pad_y, anchor="nw", window=self.shuffle_btn)
        self.canvas.create_window(pad_x + button_spacing, pad_y, anchor="nw", window=self.random_btn)
        self.canvas.create_window(pad_x + button_spacing*3, pad_y, anchor="nw", window=self.time_label)


    def update_play_button(self, is_playing):
        if is_playing:
            self.play_btn.config(text="⏸ Pause")
        else:
            self.play_btn.config(text="⏯ Resume")

    # Display time elapsed, get slider position, set slider position related logic     (This took most of my time debugging)
    def timer_status(self, path=None):
        if self.timer_job:  # If there's an old timer
            self.after_cancel(self.timer_job)  # Cancel it          (This makes sure in cases of instantaneous calls of seeking new position, only one instance of self function call remains)
            self.timer_job = None
        self.current_time = pygame.mixer.music.get_pos() / 1000
        self.elapsed_time = time.strftime('%M:%S', time.gmtime(self.current_time))

        # Try to get total song duration and set max value of slider bar to song duration
        try:
            sound = pygame.mixer.Sound(path)
            self.song_len = time.strftime('%M:%S', time.gmtime(sound.get_length())) # Convert song duration from seconds to date-time string
            self.progress_slider.config(to=int(sound.get_length())) # Max slider length set to song duration
        except TypeError:
            pass

        # If slider is not used, proceed with using current_time to set position and elapsed time
        if not self.slider_used:
            self.progress_slider.set(int(self.current_time))
        
        # Following statements helps to fix minor bug where time label uses current_time var if song is paused after we use seek function
        elif self.parent.is_paused:
            self.time_label.after(1000, self.timer_status) # Continue recalling function to keep slider and time updated when resumed
            return
        
        # If slider is used, set slider to new position and use new position time for time display
        else:
            self.progress_slider.set(int(self.progress_slider.get()))
            self.elapsed_time = time.strftime('%M:%S', time.gmtime(self.progress_slider.get()))
            self.continue_time = int(self.progress_slider.get()) + 1
            self.progress_slider.set(int(self.continue_time))
 
        self.time_label.config(text=f"{self.elapsed_time} / {self.song_len}") # Displays time label in 00:00 / 00:00 format

        # If time elapsed reaches song total time, reset slider and play next song
        if self.elapsed_time >= self.song_len:
            self.parent.next_song()
            return

        self.timer_job = self.after(1000, self.timer_status) # Calls itself after 1 second to update time and slider position (gives dynamic effect)


    def seek_song(self, event=None):
        if self.parent.music_manager.current_song():
            new_pos = self.progress_slider.get()
            self.slider_used = True
            try:
                pygame.mixer.music.set_pos(new_pos)
            except Exception as e:
                print(f"Seek failed: {e}")
                

    def seek_forward(self, event=None):
        if self.parent.music_manager.current_song():
            new_pos = self.progress_slider.get() + 5
            self.slider_used = True
            try:
                pygame.mixer.music.set_pos(new_pos)
                self.progress_slider.set(new_pos)
            except Exception as e:
                print(f"Seek failed: {e}")

    
    def seek_backward(self, event=None):
        if self.parent.music_manager.current_song():
            new_pos = self.progress_slider.get() - 5
            new_pos = max(0, new_pos)
            self.slider_used = True
            try:
                pygame.mixer.music.set_pos(new_pos)
                self.progress_slider.set(new_pos)
            except Exception as e:
                print(f"Seek failed: {e}")

# SongListPanel logic class
class SongListPanel(ttk.Frame):
    def __init__(self, parent, music_manager):
        super().__init__(parent)
        self.parent = parent
        self.music_manager = music_manager

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.load_btn = ttk.Button(self, text='📁 Load Folder', command=self.load_music_folder)
        self.load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

        self.song_list = tk.Listbox(self)
        self.song_list.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.song_list.bind("<Double-Button-1>", self.play_selected)
        self.song_list.bind("<Return>", self.play_selected)
        
    # Load new music folder and update changes in parent music manager object
    def load_music_folder(self):
        try:
            new_manager = MusicManager.get_folder()
            if not new_manager.get_all_files():
                return
            self.parent.music_manager = new_manager
            self.music_manager = self.parent.music_manager
            self.refresh_list()
            self.parent.play_song()
        except Exception:
            pass

    # Hightlight song on current index
    def highlight_current(self):
        self.song_list.select_clear(0, tk.END)
        idx = self.music_manager.current_index
        self.song_list.selection_set(idx)
        self.song_list.see(idx)

    # Delete entire listbox content and reprint
    def refresh_list(self):
        self.song_list.delete(0, tk.END)
        for file in self.music_manager.get_all_files():
            self.song_list.insert(tk.END, os.path.basename(file))

    # Play song which is double clicked on SongListPanel
    def play_selected(self, event=None):
        try:
            idx = self.song_list.curselection()[0]
            self.music_manager.current_index = idx
            self.parent.play_song()
        except IndexError:
            pass

    
if __name__ == "__main__":
    main()