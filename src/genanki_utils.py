import random
import genanki.genanki as genanki

basic_fields = [{'name': 'Front', 'font': 'serif'},
                {'name': 'Back', 'font': 'serif'}
               ]

CSS = '.card {\n font-family: serif;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n'


def get_reversed_model_no_media(model_id=None):
    if model_id is None:
        model_id = random.randrange(1 << 30, 1 << 31)

    model = genanki.Model(
        model_id,
        'Basic (and reversed card) (genanki)',
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


def get_reversed_model_with_media(model_id=None):
    if model_id is None:
        model_id = random.randrange(1 << 30, 1 << 31)

    model = genanki.Model(
        model_id,
        'Basic (and reversed card) (genanki)',
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
    if deck_id is None:
        deck_id = random.randrange(1 << 30, 1 << 31)

    return genanki.Deck(deck_id, deck_name)


def make_italic(lista):
    return [f"<i>{l}</i>" for l in lista]


def answer_layout(answer_content, i=None):
    # use HTML tags to make the answer look pretty
    definition, prompts = answer_content
    definition = f"<br>{i}. {definition}" if i is not None else f"<br>{definition}"
    
    if len(prompts) == 0:
        return definition
    else:
        return '<br>'.join([definition,] + make_italic(prompts))
    
    
def populate_deck(deck, cards, model, multianswer=True):
    for card in cards:
        if len(card.answers) > 1:
            answers = [answer_layout(c, i) for i, c in enumerate(card.answers, start=1)]
        else:
            answers = [answer_layout(c) for c in card.answers]

        if multianswer:
            note = genanki.Note(guid=card.guid, model=model, fields=[card.question, '<br>'.join(answers)])
            deck.add_note(note)
        else:
            #TODO: guid must be unique for each Note, we need sth smarter here
            [deck.add_note(genanki.Note(model=model, fields=[card.question, ans])) for ans in answers]
    
    # I guess, deck does not need to be returned but this is prettier
    return deck
