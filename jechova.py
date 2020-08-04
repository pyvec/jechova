import os
import sys
from operator import attrgetter
from textwrap import dedent

import arrow
from ics import Calendar
import requests
from slack import WebClient


NOTIFY_WHEN_REMAINING_DAYS = (14, 7, 3)


if __name__ == '__main__':
    force = '-f' in sys.argv
    channel = sys.argv[1].lstrip('#')
    ics_url = sys.argv[2]

    response = requests.get(ics_url)
    response.raise_for_status()
    calendar = Calendar(response.text)

    today = arrow.now('Europe/Prague')
    event = min((e for e in calendar.events if e.begin > today),
                key=attrgetter('begin'))
    remaining_days = (event.begin - today).days

    if not force and remaining_days not in NOTIFY_WHEN_REMAINING_DAYS:
        print(f'Dní do dalšího srazu:', remaining_days)
        print(f'Ozývám se, když zbývá:', ', '.join(map(str, NOTIFY_WHEN_REMAINING_DAYS)))        
        sys.exit()

    if 'tentative-date' not in event.categories:
        print("Zdá se, že příští sraz je naplánovaný!")
        sys.exit()

    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    client.chat_postMessage(channel=f'#{channel}', text=dedent('''
        Máte téma? A mohla bych ho vidět? :eyes:\n\n
        Pokud už tušíte, o čem Pyvo bude, přidejte to na pyvo.cz — může
        to udělat kdokoliv, v 5 jednoduchých krocích:
        https://docs.pyvec.org/guides/meetup.html#informace-na-pyvo-cz
    ''').strip())
