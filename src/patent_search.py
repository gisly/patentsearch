# coding=utf-8
__author__ = 'gisly'
import codecs
from datetime import datetime

import docs_formatter
import file_utils
import fips_search
import espace_search


TRANSLATION_DELIM = '+++'

"""
Process a list of patents from a file
patentListFilename -- the name of the file with the patent numbers
searchType -- the database to search in (FIPS or ESPACE)
translationFile -- the name of the file with translations (if the patents are not in Russian).
default is None
"""
def parsePatentListFromFile(patentListFilename, searchType, outputFilename, translationFilename = None):
    patentIdList = file_utils.readListFromFile(patentListFilename)
    patentIdList = sorted(patentIdList, reverse = True)
    if translationFilename:
        translations = readTranslationsFromFile(translationFilename)
        parsePatentList(patentIdList, searchType, outputFilename, translations)
    else:
        parsePatentList(patentIdList, searchType, outputFilename, [])
    
            
"""
Process a list of patents
patentIdList -- a list of patent ids
searchType -- the database to search in (FIPS or ESPACE)
translations -- translations for non-Russian patents. Default is None
""" 
def parsePatentList(patentIdList, searchType, outputFilename, translations = None):
    patents = []
    for patentId in patentIdList:
        print patentId
        print str(datetime.now())
        if searchType == 'FIPS':
            patents.append(fips_search.parsePatentById(patentId))
        elif searchType == 'ESPACE':
            idParts = patentId.split('#')
            if patentId in translations:
                patentTitle = translations[patentId]['title']
                patentAbstract = translations[patentId]['abstract']
            else:
                patentTitle = None
                patentAbstract = None
            patents.append(espace_search.parsePatentById(idParts[1], idParts[0], idParts[2], 
                                                         patentTitle, patentAbstract))   
    docs_formatter.createPatentTable(patents, outputFilename + '_main.docx')
    
    docs_formatter.createChemicalTable(patents, outputFilename + '_chemical.docx')
    
    docs_formatter.createTopicTable(patents, outputFilename + '_topics.docx')
    
"""reads translations from a file
Format: patentNumber+++patentTranslation
"""    
def readTranslationsFromFile(translationFile):
    translations = dict()
    with codecs.open(translationFile, 'r', 'utf-8') as fin:
        for line in fin:
            lineParts = line.strip().split(TRANSLATION_DELIM)
            translations[lineParts[0]] = dict()
            translations[lineParts[0]]['title'] = lineParts[1]
            translations[lineParts[0]]['abstract'] = lineParts[2]
    return translations



parsePatentListFromFile('../resources/russianPatents.txt', 'FIPS', 'D://russianTest')
