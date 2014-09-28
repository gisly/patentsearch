# coding=utf-8
__author__ = 'gisly'

from datetime import datetime
import codecs

GENERAL_DATE_FORMAT = '%Y-%m-%d'


###########TIME#######################

#some utility functions

month_names = {    u'января':'01',
                   u'февраля':'02',
                   u'марта':'03',
                   u'апреля':'04',
                   u'мая':'05',
                   u'июня':'06',
                   u'июля':'07',
                   u'августа':'08',
                   u'сентября':'09',
                   u'октября':'10',
                   u'ноября':'11',
                   u'декабря':'12',
                   }


def normalizeWhitespace(strToNormalize):
    return ' '.join(strToNormalize.split()).strip()

def parseStrDateAsDate(strDate, dateFormat):
    normalizedDate = normalizeDate(strDate)
    return datetime.strptime(normalizedDate , dateFormat)

def normalizeDate(dateToNormalize):
    for monthName, monthValue in month_names.iteritems():
        if monthName in dateToNormalize:
            return dateToNormalize.replace(monthName, monthValue)
    return dateToNormalize


def writeListIntoFile(wordList, filename):
    wordList = sorted(wordList)
    with codecs.open(filename, 'w', 'utf-8') as fout:
        for word in wordList:
            fout.write(word + '\r\n')
            
            
            
def readDictFromFile(filename, delimiter):
    dictToRead = dict()
    with codecs.open(filename, 'r', 'utf-8') as fin:
        for line in fin:
            lineParts = line.strip().split(delimiter)
            dictToRead[lineParts[0]] = lineParts[1]
    return dictToRead
            
def readListFromFile(filename):
    with codecs.open(filename, 'r', 'utf-8') as fin:
        return [line.strip() for line in fin]
            
            
def readFromFile(filename):
    with codecs.open(filename, 'r', 'utf-8') as fin:
        return ''.join([line for line in fin])


def writeToFile(text, filename):
    with codecs.open(filename, 'w', 'utf-8') as fout:
        fout.write(text)     
    
def writeTokensIntoFile(tokens, filename):
    tokenText = ' '.join(tokens)
    writeToFile(tokenText, filename)
    

def addToDictListByKey(itemToAdd, dictToChange, dictKey):
    if dictKey in dictToChange:
        dictToChange[dictKey].append(itemToAdd)
    else:
        dictToChange[dictKey] = [itemToAdd]
        
        
def printDict(dictToPrint):
    for key, value in dictToPrint.iteritems():
        print(key +' = ' + str(value))
        
        
    


    