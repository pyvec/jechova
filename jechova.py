from argparse import ArgumentParser
import os
import sys
from operator import attrgetter

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
        raise ValueError(
            "Meetup slug cannot contain slashes. See the README for usage."
        )

    response = requests.get(f'https://pyvo.cz/api/series/{args.pyvo_slug}.ics')
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

    docs_url = "https://docs.pyvec.org/guides/meetup.html#informace-na-pyvo-cz"
    web_url = f'https://pyvo.cz/{args.pyvo_slug}/'
    client.chat_postMessage(channel=channel, text=' '.join((
        'Máte téma? A mohla bych ho vidět? :eyes:\n',
        'Pokud už tušíte, o čem Pyvo bude, přidejte to na pyvo.cz',
        'přes odkaz _přidat informace o dalším srazu_ na',
        f'<{web_url}|pyvo.cz/{args.pyvo_slug}>.\n',
        '(Složitější případy řešte v <#C97Q9HHHT>)',
    )))
