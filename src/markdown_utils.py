import os
import os.path as osp
import re
from collections import namedtuple


re_guid = "^guid:"
re_header = "^#[^#]"
re_definition = "^-"
re_nonempty = "\S"


def get_card_paths(deck_path):
    # return paths to all *.md files in deck_path
    return [osp.join(deck_path, f) 
            for f in os.listdir(deck_path)
            if 'md' in f and osp.isfile(osp.join(deck_path, f))]


def find_first_match(lista, regex):
    # it's like list.index() but with regex
    regex = re.compile(regex)
    
    for i, item in enumerate(lista):
        if re.search(regex, item):
            return i


# guid is a unique card identifier
CardContent = namedtuple('CardContent', ['guid', 'question', 'answers', 'media'])

def parse_markdown_files(files):
    # returns list of CardContent objects
    cards = []
    for file in files:
        with open(file, 'r') as f:
            content = f.readlines()

        guid = find_first_match(content, re_guid)
        guid = content[guid][5:].strip() if guid is not None else guid
        header = find_first_match(content, re_header)

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

        cards.append(CardContent(guid, content[header][1:].strip(), answers, None))
        
    return cards