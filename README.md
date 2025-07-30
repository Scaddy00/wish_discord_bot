
## Explanation

This project is a Discord bot that integrates with Twitch to provide real-time notifications and interactive features for your Discord server. It allows you to:

- Receive alerts when specified Twitch streamers go live.
- Customize notification messages and embed content.
- Manage bot settings and responses through easy-to-edit JSON configuration files.
- Securely store sensitive information using environment variables.
- Easily set up and run with minimal configuration.
- **Database logging**: Comprehensive logging of events, commands, messages, and errors to SQLite database.
- **User verification system**: Automated verification process with temporary roles and timeouts.
- **Role management**: Automatic role assignment/removal based on reactions and member status.
- **Weekly reports**: Automated weekly summaries of server activity and statistics.
- **Database cleanup**: Automatic cleanup of old records (3+ months) to maintain performance.
- **Message logging**: Track all messages with configurable channel exclusions.

The bot is designed for flexibility and ease of use, making it suitable for communities that want to stay updated on Twitch activity directly within Discord while maintaining comprehensive server management and logging capabilities.

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
    # === Discord Bot ===
    DISCORD_TOKEN=your_discord_bot_token           # Discord bot token (required)
    COMMAND_PREFIX=!                               # Command prefix (e.g., ! or /)

    # === Debug mode ===
    DEBUG_MODE=0                                   # 1 to enable debug mode, 0 for production
    GUILD_ID=0                                     # Dev guild ID for debug mode (leave empty if not using debug)

    # === Twitch API ===
    TWITCH_CLIENT_ID=your_twitch_client_id
    TWITCH_CLIENT_SECRET=your_twitch_client_secret
    TWITCH_URL=https://www.twitch.tv/              # Base Twitch URL (usually does not need to be changed)
    TWITCH_COLOR=6441a5                            # Twitch embed color (hex without #, e.g., 9146FF)

    # === Database and data ===
    DATA_PATH=./data                               # Folder to save data (default: ./data)
    DB_FILE_NAME=database.db                       # SQLite database file name (default: database.db)
    CONFIG_FILE_NAME=config.json                   # Config file name (default: config.json)
    EMBED_TEXT_FILE_NAME=embed_text.json           # Embed texts file name (default: embed_text.json)
    VERIFICATION_DATA_FILE_NAME=verification_data.json # Verification data file name (default: verification_data.json)
    TWITCH_FILE_NAME=twitch_data.json              # Twitch data file name (default: twitch_data.json)

    # === Formats and other ===
    DATETIME_FORMAT=%d/%m/%Y %H:%M:%S              # Datetime format (default: %d/%m/%Y %H:%M:%S)

    # --- Add other variables if needed ---
    ```

---

## 🔧 Configuration

The bot uses several JSON configuration files (auto-generated or manually created):

- `config.json` — General bot and server settings
- `embed_text.json` — Customizable texts for embed messages
- `twitch_data.json` — Twitch integration settings
- `verification_data.json` — Verification system data

### Example: `embed_text.json`

Below is an example of what your `embed_text.json` file might look like. You can customize the title, description, and other fields to change how the bot's embed messages appear in Discord.

```json
{
  "twitch_live": {
    "title": "🔴 {streamer} is now LIVE on Twitch!",
    "description": "Come watch the stream: {url}\n\n**Title:** {title}\n**Game:** {game}",
    "color": 16711680,
    "thumbnail": "{profile_image_url}",
    "footer": "Wish Discord Bot • Stay connected!"
  },
  "verification_success": {
    "title": "✅ Verification Complete!",
    "description": "Welcome, {user}! You have been successfully verified.",
    "color": 65280
  },
  "role_assigned": {
    "title": "🎉 Role Assigned",
    "description": "You have been given the **{role}** role.",
    "color": 3447003
  }
}
```

- You can use placeholders like `{streamer}`, `{url}`, `{title}`, `{game}`, `{profile_image_url}`, and `{user}` which the bot will replace with real values.
- The `color` field uses decimal RGB values (e.g., 16711680 for red).
- Add or modify sections as needed for your server's needs.

---

## 💻 Usage

**Start the bot:**
```bash
python main.py
```

---

## 🏷️ Main Commands

### Admin Commands
- `/admin clear` — Bulk delete messages in current channel
- `/admin clear-channel` — Bulk delete messages in specified channel

### Configuration Commands
- `/config standard` — Execute standard bot configuration
- `/config admin-check` — View all admin configuration data
- `/config admin-add` — Add roles or channels to admin config
- `/config exception-add` — Add role or channel exceptions

### Role Management
- `/role new` — Create new role assignment message with reactions
- `/role assign` — Assign a role to a specific user
- `/role assign-all` — Assign a role to all users (with exceptions)
- `/role remove` — Remove a role from a specific user
- `/role remove-all` — Remove a role from all users (with exceptions)

### Verification System
- `/verification setup` — Set up the verification system

### Twitch Integration
- `/twitch add-tag` — Add new tags for live streams and image selection
- `/twitch change-title` — Change stream titles for different tags
- `/twitch change-streamer` — Change the streamer name
- `/twitch reset-info` — Reset last stream information

### Embed Commands
- `/embed dreamer-unico` — Send embed with Dreamer unique information
- `/embed dreamer-sub` — Send embed with Dreamer subscription levels information
- `/embed rule-new` — Create new rule messages with reactions
- `/embed rule-reload` — Reload existing rule embed with updated content

### Utility Commands
- `/utility emoji-to-unicode` — Get Unicode value of an emoji

### Information Commands
- `/info user` - Display detailed user information

*And many more! Use `/help` or check the code for the full list.*

---

## 🔔 Discord Events

The bot listens and reacts to several Discord events to automate server management and enhance user experience. Here are the main events handled:

- **on_ready**: Triggered when the bot is ready and connected. Used to authenticate Twitch, restore verification tasks, and start background tasks.
- **on_guild_join**: Welcomes the bot to a new server and sends setup instructions.
- **on_member_join**: Sends a welcome message to new members and assigns roles if configured.
- **on_raw_member_remove**: Notifies when a user leaves the server.
- **on_member_update**: Detects when a user becomes or stops being a server booster and updates roles accordingly.
- **on_message**: Logs messages sent in the server, except those in excluded channels or by bots.
- **on_raw_reaction_add**: Handles role assignment and verification when users react to specific messages.
- **on_raw_reaction_remove**: Handles role removal when users remove reactions from specific messages.

Additionally, the bot runs scheduled background tasks such as:
- **Booster check**: Periodically checks and updates server booster roles.
- **Twitch notifications**: Monitors Twitch streams and sends notifications.
- **Weekly report**: Sends a weekly summary of server activity and events.
- **Database cleanup**: Daily cleanup of old records (3+ months) to maintain database performance.

---

## 🧩 Extending the Bot

Wish Discord Bot is modular! You can add new features by creating new cogs in the `cogs/` directory or utilities in `utils/`. The project is structured for easy expansion and maintenance.

### Project Structure

```
wish_discord_bot/
├── bot.py                 # Main bot class
├── main.py               # Entry point
├── database/             # Database management
├── logger/               # Logging system
├── config_manager/       # Configuration management
├── cogs/
│   ├── commands/         # Slash commands
│   ├── events/           # Discord event handlers
│   ├── tasks/            # Background tasks
│   ├── modals/           # UI components
│   ├── verification/     # User verification system
│   └── twitch/           # Twitch integration
└── utils/                # Utility functions
```

### Key Features

- **Database Integration**: SQLite database with automatic connection management
- **Comprehensive Logging**: All events, commands, and errors are logged
- **Modular Architecture**: Easy to extend with new cogs and features
- **Configuration Management**: JSON-based configuration with environment variables
- **Error Handling**: Robust error handling with logging and notifications
- **User Information System**: Enhanced user data display with detailed Discord User object information
- **Real-time Interaction Handling**: Proper Discord interaction management with timeout handling

---

## 📝 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).


---

## 📚 Code Documentation

The project includes comprehensive docstrings throughout the codebase:

- **Database Operations**: All database methods are documented with parameters and return types
- **Logging Functions**: Complete documentation of logging methods and their usage
- **Command Classes**: All Discord commands include parameter descriptions
- **Event Handlers**: Event processing functions are fully documented
- **Utility Functions**: Helper functions include usage examples and parameter descriptions

The code follows Google/NumPy docstring format for consistency and IDE compatibility.

---

## 📫 Contact

For support or questions, open an issue or contact the maintainer via GitHub.

---
