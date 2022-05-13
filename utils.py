"""
Different utilities that are used across the tma module.
"""
from termcolor import colored


def highlight_words(sen:str, words:list, color='yellow'):
    """
    Colors the words one by one, splitting the sentence in half each time.
    `words` are not in the sentence --> no painting.
    `words` is empty --> no painting.
    """
    acc = ''
    for word in words:
        if word not in sen:
            continue

        left, right = sen.split(word, 1)

        acc += left + colored(word, color)
        sen = right

    acc += sen
    return acc

