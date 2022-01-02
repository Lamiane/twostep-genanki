import os
import os.path as osp
import re
from tqdm import tqdm

from .card import Card
from .text_utils import letters_only

re_guid = "^guid:"
re_header = "^#[^#]"
re_definition = "^-"
re_nonempty = "\S"


def get_card_paths(directory):
    """return paths to all *.md files in directory"""
    return [osp.join(directory, f) 
            for f in os.listdir(directory)
            if 'md' in f and osp.isfile(osp.join(directory, f))]


def get_unique_filepath(card, directory):
    """
    returns: [directory]/[card.question]_[number].md
    if multiple cards have equal question, they'll get different numbers
    """
    filename = letters_only(card.question).replace(' ', '-')
    matching_files = [f for f in get_card_paths(directory) if filename in f]
    return osp.join(directory, f"{filename}-{len(matching_files)}.md")


def first_match(lista, regex):
    """it's like list.index() but with regex"""
    regex = re.compile(regex)
    
    for i, item in enumerate(lista):
        if re.search(regex, item):
            return i


def parse_to_markdown(card, tags='[anki]'):
    """uses card to create markdown code"""
    content = ['---', f'tags: {tags}', f'title: {card.question}',
               f'guid: {card.guid}','---\n', f'# {card.question}\n']
    
    answer_content = []
    for answer in card.answers:
        definition, prompts = answer
        answer_content.append(f"- {definition}")
        for prompt in prompts:
            answer_content.append(f"  {prompt}")
            
    content = '\n'.join(content+answer_content+['\n', ])
    return content


def parse_from_markdown(files):
    """for each file an api.Card is returned"""
    cards = []
    for file in files:
        with open(file, 'r') as f:
            content = f.readlines()

        guid = first_match(content, re_guid)
        guid = content[guid][5:].strip() if guid is not None else guid
        header = first_match(content, re_header)

        answers = []
        definition = None
        for line in content[1+header:]:
            # new definition starts here
            if re.search(re_definition, line):
                if definition is not None:
                    answers.append((definition, prompts))
                definition = line[1:].strip()
                prompts = []
            else:
                # a nonempty line that is not a definition is a prompt
                if re.search(re_nonempty, line):
                    prompts.append(line.strip())
        answers.append((definition, prompts))

        cards.append(Card(guid, content[header][1:].strip(), answers, None))
        
    return cards


def save_as_markdown(cards, directory, tags='[anki]'):
    # create directory if needed
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
    
    for card in tqdm(cards, desc='Saving...'):
        with open(get_unique_filepath(card, directory), 'w') as f:
            f.write(parse_to_markdown(card, tags=tags))
            
    print("Done.")
