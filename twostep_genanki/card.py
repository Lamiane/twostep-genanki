from time import time
from collections import namedtuple

# Card is a common API for:
# - output of web scrapers
# - input for markdown creation
# - output of markdown parsing
# - input for Anki deck creation

# guid is a unique card identifier
# a single answer is (definition, [prompt1, prompt2...])
Card = namedtuple('Card', ['guid', 'question', 'answers', 'media'])


def get_guid():
    """lots of digits likely unique"""
    return str(time()).replace('.', '')


def ensure_guid_uniqueness(cards):
    guids = [c.guid for c in cards]
    assert len(guids) == len(set(guids)), "guids are not unique but really should be."    

    
def card_cleaner(card):
    """remove empty definitions"""
    clean_answers = []
    for answer in card.answers:
        definition, prompts = answer
        if len(definition) + len(prompts) > 0:
            clean_answers.append(answer)
    return Card(card.guid, card.question, clean_answers, card.media)


def card_printer(card):
    print(f"G: {card.guid}")
    print(f"Q: {card.question}")
    for answer in card.answers:
        definition, prompts = answer
        print(f"\tD: {definition}")
        [print(f"\t\tp: {p}") for p in prompts]
    print()
