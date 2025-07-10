# Music-Player-using-Tkinter-in-Python
A music player interface with all most used features and functionalitues.


# Dilshad's Music Player

#### Video Demo:  [Watch on YouTube](https://youtu.be/wDdmo-YznOk)
#### Description:


A modern and interactive desktop music player built with Tkinter, ttkbootstrap, and Pygame. It supports MP3/WAV playback, custom background images, intuitive keyboard controls, and dynamic UI features like song progress slider and time tracking.
Theme used: Vapor

Dilshad's Music Player is a fully GUI-based desktop audio player designed for ease of use and visual appeal. Built using Tkinter and enhanced with `ttkbootstrap` theme 'vapor', it supports seamless playback of MP3/WAV files directly from user-selected folders.

The player also features live progress tracking with a custom slider, dynamic time display, and a unique visual experience using randomly chosen background images. Designed with keyboard accessibility in mind, users can control playback, shuffle, and seek with/without using a mouse.


## 🧠 How It Works

- The main application initializes a `ttkbootstrap` window and splits the layout into two panels:
  - `SongListPanel`: Displays the loaded songs in a listbox and allows folder selection.
  - `ImagePanel`: Displays dynamic backgrounds, progress slider, and control buttons.

- Music is managed through a custom `MusicManager` class that handles:
  - Loading and indexing song files
  - Tracking the current song
  - Shuffling and randomly selecting tracks

- Playback is handled using the `pygame.mixer` module, and the time tracking is updated every second using a recursive call via Tkinter's `after()` method.

Clicking GUI buttons executes functions dedicated to each of them.
Resizing window redraws and readjusts background image and buttons respectively.


## Challenges faced:

A lot of technical bugs in function named `timer_status` while seeking through slider due to self call.
The self call after each second is done so as to update the GUI (progress slider and elapsed time).
Fix was to store a single call and cancel any previous call in that 1 second duration.

Wrong elapsed time while pausing since program kept switching to refer `current_time` rather than slider position while paused.
Used flags to define behaviour while paused in order to fix it.


## 🚀 Features:

🎧 Play/Pause/Resume music using buttons or spacebar
🔀 Shuffle or 🎲 Randomly select songs with a single click or keyboard shortcuts
⏮️ ⏯️ ⏭️ Navigate previous, next, and current songs
📁 Load music folder to populate the playlist automatically
🖼️ Dynamic background images (changes with every song)
⌛ Live time tracking and seek bar to jump to different parts of the song
🎹 Keyboard Shortcuts:
    Space → Play/Pause
    S → Shuffle
    R → Random
    ← / → → Seek backward/forward 5 seconds


## 📁 Folder Structure

    your_project/
    ├── bg_images/         # Background images (picks images randomly)
    ├── main.py            # Main application file
    └── README.md


## 🛠️ Requirements
    Python 3.8+

    pygame
    Pillow
    ttkbootstrap
    tkinter

    random
    time
    os


## Total time taken:
    2-3 days
    10 hours approx.
