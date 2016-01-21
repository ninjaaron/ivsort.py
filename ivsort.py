#!/usr/bin/env python
# coding=UTF-8
"""
Module for properly sorting Hebrew words with niqqud -- according to consonants
first and vowels later. If run from the command line, takes a file with a list
of words as input or reads lines from stdin.

disclaimer: there is no universal method for the ordering of Hebrew vowels. The
order used by this module is:

    Sheva, Hataf Segol, Hataf Patah, Hataf Qamets,
    Hiriq, Tsere, Segol, Patah, Qamets, Holem, Holem Vav, Qibbuts, Shureq

This order may seem foreign to those accustomed to Latin-based languages, but
it was recommended to me by the Academy for the Hebrew Language in Israel, and
it is very similar to orders use by Unicode and standard Israeli keyboard
layouts. It is also more "scientific" in the sense that it follows a
phonological pattern (horizontal to vertical vowels), rather than a
traditional, Latin-based pattern (aeiou).

This does differ from the one convention common in Israeli works, in that it
treats Sin as a separate letter from Shin. This is not especially common in
Israel, but it is the convention in all of the widely used Biblical lexicons
and other Western Biblical scholarship. I do this both because it
would be pedagogical malpractice to give my students glossaries that differ in
this regard from the works they will be using later, and because it is more
accurate from the perspective of historical linguistics.

I would probably revise this approach if this sort engine were targeted at
modern Hebrew.
"""
from __future__ import unicode_literals
import unicodedata as ud
import re
import io
import six
# If you are looking at this that some text editors "fix" the display of
# characters for RTL languages, so some of this may be reversed for your
# viewing pleasure.
CONS = {c: i for i, c in enumerate(' אבגדהוזחטיךכלםמןנסעףפץצקרשׂשת')}
CONS['־'] = CONS[' ']
VOWELORDER = 'םְםֱםֲםֳםִםֵםֶםַםָםֹםֺוֹםֻוּ'.replace('ם', '')
ORDER2 = CONS.copy()
ORDER2.update({c: 100 + i for i, c in enumerate(VOWELORDER)})
VOWELS = set(VOWELORDER)
VOWDAGESH = VOWELS.copy()
VOWDAGESH.add('\u05BC')
RELEVANTCHARS = VOWDAGESH.union(set(CONS))
RELEVANTCHARS = RELEVANTCHARS.union({'\u05C2', '\u05C1'})
TRICKYVAVS = [(u'\u05B9ו', 'וֹ'), (u'ו\u05B9', 'וֹ'), (u'ו\u05BC', 'וּ')]
MATCHSIN = re.compile(u'ש([%s]{0,2})\u05C2' % ''.join(VOWDAGESH))


def sortkey(word):
    """
    Returns a key based on consonants only first, and then consonants and
    vowels together.
    """
    word = substitutions(word)
    key1, key2 = [], []
    for char in word:
        if char in CONS:
            key1.append(CONS[char])
        if char in ORDER2:
            key2.append(ORDER2[char])
    return (key1, key2)


def substitutions(word):
    """
    Return a word that makes sure all characters special to the sort key are
    recognized.
    """
    word = ud.normalize('NFD', word)
    word = ''.join(c for c in word if c in RELEVANTCHARS)
    word = MATCHSIN.sub(u'שׂ\1', word)
    for nfd, nfc in TRICKYVAVS:
        word = trickyvav_replacer(word, nfd, nfc)
    return word


def trickyvav_replacer(word, nfd, nfc):
    """
    Certain vavs make it difficult to tell if they are consonants or vowels,
    This function makes sure.
    """
    check = word.find(nfd)
    i = check
    while check != -1:
        if not (word[i+2:i+1] in VOWDAGESH or word[i-1:i] in VOWELS):
            word = word.replace(nfd, nfc, 1)
        start = i + 1
        check = word[start:].find(nfd)
        i = check + start
    return word


def ivsort(wordlist):
    """Sort your dang list of hebrew words."""
    return sorted(wordlist, key=sortkey)


def main():
    """print the output of a sort"""
    import sys
    try:
        wordlist = io.open(sys.argv[1], encoding='UTF-8')
    except IndexError:
        wordlist = sys.stdin
        if six.PY2:
            wordlist = [w.decode('UTF-8') for w in wordlist]
    for word in ivsort(wordlist):
        print(word.rstrip())


if __name__ == "__main__":
    main()
