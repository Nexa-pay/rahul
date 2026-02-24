“””
Configuration - credentials filled in, ready to deploy
“””

class Config:

```
# Bot Token
BOT_TOKEN: str = "8361863948:AAEbIgDTTxViZYCMerKr9c3-5qeK-RO9kd4"

# Telegram API (from my.telegram.org)
API_ID: int = 37133457
API_HASH: str = "951a895d6016c9d88880f9591209dbc2"

# Owner info
OWNER_ID: int = 6950501653
OWNER_USERNAME: str = "KRUSHOVE"        # no @ symbol
SUPPORT_USERNAME: str = "l_ITS_ALONE_ll"  # no @ symbol

# Database (SQLite - works on Railway, no setup needed)
DATABASE_URL: str = "sqlite:///bot.db"

# Token settings
TOKENS_PER_REPORT: int = 1
DEFAULT_TOKENS: int = 5
```
