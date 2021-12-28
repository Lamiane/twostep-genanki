import sys
sys.path.append('/home/pocha/projects')

import os.path as osp
import genanki.genanki as genanki
from markdown_utils import get_card_paths, parse_markdown_files
from genanki_utils import get_reversed_model_no_media, get_deck, populate_deck

multianswer = True

deck_path = osp.join('..', 'deck')
cards = get_card_paths(deck_path)
cards = parse_markdown_files(cards)

model = get_reversed_model_no_media()
deck = get_deck('Example')
notes = populate_deck(deck, cards, model, multianswer=multianswer)

my_package = genanki.Package(deck)
my_package.write_to_file('output.apkg')
