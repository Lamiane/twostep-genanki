import sys
import os.path as osp
sys.path.append(osp.join(osp.dirname(osp.realpath(__file__)), '..', '..'))

import argparse
from twostep_genanki.scraper import scrap
from twostep_genanki.deck import load_deck_definition
from twostep_genanki.markdown_utils import save_as_markdown

parser = argparse.ArgumentParser(description='Scrap words to markdown.')
parser.add_argument('wordfile', type=str, help='path to file with words')
args = parser.parse_args()

wordfile_dir = osp.dirname(osp.realpath(args.wordfile))
wordfile = load_deck_definition(args.wordfile)

cards = scrap(words=wordfile['words'], scraper=wordfile['scraper'],
              language_from=wordfile['language_from'],
              language_to=wordfile['language_to'])

save_as_markdown(cards, directory=osp.join(wordfile_dir, wordfile['save_dir']), tags=wordfile['tags'])
