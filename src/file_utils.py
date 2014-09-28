# coding=utf-8
__author__ = 'gisly'
import codecs


#utility functions for working with files

"""
reads lines from a file and returns a list
"""

def readListFromFile(filename):
    with codecs.open(filename, 'r', 'utf-8') as fin:
        return [line.strip() for line in fin]