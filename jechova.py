from argparse import ArgumentParser
import os
import sys
from operator import attrgetter

import arrow
from ics import Calendar
import requests
from slack import WebClient


# Only send a message when the number of remaining days is a key here.
# Values are emoji names; they should be more urgent for smaller numbers.
NOTIFY_WHEN_REMAINING_DAYS = {
    3: 'panicmonster',
    7: 'hourglass_flowing_sand',
    14: 'eyes'
}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--force', '-f', action='store_true')
    parser.add_argument('--today', metavar='YYYY-MM-DD',
                        help="Override current date (for testing)")
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

    if args.today:
        today = arrow.get(args.today)
    else:
        today = arrow.now('Europe/Prague')
    event = min((e for e in calendar.events if e.begin > today),
                key=attrgetter('begin'))
    remaining_days = (event.begin - today).days

    if not args.force and remaining_days not in NOTIFY_WHEN_REMAINING_DAYS:
        print('Dní do dalšího srazu:', remaining_days)
        print('Ozývám se, když zbývá:',
              ', '.join(map(str, NOTIFY_WHEN_REMAINING_DAYS)))
        sys.exit()

    for days, emoji in sorted(NOTIFY_WHEN_REMAINING_DAYS.items()):
        if remaining_days <= days:
            break
        # nb. `emoji` keeps the value from the last iteration of this loop

    if 'tentative-date' not in event.categories:
        print("Zdá se, že příští sraz je naplánovaný!")
        sys.exit()

    channel = '#' + args.channel.lstrip('#')
    client = WebClient(token=os.environ['SLACK_API_TOKEN'])

    docs_url = "https://docs.pyvec.org/guides/meetup.html#informace-na-pyvo-cz"
    web_url = f'https://pyvo.cz/{args.pyvo_slug}/'

    if remaining_days < 0:
        remaining_msg = 'Pyvo už bylo!'
    elif remaining_days == 0:
        remaining_msg = 'Pyvo je dnes!'
    elif remaining_days == 1:
        remaining_msg = 'Zbývá poslední den!'
    elif remaining_days < 5:
        remaining_msg = f'Zbývají {remaining_days} dny'
    else:
        remaining_msg = f'Zbývá {remaining_days} dní'

    client.chat_postMessage(channel=channel, text=' '.join((
        f'Máte téma? A mohla bych ho vidět? {remaining_msg} :{emoji}:\n',
        'Pokud už tušíte, o čem Pyvo bude, přidejte to na pyvo.cz',
        'přes odkaz _přidat informace o dalším srazu_ na',
        f'<{web_url}|pyvo.cz/{args.pyvo_slug}>.\n',
        '(Složitější případy řešte v <#C97Q9HHHT>)',  # links to #pyvo channel
    )))
