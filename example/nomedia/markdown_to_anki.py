import sys
import os.path as osp
sys.path.append(osp.join(osp.dirname(osp.realpath(__file__)), '..', '..'))

import argparse
import genanki.genanki as genanki
from twostep_genanki.markdown_utils import get_card_paths, parse_from_markdown
from twostep_genanki.deck import load_deck_properties, reversed_model_no_media, get_deck, populate_deck

parser = argparse.ArgumentParser(description='Parse markdown files to Anki deck.')
parser.add_argument('deck_properties', type=str, help='path to file with deck properties')
args = parser.parse_args()

deck_prop_dir = osp.dirname(osp.realpath(args.deck_properties))
deck_prop = load_deck_properties(args.deck_properties)

cards_paths = get_card_paths(osp.join(deck_prop_dir, deck_prop['deck_dir']))
cards = parse_from_markdown(cards_paths)

model = reversed_model_no_media()
deck = get_deck(deck_prop['deck_name'], deck_prop['deck_id'])
notes = populate_deck(deck, cards, model, multianswer=deck_prop['multianswer'])

my_package = genanki.Package(deck)
my_package.write_to_file(osp.join(deck_prop_dir, deck_prop['apkg_name']))
