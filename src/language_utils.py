# coding=utf-8
__author__ = 'gisly'
from pymorphy.contrib import tokenizers
from pymorphy import get_morph
import nltk
import ConfigParser


config = ConfigParser.RawConfigParser()
config.read('patentSettings.ini')


morph = get_morph(config.get('PYMORPHY','morphSqlite'))

PYMORPHY_NOUN = u'С'

"""splits a text into words"""
def tokenizeText(text):
    return [word for word in tokenizers.extract_words(text)]

"""splits a text into sentences"""
def splitIntoSentences(text):
    return nltk.sent_tokenize(text)

"""generates all noun forms for a word"""
def generateForms(word):
    return [form['word'].lower() for form in morph.decline(word.upper(), gram_class = PYMORPHY_NOUN)]