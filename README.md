![Boombox Icon](https://raw.githubusercontent.com/lonewanderer27/Boombox-v4/master/boombox_v4_icon.png)

# Boombox v4

Next major release of Boombox, rewritten from the ground up to utilize cogs and slash commands feature!  
This version is currently work in progress!

# Features!

- Play
  - Song's title
  - Youtube link, including playlist
- Pause / Next / Stop the music
- Shuffle
- Display lyrics
- Show the queue
- Move the bot to a channel
- Uses slash command
- Uses cogs for better organization of code [FINALLY!]

### Planned:

- [ ] Allow the user to reorder queued music
- [ ] Support for other sources like Spotify, Apple Music, Deezer etc...
- [ ] Optimize code further [Playing music & getting lyrics is now faster thanks to this!]

# Run the Bot!

#### Installing Python on Windows

1. Download the latest Python installer for Windows from the official website: https://www.python.org/downloads/windows/
2. Run the installer and follow the installation wizard.
3. During the installation, make sure to select "Add Python to PATH" option.
4. Click "Install Now" button and wait for the installation to complete.

#### Installing Python on Linux / Ubuntu

1. Open a Terminal window.
2. Run the following command to install Python: `sudo apt update && sudo apt install python3`
3. Verify the installation by running the following command: `python3 --version`

#### Installing Poetry

1. Open a new Command Prompt window.
2. Run the following command to install Poetry:<br>
   `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`
3. Navigate to the cloned directory: `cd Boombox-v4`
4. Run the following command to install the required dependencies using Poetry: `poetry install`
5. Create a .env file in the root directory of the project and set the following environment variables:<br>

```
BOOMBOX_PROGRAMMABLE_SEARCH_ENGINE_KEY=<YOUR_API_KEY>
BOOMBOX_PROGRAMMABLE_SEARCH_ENGINE_ID=<YOUR_ENGINE_ID>
BOOMBOX_V4_TOKEN=<YOUR_TOKEN>
```

6. Finally, run the application with the following command: `poetry run python ./app.py`

# Deploy the Bot!

Coming soon! Wait till I get to a stable release!
