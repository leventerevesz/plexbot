# PlexBot

A Telegram bot that downloads stuff on your server

## Usage

▶️ Send a youtube link, the bot downloads it on the server.

## Install

```
python3 -m pip install .
```

Get a token from the BotFather.

Edit the config file and copy it to `~/.config/plexbot/`.

Edit the service file and copy it to `/etc/systemd/system/`.

```
sudo systemctl daemon-reload
sudo systemctl enable plexbot.service
```