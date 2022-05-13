"""
Tiny translator (tt).
Configurable via 'config.yaml'.
Can work in interactive mode.
"""
from pathlib import Path
import sys
import warnings

from omegaconf import DictConfig, ListConfig, OmegaConf
import pyttsx3
import requests

from tma import Macmillan, ReversoContext


class API:
    def __init__(self, conf: DictConfig | ListConfig):
        self.mm = Macmillan(conf.textwidth)
        self.rc = ReversoContext(
                conf.num_samples, conf.textwidth,
                conf.target_context_language)

        self.voice = pyttsx3.init()
        self.voice.setProperty('rate', conf.speech_rate)

        self.hist_path = getattr(conf, 'history_file', None)
        self.save_flag = self.hist_path is not None
        self.history = []

    def __call__(self, init_word: str | None = None):
        if init_word is not None:
            self.make_query(init_word)
            return

        print('Type HELP to get help.')
        print('<Ctrl-d> to exit.\n')

        try:
            while True:
                word = input('> ').strip()
                if self.make_query(word):
                    if word not in self.history:  # beta
                        self.history.append(word)

        except KeyboardInterrupt:
            self.write_history()
            print('\n')

        except EOFError:
            self.write_history()
            print('\n')

        except requests.exceptions.ConnectionError:
            print('\nNo internet connection. Exiting..\n')

    def make_query(self, word):
        if self.make_action(word):
            return

        self.voice.say(word)
        self.voice.runAndWait()

        ok1 = self.mm(word)
        ok2 = self.rc(word)

        return (ok1 | ok2) & self.save_flag

    def write_history(self):
        if self.hist_path is None:
            return

        with open(self.hist_path, 'a') as fp:
            for word in self.history:
                fp.write(f'{word}\n')

    def make_action(self, word):
        match word:
            case 'HELP':
                return self._help()
            case 'POP':
                return self._pop()
            case 'SAVE':
                return self._save()
            case 'NOSAVE':
                return self._nosave()
            case 'TAIL':
                return self._tail10()
            case '':
                return True
            case _:
                return False

    def _help(self):
        print('Available commands:')
        print('HELP POP TAIL SAVE NOSAVE')
        return True

    def _pop(self):
        self._warn()
        if self.history:
            item = self.history.pop()
            print(f"Item '{item}' has been removed.")

        return True

    def _tail10(self):
        print('The last <= 10 words queried during the session:')
        print('', *self.history[-10:], sep='\n- ')
        print()

        return True

    def _save(self):
        self._warn()
        if not self.save_flag:
            print('Saving to history from now on.')

        self.save_flag = True
        return True

    def _nosave(self):
        if self.save_flag:
            print('Not writing to history anymore.')

        self.save_flag = False
        return True

    def _warn(self):
        if self.hist_path is None:
            warnings.warn(
                    'NOTE: modifying history does not make sense '
                    "when 'save_to_file' is not set in config.yaml",
                    stacklevel=2)


if __name__ == '__main__':
    folder = Path(__file__).parent
    conf = OmegaConf.load(folder / 'config.yaml')

    init_word = sys.argv[1] if len(sys.argv) > 1 else None

    api = API(conf)
    api(init_word)
