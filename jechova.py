from argparse import ArgumentParser
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
    parser = ArgumentParser()
    parser.add_argument('--force', '-f', action='store_true')
    parser.add_argument('channel')
    parser.add_argument('pyvo_slug')
    args = parser.parse_args()

    if '/' in args.pyvo_slug:
        # Deprecated: We accept an ICS URL instead of just a slug
        ics_url = args.pyvo_slug
        web_url = None
    else:
        ics_url = f'https://pyvo.cz/api/series/{args.pyvo_slug}.ics'
        web_url = f'https://pyvo.cz/{args.pyvo_slug}/'

    response = requests.get(ics_url)
    response.raise_for_status()
    calendar = Calendar(response.text)

    today = arrow.now('Europe/Prague')
    event = min((e for e in calendar.events if e.begin > today),
                key=attrgetter('begin'))
    remaining_days = (event.begin - today).days

    if not args.force and remaining_days not in NOTIFY_WHEN_REMAINING_DAYS:
        print('Dní do dalšího srazu:', remaining_days)
        print('Ozývám se, když zbývá:',
              ', '.join(map(str, NOTIFY_WHEN_REMAINING_DAYS)))
        sys.exit()

    if 'tentative-date' not in event.categories:
        print("Zdá se, že příští sraz je naplánovaný!")
        sys.exit()

    channel = '#' + args.channel.lstrip('#')
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])
    if web_url:
        client.chat_postMessage(channel=channel, text=dedent(f'''
            Máte téma? A mohla bych ho vidět? :eyes:\n\n
            Pokud už tušíte, o čem Pyvo bude, přidejte to na pyvo.cz — nejlépe
            přes tlačítko _přidat informace o dalším srazu_ na <{web_url}>.

            (Existuje i <https://docs.pyvec.org/guides/meetup.html#informace-na-pyvo-cz|podrobnější návod>.)
        ''').strip())
    else:
        client.chat_postMessage(channel=channel, text=dedent('''
            Máte téma? A mohla bych ho vidět? :eyes:\n\n
            Pokud už tušíte, o čem Pyvo bude, přidejte to na pyvo.cz — může
            to udělat kdokoliv, v 5 jednoduchých krocích:
            https://docs.pyvec.org/guides/meetup.html#informace-na-pyvo-cz
        ''').strip())
