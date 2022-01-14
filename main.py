from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.properties import BooleanProperty

import re
import json
from itertools import permutations


kv = """
<LetterInput>:
    size_hint: None, None
    size: 30, 30
    write_tab: False
    on_text: app.process_text()
    input_filter: self.one_letter
    
BoxLayout:
    orientation: 'vertical'
    spacing: 5
    Label:
        text: 'Wordle Assistant'
        font_size: 30
        size_hint_y: None
        height: 48
    BoxLayout:
        size_hint_y: None
        height: 30
        Label:  # Placeholder
        BoxLayout:
            size_hint_x: None
            width: 30 * 5
            id: letters
        Label:  # Placeholder
    BoxLayout:
        size_hint_y: None
        height: 30
        Label:
            size_hint_x: .3
            text: 'Not in Word'
        UniqueLettersInput:
            id: not_in_word
            hint_text: 'Enter the letters not in the word'
            write_tab: False
            on_text: app.process_text()
            input_filter: self.unique_letters
            
    BoxLayout:
        size_hint_y: None
        height: 30
        Label:
            size_hint_x: .3
            text: 'Position Unknown'
        UniqueLettersInput:
            id: pos_unknown
            hint_text: 'Enter the letters in the word, position unknown'
            write_tab: False
            on_text: app.process_text()
            input_filter: self.unique_letters
    BoxLayout:
        size_hint_y: None
        height: 48
        Button:
            text: 'Enter'
            on_release: app.find_candidates()
            disabled: app.no_input
        Button: 
            text: 'Clear'
            on_release: app.clear_inputs()
    ScrollView:
        GridLayout:
            cols: 5
            id: grid
            row_default_height: 30
            size_hint_y: None
            height: self.minimum_height
"""


class LetterInput(TextInput):
    def one_letter(self, c, undo):
        return c.upper() if len(self.text) == 0 and c.isalpha() else ''


class UniqueLettersInput(TextInput):
    def unique_letters(self, c, undo):
        if not c.isalpha() or c in self.text:
            return ''
        else:
            return c.upper()


class WordleCheat(App):
    no_input = BooleanProperty(True)  # used to disable enter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words = ''

    def build(self):
        return Builder.load_string(kv)

    def on_start(self):
        # create letter inputs
        for _ in range(5):
            self.root.ids.letters.add_widget(LetterInput())

        # load words
        with open('words.json') as f:
            words = json.load(f)
        self.words = '\n'.join(words)

    def find_candidates(self):
        # create the search terms based on what is know, display candidates
        # get know letters and positions
        p = self.root.ids
        known = []
        for letter in p.letters.children[::-1]:
            if letter.text.isalpha():
                known.append(letter.text.lower())
            else:
                known.append('.')
        # letters not in the word
        if p.not_in_word.text:
            nots = '[^' + p.not_in_word.text.lower() + '\n]'
        else:
            nots = None
        # print(nots)
        # letters in word and pos unknown
        search = []
        if p.pos_unknown.text:
            pos_unknown = p.pos_unknown.text.lower()
            count = known.count('.') - len(pos_unknown)
            ss = pos_unknown + '.' * count
            # print(f'{ss=}')
            ss_permutations = permutations(ss, len(ss))
            perms = set(ss_permutations)  # remove duplicates
            # position and value of know characters
            known_poss = [(i, c) for i, c in enumerate(known) if c != '.']
            # insert known data into permuted data
            known_and_pos_unknowns = []
            for perm in perms:
                # tuple to list
                pl = list(perm)
                for k in known_poss:
                    pl.insert(k[0], k[1])
                known_and_pos_unknowns.append(pl)
            # Convert list of known and unknown chars to search string
            for term in known_and_pos_unknowns:
                search.append('(' + ''.join(term) + '\n)|')
            search = ''.join(search)[:-1]  # remove trailing |
        else:
            search = ''.join(known[::])

        if nots:
            search = search.replace('.', nots)
        # print(f'{repr(search)}')
        candidates = re.findall(search, self.words)
        # print(candidates)
        if candidates and isinstance(candidates[0], tuple):
            candidates = [e1.strip() for e in candidates for e1 in e if e1]
        self.root.ids.grid.clear_widgets()
        for word in candidates:
            self.root.ids.grid.add_widget(Label(text=word.upper()))

    def clear_inputs(self):
        p = self.root.ids
        for letter in p.letters.children:
            letter.text = ''
        p.not_in_word.text = ''
        p.pos_unknown.text = ''
        self.root.ids.grid.clear_widgets()

    def process_text(self):
        p = self.root.ids
        self.no_input = not any([w.text for w in p.letters.children] + [p.not_in_word.text] + [p.pos_unknown.text])
        # get letters from input
        letters = [w.text for w in p.letters.children]
        # if letter is in a known position remove from pos_unknown and not_in_word
        for letter in letters:
            if letter in p.pos_unknown.text:
                p.pos_unknown.text = p.pos_unknown.text.replace(letter, '')
            if letter in p.not_in_word.text:
                p.not_in_word.text = p.not_in_word.text.replace(letter, '')
        # if letter is in pos_known remove from not_in_word
        for letter in p.pos_unknown.text:
            if letter in p.not_in_word.text:
                p.not_in_word.text = p.not_in_word.text.replace(letter, '')


WordleCheat().run()
