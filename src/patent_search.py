# coding=utf-8
__author__ = 'gisly'
import codecs
from datetime import datetime

import docs_formatter
import file_utils
import fips_search
import espace_search
import espace_search_ws
import sys
import traceback

import re


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
    patentIdList = sorted(set(patentIdList), reverse = True)
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
    if translations:
        for patentId, value in translations.iteritems():
            if not patentId in patentIdList:
                print 'new patent!!!' + patentId
    
    
    for patentId in patentIdList:
        try:
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
                   print 'no translation for ' + patentId
                curPatent = espace_search_ws.parsePatentById(idParts[1], idParts[0], idParts[2], 
                                                         patentTitle, patentAbstract)
                curPatent['originalId'] = patentId
                patents.append(curPatent)  
                   
            patents = sorted(patents, key = lambda x:getPatentIdentifiers(x))       
                    
            docs_formatter.createPatentTable(patents, outputFilename + '_main.docx')
            
            docs_formatter.createChemicalTable(patents, outputFilename + '_chemical.docx')
            
            docs_formatter.createTopicTable(patents, outputFilename + '_topics.docx')
        except Exception, e:
            print traceback.format_exc()
            print patentId + str(e)
            
def getPatentIdentifiers(patent):
    return patent['patentNumber'][0:2] + patent['patentNumber'].split('(')[1]
    
"""reads translations from a file
Format: patentNumber+++patentTranslation
"""    
def readTranslationsFromFile(translationFile):
    translations = dict()
    isNextEnglishTitle = False
    with codecs.open(translationFile, 'r', 'utf-8') as fin:
        curId = None
        isTitle = True
        for line in fin:
            strippedLine = line.strip()
            if strippedLine == '':
                continue
            if strippedLine.startswith(u'Номер заявки'):
                isNextEnglishTitle = True
                continue
            
            if isNextEnglishTitle:
                isNextEnglishTitle = False
                continue
            
            
            matchRes = re.match('([A-Z][A-Z])(\d+)\s*?\((.+?)\)', strippedLine)
            if matchRes:
                if curId:
                    translations[curId]['abstract'] = translations[curId]['abstract'].strip()
                curId = matchRes.group(1)  + '#'+ matchRes.group(2) + '#' + matchRes.group(3)
                print curId
                translations[curId] = dict()
                isTitle = True
            else:
                if isTitle:
                    translations[curId]['title'] = line.strip()
                    translations[curId]['abstract'] = ''
                    isTitle = False
                else:
                    translations[curId]['abstract'] += '\r\n' + line.strip()
                
    return translations



def readTranslationsFromFileOld(translationFile):
    translations = dict()
    with codecs.open(translationFile, 'r', 'utf-8') as fin:
        prevAbstract = None
        curId = None
        for line in fin:
            strippedLine = line.strip()
            lineParts = strippedLine.split('+++')
            if len(lineParts) < 3:
                translations[curId]['abstract'] += '\r\n' + strippedLine
            else:
                curId = lineParts[0].strip()
                translations[curId] = dict()
                translations[curId]['title'] = ' '
                translations[curId]['abstract'] =  lineParts[2]
                
                
    return translations



def main():
    if len(sys.argv)<4:
        print('usage1: python patent_search.py patentListFilename searchType outputFilename')
        print('usage2: python patent_search.py patentListFilename searchType outputFilename translationFilename')
        return
    if len(sys.argv)<5:
        parsePatentListFromFile(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        parsePatentListFromFile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


"""if __name__ == "__main__":
    main()"""



parsePatentListFromFile('../resources/nano_13112014_ids.txt', 'ESPACE', 'D://nano_13112014', 
                                            '../resources/nano_13112014_translations.txt')

#parsePatentListFromFile('../resources/nano_12112014.txt', 'ESPACE', 'D://nano_12112014')
#parsePatentListFromFile('../resources/foreignPart1.txt', 'ESPACE', 'D://foreignPart2')
