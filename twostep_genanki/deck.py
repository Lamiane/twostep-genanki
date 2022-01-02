import html
import random
from distutils.util import strtobool

try:
    import genanki.genanki as genanki
except ModuleNotFoundError:
    import genanki

from .builtin_scrapers import SCRAPERS

basic_fields = [{'name': 'Front', 'font': 'serif'},
                {'name': 'Back', 'font': 'serif'}
               ]

CSS = '.card {\n font-family: serif;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n list-style-position: inside;\n}\n'


def reversed_model_no_media():
    model = genanki.Model(
        1795872692,
        'Basic (and reversed card) (genanki-markdown)',
        fields=basic_fields,
        templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
        },
        {
            'name': 'Card 2',
            'qfmt': '{{Back}}',
            'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}',
        },
        ],
        css=CSS,
    )
    return model


def reversed_model_with_media():
    model = genanki.Model(
        1875624546,
        'Basic (and reversed card) with media (genanki-markdown)',
        fields=basic_fields + [{'name': 'MyMedia'},],
        templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}<br>{{MyMedia}}',
        },
        {
            'name': 'Card 2',
            'qfmt': '{{Back}}<br>{{MyMedia}}',
            'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}',
        },
        ],
        css=CSS,
    )
    return model


def get_deck(deck_name, deck_id=None):
    """creates a new deck with deck_id"""
    if deck_id is None:
        deck_id = random.randrange(1 << 30, 1 << 31)

    return genanki.Deck(deck_id, deck_name)


def load_deck_definition(path):
    """Loads word-list file, such as example/german_words.txt"""
    with open(path, 'r') as f:
        lines = f.readlines()
        
    content = {}
    for i, line in enumerate(lines):
        if ':' not in line:
            break
        key, value = line.split(':')
        content[key.strip()] = value.strip()
        
    content['scraper'] = SCRAPERS[content['scraper']]
    content['words'] = [w.strip() for w in lines[i:] if len(w.strip())>0]
    
    return content


def load_deck_properties(path):
    """Loads a deck properties file, such as example/german_deck.conf"""
    with open(path, 'r') as f:
        lines = f.readlines()
        
    content = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':')
            content[key.strip()] = value.strip()
        
    content['deck_id'] = int(content['deck_id'])
    content['multianswer'] = True if strtobool(content['multianswer'])==1 else False
    return content


def populate_deck(deck, cards, model, multianswer=True):
    """
    populate deck with cards as genanki.Notes that follow model
    if multianswer==True all answers are on a single card
    otherwise a new card for each answer is created
    """
    for card in cards:
        question = question_layout(card.question)
        if len(card.answers) > 1:
            answers = [answer_layout(c, i) for i, c in enumerate(card.answers, start=1)]
        else:
            answers = [answer_layout(c) for c in card.answers]

        if multianswer:
            note = genanki.Note(guid=card.guid, model=model, fields=[question, '<br>'.join(answers)])
            deck.add_note(note)
        else:
            #TODO: guid must be unique for each Note, we need sth smarter here
            [deck.add_note(genanki.Note(model=model, fields=[question, ans])) for ans in answers]
    
    # I guess, deck does not need to be returned but this is prettier
    return deck


def make_italic(lista):
    return [f"<i>{l}</i>" for l in lista]


def question_layout(question_content):
    """not much happenning here at this point"""
    return html.escape(question_content)


def answer_layout(answer_content, i=None):
    """use HTML tags to make the answer look pretty"""
    definition, prompts = answer_content
    if definition is not None:
        definition = html.escape(definition)
    definition = f"<br>{i}. {definition}" if i is not None else f"<br>{definition}"
    
    if len(prompts) == 0:
        return definition
    else:
        prompts = [html.escape(p) for p in prompts]
        prompt_list = f"<ul><li>{'</li><li>'.join(make_italic(prompts))}</li></ul>"
        return '<br>'.join([definition, prompt_list])
