# Justanotherpanel Discord Bot

A Discord bot for ordering social media services (like Instagram Likes, TikTok Likes, etc.) using the JustAnotherPanel API. All services and configuration are managed via JSON files for easy expansion and maintenance.

## Features
- Add unlimited services (Instagram, TikTok, etc.) via `serviceconfig.json`
- Dynamic command creation for each service
- Real-time price fetching from the API
- Order confirmation with Discord UI buttons
- Owner-only command access

## Important Notes
- This bot uses the [JustAnotherPanel](https://justanotherpanel.com/) API for all service orders. You must have an account and a valid API key from their platform.
- Make sure your JustAnotherPanel account has sufficient balance. If your balance is low or empty, orders will not be processed and the bot will not work as expected.

## Setup Instructions

### 1. Download this Repository

### 2. Install Requirements
This bot requires Python 3.8+.
Install dependencies:
```
pip install -r requirements.txt
```

### 3. Configure the Bot

#### `config.json`
Fill in your Discord bot token, API keys, and owner ID:
```json
{
  "BOT_TOKEN": "YOUR_BOT_TOKEN",
  "JUSTANOTHERPANEL_API_KEY": "YOUR_JUSTANOTHERPANEL_API_KEY",
  "JUSTANOTHERPANEL_API_URL": "https://justanotherpanel.com/api/v2",
  "EXCHANGE_RATE_API_KEY": "YOUR_EXCHANGERATE_API_KEY",
  "EXCHANGE_RATE_API_URL": "https://v6.exchangerate-api.com/v6/078cfb5699eb40b0c8754985/latest/USD",
  "OWNER_ID": 1025029483847241738
}
```

#### `serviceconfig.json`
Add or edit services as needed:
```json
{
  "services": {
    "iglikes": {
      "service_id": 8464,
      "display_name": "Instagram Likes"
    },
    "tiktoklikes": {
      "service_id": 9001,
      "display_name": "TikTok Likes"
    },
    "tiktokfollowers": {
      "service_id": 9129,
      "display_name": "TikTok Followers"
    }
  }
}
```
- The key (e.g., `iglikes`) becomes the command name: `!iglikes`
- `service_id` is the ID from your panel/API
- `display_name` is shown in the confirmation embed and help

### 4. Run the Bot
```
python main.py
```

## Usage
- Only the owner (set in `config.json`) can use the commands.
- Use `!help` in your server to see all available service commands.
- Example: `!iglikes <link> <amount>`

## Adding More Services
Just add new entries to `serviceconfig.json` under `services` and restart the bot.

## Disclaimer
This project is no longer updated or maintained. Use at your own risk. The author is not responsible for any issues, damages, or consequences resulting from the use of this bot.