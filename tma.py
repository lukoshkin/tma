"""
'Tell me about (tma) the word' module.
Finds the word meanings (Macmillan dictionary)
and its translations in context (Reverso Context).
"""
import textwrap as twr

from bs4 import BeautifulSoup
import requests
from termcolor import colored

from utils import highlight_words, LANG_ABBREV


class QueryParser:
    """
    Abstract base class.
    Derived class should give an idea of the word being queried.
    """
    def __init__(self, textwidth):
        self.base = ''
        self.textwidth = textwidth
        self.headers = {
                'user-agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}

    def get_request(self, query='', payload=None):
        url = f'{self.base}/{query}'
        r = requests.get(url, headers=self.headers, params=payload)
        soup = BeautifulSoup(r.text, 'html.parser')

        return soup

    def text_wrap(self, text):
        text = twr.indent(twr.fill(text, self.textwidth), '\t')
        return text


class Macmillan(QueryParser):
    """
    Fetches the word's info from Macmillan dictionary.
    """
    def __init__(self, textwidth=80):
        super().__init__(textwidth)
        self.base = 'https://www.macmillandictionary.com/dictionary/british'

    def print_definition(self, content, num):
        definition = colored(f'{num}. ', 'red')
        try:
            definition += content.find_all('span', 'DEFINITION')[0].text
            definition = self.text_wrap(definition)
            print(definition)
        except IndexError:
            print('Website error..')

    def print_example(self, content, tag, key):
        found = content.find_all(tag, key)
        if not found:
            return

        example = colored('Example: ', 'green')
        example += found[0].text
        example = self.text_wrap(example)
        print(example)
        print()

    def print_synonyms(self, content):
        # synonyms = content.find('div', 'THES')  # Thesaurus
        # synonyms = synonyms.find('div', 'hidden-closed')
        # synonyms = synonyms.find('div', 'synonyms row')

        synonyms = content.find('div', 'synonyms row')
        if synonyms is None:
            return

        synonyms = synonyms.find_all('a')
        synonyms = ', '.join([x.text for x in synonyms])
        synonyms = f"{colored('Synonyms:', 'cyan')} {synonyms}"
        synonyms = self.text_wrap(synonyms)
        print(synonyms)
        print()

    def print_other_forms(self, soup, query):
        word_forms = soup.find('div', 'wordforms')
        if word_forms is None:
            return

        word_forms = word_forms.find_all('span', 'INFLECTION-CONTENT')
        word_forms = set(x.text for x in word_forms) - {query}
        word_forms = colored(' '.join(word_forms), 'magenta')
        print(self.text_wrap(word_forms))
        print()

    def __call__(self, query: str):
        """
        Returns True if found sth, False otherwise.
        """
        soup = self.get_request(query)
        title = colored('Macmillan Dictionary:\n', 'blue')
        print(title)

        std_dict = soup.find_all('div', 'SENSE-BODY')
        open_dict = soup.find_all('div', 'openSense')

        if not std_dict:
            did_you_mean = soup.find('div', 'display-list red-links')
            if did_you_mean is not None:
                did_you_mean = did_you_mean.find_all('a')
                did_you_mean = [x.text for x in did_you_mean]
                print(
                        self.text_wrap(
                            colored('Did you mean?: ', 'red')
                            + '; '.join(did_you_mean)) + '\n')

            return False

        self.print_other_forms(soup, query)

        num = 1
        for content in std_dict:
            self.print_definition(content, num)
            self.print_example(content, 'p', 'EXAMPLE')
            self.print_synonyms(content)
            num += 1

        for content in open_dict:
            self.print_definition(content, num)
            self.print_example(content, 'div', 'openEx')
            num += 1

        print()

        return True


class ReversoContext(QueryParser):
    """
    Gives translations of the word in context.
    The info is fetched from context.reverso.net.
    """
    def __init__(self, num_examples=4, textwidth=80, lang='russian'):
        super().__init__(textwidth)
        self.base = f'https://context.reverso.net/translation/english-{lang}'
        self.num_examples = num_examples
        self.lang = LANG_ABBREV[lang]

    def highlight_words(self, soup_sen):
        sen = soup_sen.text.strip()
        ems = [x.text for x in soup_sen.find_all('em')]
        return highlight_words(sen, ems)

    def __call__(self, query: str):
        """
        Returns True if found sth, False otherwise.
        """
        soup = self.get_request(query)
        title = colored('Reverso.Context:\n', 'blue')
        print(title)

        elems = soup.find_all('div', 'example')
        elems = elems[:self.num_examples]

        if len(elems) == 0:
            print(self.text_wrap(colored('No results!', 'red')))
            warning = soup.find('span', 'wide-container message')
            if warning is not None:
                print(self.text_wrap(warning.text))

            return False

        for elem in elems:
            ## ('span', 'text') finds only <span class='text'>
            ## but doesn't pick up <span class='text' lang='ru'>.
            ## 'ru' is taken for example.
            sentence = elem.find('span', 'text')
            translation = elem.find('span', lang=self.lang)

            sentence = self.highlight_words(sentence)
            translation = self.highlight_words(translation)

            print(self.text_wrap(sentence))
            print(self.text_wrap(translation))
            print()

        return True

