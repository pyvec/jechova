# Jechová

Checks whether the next meetup is announced on [pyvo.cz](https://pyvo.cz/). If not, sends a message to the specified Slack channel to remind about the situation and provide a link to documentation on how anyone can fix it.

## Usage

1. [Create a Slack app](https://api.slack.com/apps?new_app=1).
1. Add scopes allowing the app to write to Slack channels (`chat:write`, `chat:write.public`).
1. Create a bot user for the app so it can act independently.
1. Install the app for your workspace.
1. Find the bot token (starts with `xoxb-`) and set it as an environment variable before running the script:

```bash
$ export SLACK_API_TOKEN=...
$ python jechova.py '#pyvo-praha' https://pyvo.cz/api/series/praha-pyvo.ics
```

First argument is a channel name where the message should go. Beware, if you specify it as `#pyvo-praha`, standard shell interprets the `#` as a start of a comment and will ignore the rest of the line. You must pass it either as `pyvo-praha` or as `'#pyvo-praha'` (both works).

Second argument is the source ics feed for the Pyvo meetup you want to watch. Each meetup tracked on pyvo.cz has the ics feed automatically generated, you can find a link somewhere on the meetup page (e.g. somewhere on [pyvo.cz/praha-pyvo](https://pyvo.cz/praha-pyvo/)).

When debugging, force sending of the message by adding `-f`. (And use `#automatizace` or other less populated channel.)

## Deployment

The script is deployed as a [daily GitHub Action](https://github.com/pyvec/jechova/actions). `SLACK_API_TOKEN` needs to be [set as a secret](https://github.com/pyvec/jechova/settings/secrets). If you want Jechová to handle meetup in your town as well, just [add a new workflow](https://github.com/pyvec/jechova/tree/master/.github/workflows).

## Dependencies and CI

[@dependabot](https://dependabot.com/) is set up to automatically upgrade dependencies on the repo. It won't automerge PRs if there are no checks though, so there's also a [default build as a GitHub Action](https://github.com/pyvec/jechova/blob/master/.github/workflows/build.yml), currently only consisting of a linter check.

There are no tests. If the code breaks, we'll know when it crashes during the daily cron build.
