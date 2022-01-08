import re
import urllib.parse

from . import card
from .scraper import make_finder, peel
from .text_utils import shadowing, letters_only
from .card import Card, get_guid, ensure_guid_uniqueness, card_cleaner


def get_link(search_word, language_from='deutsch', language_to='polnisch'):
    return f"https://de.pons.com/%C3%BCbersetzung/{language_from}-{language_to}/{urllib.parse.quote(search_word)}"


def get_cards(soup, replacement='*', pprint=lambda *args, **kwargs: None):
    """
    parses pons.de webpage, returns List[api.Card]
    replacement - used for text_utils.shadowing
    pprint - printing function, default - no printing
    """
    all_cards = []
    
    for my_result in soup.find_all(make_finder('div', 'class', 'results')):
        for entry in my_result.find_all(make_finder('div', 'class', 'entry')):

            # Here a new card begins. (One entry can produce multiple cards.)
            for rom in entry.find_all(make_finder('div', 'class', 'rom')):
                # skipping seealso rows that are usually hidden
                if 'seealso' in rom.parent.attrs['class']:
                    continue

                # prepare stuff for a new card, so nth is left from the previous iteration
                this_guid = get_guid()
                this_question = ''
                this_answer = []
                this_definition = ''
                this_prompts = []
                this_media = None

                this_question = get_question(rom)
                pprint('Q:', this_question)

                # looking for answers := (definition, [prompt1, ...])
                for translation in rom.find_all(make_finder('div', 'class', 'translations')):
                    definition, shadow_word = get_definition_and_shadow_word(translation)
                    
                    if len(definition) > 0:
                        this_answer.append((this_definition, this_prompts))
                        this_definition = definition
                        this_prompts = []
                        pprint('\tD:', definition)

                    # looking for prompts
                    for dl in translation.find_all('dl'):
                        # TODO: media can be retrieved from dl. 
                    
                        src, trgt = source_and_target(dl, shadow_word if len(shadow_word)>0 else this_question.split('<')[0], replacement)
                        # source was same as definition -> target is an alternative definiton
                        if src.strip() == replacement:
                            this_answer.append((this_definition, this_prompts))
                            this_definition = trgt
                            this_prompts = []
                            pprint('\tD:', trgt)
                        else:
                            prompt = f"{src} - {trgt}"
                            this_prompts.append(prompt)
                            pprint('\t\tp:', prompt)

                    this_answer.append((this_definition, this_prompts))
                    this_definition = ''
                    this_prompts = []
                    pprint(": : : : :")

                all_cards.append(Card(this_guid, this_question, this_answer, this_media))
                pprint("^ ^ ^ ^ \n")
    
    ensure_guid_uniqueness(all_cards)
    all_cards = [card_cleaner(c) for c in all_cards]
    return all_cards


def add_genus(h2, word):
    """pons.de h2 is parsed to join (der, die, das)"""   
    genus = h2.find_all(make_finder('span', 'class', 'genus'))
    # some nouns don't have genus given
    if len(genus) != 0:
        try:
            genus = peel(genus)
            genus = [genus.text.strip(), ]
        except AssertionError:
            # some words can be both masculine and feminine
            if len(genus) != 2:
                raise AssertionError
            genus = [g.text.strip() for g in genus]
            # TODO: currently it works only if the alternative is feminine
            feminine = h2.find_all(make_finder('span', 'class', 'feminine'))
            word = f"{word}{''.join([f.text.strip() for f in feminine])}"
            
        def derdiedas(g):
            if 'm' in g:
                return 'der'
            elif 'f' in g:
                return 'die'
            elif 'nt' in g:
                return 'das'
            else:
                print(f"Weird genus: {g}")
                return '???'
            
        geni = [derdiedas(g) for g in genus]
        word = f"{'/'.join(geni)} {word}"
    return word


def question_description(text):
    """plural form of nouns and irregular declination of verbs are hidden in <...>"""
    pl_pattern = re.compile("<.+>")
    desc = pl_pattern.search(text)
    if desc is not None:
        return desc.group(0)
    else:
        return ''


