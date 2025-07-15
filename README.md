
## Explanation

This project is a Discord bot that integrates with Twitch to provide real-time notifications and interactive features for your Discord server. It allows you to:

- Receive alerts when specified Twitch streamers go live.
- Customize notification messages and embed content.
- Manage bot settings and responses through easy-to-edit JSON configuration files.
- Securely store sensitive information using environment variables.
- Easily set up and run with minimal configuration.

The bot is designed for flexibility and ease of use, making it suitable for communities that want to stay updated on Twitch activity directly within Discord.

---

## ⚙️ Requirements

- Python 3.8+
- [discord.py](https://github.com/Rapptz/discord.py) 2.5+
- [twitchAPI](https://github.com/Teekeks/pyTwitchAPI) 4.5.0+
- python-dotenv
- SQLite3

---

## 📦 Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/tuouser/wish_discord_bot.git
    cd wish_discord_bot
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
    Create a `.env` file in the root directory:
    ```env
    DISCORD_TOKEN=your_token
    TWITCH_CLIENT_ID=your_client_id
    TWITCH_CLIENT_SECRET=your_client_secret
    BOT_COMMUNICATION_CHANNEL_ID=channel_id
    # Add other required variables as needed
    ```

---

## 🔧 Configuration

The bot uses several JSON configuration files (auto-generated or manually created):

- `config.json` — General bot and server settings
- `embed_text.json` — Customizable texts for embed messages
- `twitch_data.json` — Twitch integration settings
- `verification_data.json` — Verification system data

---

## 💻 Usage

**Start the bot:**
```bash
python main.py
```

---

## 🏷️ Main Commands

- `/admin clear` — Bulk delete messages in a channel
- `/admin config` — Manage server and bot configuration
- `/role assign` — Assign roles to users
- `/role remove` — Remove roles from users
- `/role mass-assign` — Assign a role to multiple users
- `/verification setup` — Set up the verification system
- `/twitch add-tag` — Add tags for Twitch notifications
- `/twitch set-title` — Change Twitch stream title
- `/info user` — Get information about a user
- `/info server` — Get server statistics and info
- `/utility ...` — Various utility commands

*And many more! Use `/help` or check the code for the full list.*

---

## 🧩 Extending the Bot

Wish Discord Bot is modular! You can add new features by creating new cogs in the `cogs/` directory or utilities in `utils/`. The project is structured for easy expansion and maintenance.

---

## 📝 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).


---

## 📫 Contact

For support or questions, open an issue or contact the maintainer via GitHub.

---
