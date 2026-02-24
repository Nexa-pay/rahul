“””
Account Manager - Manages Telegram user accounts via Telethon
“””

import logging
import os
from typing import Dict, Optional
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
SessionPasswordNeededError,
PhoneCodeInvalidError,
PhoneCodeExpiredError,
PasswordHashInvalidError
)
from config import Config

logger = logging.getLogger(**name**)
config = Config()

# Store pending clients waiting for code verification

_pending_clients: Dict[str, TelegramClient] = {}

class AccountManager:
def **init**(self, db):
self.db = db

```
async def send_code(self, phone: str, user_id: int) -> Dict:
    """Send verification code to phone number"""
    try:
        client = TelegramClient(StringSession(), config.API_ID, config.API_HASH)
        await client.connect()
        result = await client.send_code_request(phone)
        _pending_clients[phone] = client
        return {
            'success': True,
            'phone_code_hash': result.phone_code_hash
        }
    except Exception as e:
        logger.error(f"Send code error: {e}")
        return {'success': False, 'error': str(e)}

async def verify_code(self, phone: str, code: str, phone_code_hash: str, user_id: int) -> Dict:
    """Verify the received code"""
    client = _pending_clients.get(phone)
    if not client:
        return {'success': False, 'error': 'Session expired. Try again.'}

    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        session_string = client.session.save()
        self.db.save_account(user_id, phone, session_string)
        await client.disconnect()
        _pending_clients.pop(phone, None)
        return {'success': True}
    except SessionPasswordNeededError:
        return {'success': False, 'need_password': True}
    except (PhoneCodeInvalidError, PhoneCodeExpiredError) as e:
        return {'success': False, 'error': 'Invalid or expired code.'}
    except Exception as e:
        logger.error(f"Verify code error: {e}")
        return {'success': False, 'error': str(e)}

async def verify_password(self, phone: str, password: str, user_id: int) -> Dict:
    """Verify 2FA password"""
    client = _pending_clients.get(phone)
    if not client:
        return {'success': False, 'error': 'Session expired. Try again.'}

    try:
        await client.sign_in(password=password)
        session_string = client.session.save()
        self.db.save_account(user_id, phone, session_string)
        await client.disconnect()
        _pending_clients.pop(phone, None)
        return {'success': True}
    except PasswordHashInvalidError:
        return {'success': False, 'error': 'Wrong password.'}
    except Exception as e:
        logger.error(f"Password verify error: {e}")
        return {'success': False, 'error': str(e)}

async def get_client(self, session_string: str) -> Optional[TelegramClient]:
    """Get an active Telethon client from session string"""
    try:
        client = TelegramClient(StringSession(session_string), config.API_ID, config.API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            return None
        return client
    except Exception as e:
        logger.error(f"Client creation error: {e}")
        return None
```