def get_question(rom):
    """pons.de h2 is parsed to create a nice question"""
    h2 = rom.find_all('h2')
    h2 = peel(h2)
    
    # span with roman capitals at the beginning
    if 1 == len(h2.find_all(make_finder('span', 'class', 'roman'))):
        # removing ^1, ^2 ... (ex. albern)
        _ = [s.replace_with("") for s in h2.find_all('sup')]

        word = h2.text.split('\n')[-1].split(' ')[0]
        word_info = ''.join(h2.text.split('\n')[-1].split(' ')[1:])
    else:
        headword_attr = h2.find_all(make_finder('span', 'class', 'headword_attributes'))
        if len(headword_attr)>0:
            word = peel(headword_attr).text
        else:
            word = h2.contents[0]
        
        word_info = ''.join([el if isinstance(el, str) else el.text for el in h2.contents[1:]])

    word = word.replace('\n', '').strip(' *')
    word_info = re.sub('\s', ' ', word_info)

    # plural form and irregular verbs info
    word_desc = question_description(word_info)

    # if wordclass == 'SUBST' then we look for genus
    wordclass = h2.find_all(make_finder('span', 'class', 'wordclass'))
    wordclass = ' '.join([w.text.strip() for w in wordclass])
    if wordclass == 'SUBST':
        word = add_genus(h2, word)

    question = ' '.join([word, word_desc])
    return question



def get_definition_and_shadow_word(translation):
    """pons.de translation->h3 usually is: `[shadow_word] ([definition])` where shadow_word is the search word or a similar term"""
    h3 = translation.find_all('h3')
    h3 = peel(h3)

    # sometimes the element, where the definition should be, is empty
    if make_finder('h3', 'class', 'empty')(h3) and make_finder('h3', 'class', 'hidden')(h3):
        # pprint("EMPTY HIDDEN")
        definition = ''
        shadow_word = ''
    else:
        if len(h3.contents) > 1:
            shadow_word, w2 = get_definition_and_description(h3)
            definition = ' '.join([shadow_word, w2])
        else:
            try:
                shadow_word = h3.contents[0].strip().split(' ')[1]
            except IndexError:
                shadow_word = h3.contents[0].strip().split(' ')[0]
            definition = letters_only(shadow_word)

    definition = shadowing(definition, shadow_word, replacement='')
    return definition, shadow_word


def get_definition_and_description(h3):
    """pons.de h3 is parsed to get definition"""
    
    # this usually is the word that is searched for
    ans =  h3.contents[0].strip().split(' ')[-1]

    # this usually is the translation
    desc = h3.find_all(make_finder('span', 'class', 'sense'))
    if len(desc) == 0:
        desc = ''
    else:
        desc = ''.join([d.text for d in desc])
    
    ans, desc = letters_only(ans), desc.strip('()')
    return ans, desc


def source_and_target(dl, shadow_word, replacement):
    """pons.de dl is parsed to get prompt := (source, target)"""
    source = dl.find_all(make_finder('div', 'class', 'source'))
    source = peel(source)
    src = pretty_prompt(source)
    src = shadowing(src, shadow_word, replacement=replacement)

    target = dl.find_all(make_finder('div', 'class', 'target'))
    target = peel(target)
    trgt = pretty_prompt(target)
    return src, trgt


def pretty_prompt(tag):
    """pons.de dl beatufier (dl is a tag that stores prompts)"""
    # spans with unwanted info are erased
    bad_spans = tag.find_all('span')
    if len(bad_spans)>0:
        _ = [b.replace_with("") for b in bad_spans
             if 'example' not in b.attrs['class'] and 'idiom_proverb' not in b.attrs['class']]
    
    # rest is just slightly cleaned
    text = tag.text.strip()
    text = re.sub('\n', ' ', text)  # usuń entery
    text = re.sub(' +', ' ', text)  # wyrównaj spacje
    return text
