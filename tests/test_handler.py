import json

import arrow
from pyticket import handler

with open('config.json', 'r') as f:
    config = json.load(f)


def test_scrape():
    html_string = handler.Scrape.scrape(config['site']['url'])
    next_game_date_string = html_string[0].strip('<p>\t')
    next_game_datetime = arrow.get(next_game_date_string, 'DD MMMM YYYY, HH:mm', locale='ru')
    assert type(next_game_datetime) is arrow.arrow.Arrow
