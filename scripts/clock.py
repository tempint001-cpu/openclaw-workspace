#!/usr/bin/env python3
from datetime import datetime
import pytz

def get_nemesis_time():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    return {
        'iso': now.isoformat(),
        'time': now.strftime('%H:%M'),
        'date': now.strftime('%Y-%m-%d'),
        'day': now.strftime('%A'),
        'hour': now.hour,
        'minute': now.minute,
        'is_active': 7 <= now.hour <= 23,
        'is_sleeping': now.hour < 7 or now.hour >= 23
    }

if __name__ == "__main__":
    t = get_nemesis_time()
    print(f"{t['day']} {t['date']} {t['time']} IST")
    print(f"Active hours: {t['is_active']}")
