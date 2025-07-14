# Wish Discord Bot 🤖

A multifunctional Discord bot written in Python that offers moderation features, user verification, role management, Twitch integration, and much more.

## 🌟 Main Features

- ⚙️ **User verification system**
  - Automatic verification through reactions
  - Configurable timeout
  - Temporary and permanent roles

- 👥 **Role Management**
  - Automatic assignment through reactions
  - Commands to assign/remove roles
  - Mass role management

- 🎮 **Twitch Integration**
  - Live streaming notifications
  - Custom tag management
  - Customizable embed messages

- 🛡️ **Admin Features**
  - Channel cleanup
  - Configuration management
  - Complete logging system

- 📝 **Logging system**
  - Event logging
  - Command logging
  - Message logging
  - Error logging

## ⚙️ Requirements

- Python 3.8+
- Discord.py 2.5+
- SQLite Database
- Discord Bot Token
- Twitch API Credentials

## 📦 Main Dependencies

```text
discord.py==2.5.2
python-dotenv==1.1.0
twitchAPI==4.5.0
sqlite3
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/tuouser/wish_discord_bot.git
cd wish_discord_bot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the `.env` file:
```env
DISCORD_TOKEN=your_token
TWITCH_CLIENT_ID=your_client_id
TWITCH_CLIENT_SECRET=your_client_secret
BOT_COMMUNICATION_CHANNEL_ID=channel_id
...
```

## 🔧 Configuration

The bot uses several configuration files in JSON format:

- `config.json`: General configurations
- `embed_text.json`: Texts for embed messages
- `twitch_data.json`: Twitch configurations
- `verification_data.json`: Verification system data

## 💻 Usage

To start the bot:

```bash
python main.py
```

### Main Commands

- `/admin clear` - Clears messages from a channel
- `/role assign` - Assigns roles to users
- `/verification setup` - Sets up verification system
- `/twitch add-tag` - Adds tags for Twitch notifications

## 📁 Project Structure

```
.
├── bot.py              # Main bot class
├── main.py            # Entry point
├── cogs/              # Commands and features
├── utils/             # Various utilities
├── logger/            # Logging system
└── config_manager/    # Configuration management
```

## 📝 License

[MIT](https://choosealicense.com/licenses/mit/)