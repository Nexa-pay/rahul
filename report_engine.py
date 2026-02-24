“””
Report Engine - Executes reports using multiple accounts simultaneously
“””

import asyncio
import logging
from typing import Dict, List, Optional
from telethon import TelegramClient
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
InputReportReasonSpam,
InputReportReasonViolence,
InputReportReasonPornography,
InputReportReasonChildAbuse,
InputReportReasonOther,
InputReportReasonCopyright,
InputReportReasonGeoIrrelevant,
InputReportReasonFake,
InputReportReasonIllegalDrugs,
InputReportReasonPersonalDetails,
)
from config import Config

logger = logging.getLogger(**name**)
config = Config()

# Map report type strings to Telethon reason objects

REPORT_REASONS = {
“spam”: InputReportReasonSpam(),
“violence”: InputReportReasonViolence(),
“pornography”: InputReportReasonPornography(),
“child_abuse”: InputReportReasonChildAbuse(),
“copyright”: InputReportReasonCopyright(),
“personal_data”: InputReportReasonPersonalDetails(),
“illegal_goods”: InputReportReasonIllegalDrugs(),
“illegal_adult”: InputReportReasonPornography(),
“non_consensual”: InputReportReasonPornography(),
“animal_abuse”: InputReportReasonOther(),
“scam_fraud”: InputReportReasonFake(),
“other”: InputReportReasonOther(),
“custom”: InputReportReasonOther(),
}

# Auto-generated report texts per type

AUTO_REPORT_TEXTS = {
“spam”: “This channel/group is sending massive amounts of spam messages and unsolicited advertisements to users.”,
“violence”: “This channel/group contains graphic violent content including threats, physical harm, and disturbing imagery.”,
“pornography”: “Dear Telegram Support Team, I am reporting a Telegram group that is involved in serious illegal activities. This channel is sharing pornographic content in violation of Telegram’s terms of service.”,
“child_abuse”: “URGENT: This channel is distributing child abuse material (CSAM). Immediate action is required to protect minors.”,
“copyright”: “This channel is sharing copyrighted content without permission, including films, music, software, and other protected materials.”,
“personal_data”: “This channel is illegally sharing private personal data, including phone numbers, addresses, and financial information of individuals.”,
“illegal_goods”: “This channel is facilitating the sale of illegal goods and controlled substances in violation of Telegram’s terms of service and applicable laws.”,
“illegal_adult”: “This channel contains illegal adult content that violates Telegram’s terms of service and local laws.”,
“non_consensual”: “This channel is distributing non-consensual sexual imagery (revenge porn) which is illegal in most jurisdictions.”,
“animal_abuse”: “This channel contains content showing animal cruelty and abuse, which is illegal in most jurisdictions.”,
“scam_fraud”: “This channel is operating a scam/fraud scheme, deceiving users and stealing money through false promises.”,
“other”: “This channel is violating Telegram’s Terms of Service and community guidelines.”,
“custom”: “”,
}

def clean_target(target: str) -> str:
“”“Clean and normalize target username/link”””
target = target.strip()
for prefix in [“https://t.me/”, “http://t.me/”, “t.me/”, “@”]:
if target.startswith(prefix):
target = target[len(prefix):]
target = target.split(”/”)[0].split(”?”)[0]
return target

class ReportEngine:
def **init**(self, db, account_manager):
self.db = db
self.account_manager = account_manager

```
def get_report_text(self, report_type: str, custom_text: str, target: str) -> str:
    """Generate appropriate report text"""
    # Check if admin has set custom text
    admin_text = self.db.get_setting('report_text')
    if admin_text:
        return admin_text.replace("{target}", target)

    if report_type == "custom" and custom_text:
        return custom_text

    return AUTO_REPORT_TEXTS.get(report_type, AUTO_REPORT_TEXTS["other"])

async def report_with_account(self, session_string: str, target: str, report_type: str, message: str) -> bool:
    """Report target using a single account"""
    client = None
    try:
        client = await self.account_manager.get_client(session_string)
        if not client:
            return False

        entity = await client.get_entity(target)
        reason = REPORT_REASONS.get(report_type, InputReportReasonOther())

        await client(ReportPeerRequest(
            peer=entity,
            reason=reason,
            message=message
        ))
        return True

    except Exception as e:
        logger.warning(f"Report failed for {target}: {e}")
        return False
    finally:
        if client:
            try:
                await client.disconnect()
            except:
                pass

async def run_reports(
    self,
    user_id: int,
    target: str,
    report_type: str,
    custom_text: str,
    count: int,
    accounts: List[Dict]
) -> Dict:
    """Run reports simultaneously across all accounts"""
    clean = clean_target(target)
    message = self.get_report_text(report_type, custom_text, clean)

    # Build task list: distribute count across accounts
    tasks = []
    account_cycle = accounts * (count // len(accounts) + 1)
    selected = account_cycle[:count]

    for acc in selected:
        tasks.append(
            self.report_with_account(
                acc['session_string'],
                clean,
                report_type,
                message
            )
        )

    # Run all concurrently with semaphore to avoid flooding
    semaphore = asyncio.Semaphore(10)

    async def sem_task(t):
        async with semaphore:
            return await t

    results = await asyncio.gather(*[sem_task(t) for t in tasks], return_exceptions=True)

    success = sum(1 for r in results if r is True)
    failed = len(results) - success

    # Save to DB
    self.db.save_report(user_id, clean, report_type, custom_text, count, success, failed)

    # Update account stats
    for acc in accounts:
        self.db.save_account_report(acc['id'], 1)

    return {'success': success, 'failed': failed, 'total': len(results)}
```