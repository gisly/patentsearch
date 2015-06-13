# coding=utf-8
__author__ = 'gisly'
import time
import re


import html_utils
import general_utils


import espace_search

import information_extraction

import ConfigParser


config = ConfigParser.RawConfigParser()
config.read('patentSettings.ini')


FISP_DB_RUS = 'RUPAT'
FILE_TYPE = 'html'

ENCODING = 'cp1251'

BIBL_TAG = 'td'
BIBL_CLASS = 'rbib'

COUNTRYREG_TAG = 'td'
COUNTRYREG_CLASS = 'tdt'


PRIORITY_TAG = 'p'
PRIORITY_CLASS = 'lt'

MPK_TAG = 'tr'
MPK_ATTR = 'valign'
MPK_ATTR_VALUE = 'top'

MPK_DATE_DELIMITER = '('




MPK_NUM_DESC_BIG = ur'МПК \d'
MPK_PATTERN = r'[A-Z0-9]+/\d\d'


AUTHOR_DESC = u'Автор(ы):'
OWNER_DESC = u'Патентообладатель(и):'
REGISTRATOR_DESC = u'Заявитель(и):'

BIBL_GROUP_DELIM = '</b>'


APPLICATION_NUMBER = '(21)'
APPLICATION_DESC = u'Заявка:'


APP_PUBLISHED_NUMBER = '(43)'
APP_PUBLISHED_DESC = u'Дата публикации заявки:'

PUBLISHED_NUMBER = '(45)'
PUBLISHED_DESC = u'Опубликовано:'

ABSTRACT_DESC = u'Реферат:'


ABSTRACT_TAG = 'span'
ABSTRACT_CLASS = 'referat'


TITLE_NUMBER = '(54)'
TITLE_END = '</b>'

DELIMITER = '<br/>'


SPECIFIC_TERMS = [u'ф-лы', u'ил', u'табл']


uniqueSymbols = []

FIPS_TYPE = u'Патент на изобретение'



PICTURES_SYMBOLS = {
                    'http://www.fips.ru/chr/8202.gif':' ',
                    'http://www.fips.ru/chr/183.gif':u'·',
                    'http://www.fips.ru/chr/963.gif':u'σ',
                    'http://www.fips.ru/chr/8804.gif':u'≤',
                    'http://www.fips.ru/chr/8805.gif':u'≥',
                    'http://www.fips.ru/chr/931.gif':u'Σ',
                    'http://www.fips.ru/chr/177.gif':u'±',
                    }



SPECIAL_CHARACTERS = {
                      '<sup>,</sup>':u'ʹ'
                      }


"""
processes a patent by its id
"""
def parsePatentById(patentId):
    time.sleep(config.getint('FIPS', 'PAUSE_SEC'))
    params = {'DB':FISP_DB_RUS, 'TypeFile':FILE_TYPE, 'DocNumber':patentId}
    patentHTML = html_utils.getHTMLData(config.get('FIPS', 'URL'), ENCODING, params)
    
    return parsePatentHTML(patentHTML)

"""
parses a patent HTML according to the standards
"""
def parsePatentHTML(patentHTML):
    patent = dict()
    country, patentNumber = parseCountryReg(patentHTML)
   
    patent['country'] = country.strip()
    patent['type'] = FIPS_TYPE
    patent['patentNumber'] = patentNumber
    
    patentId, patentKC = getPatentIdKC(patentNumber)
    
    mpkClasses = parseMPKClasses(patentHTML)
    patent['mpkClasses'] = mpkClasses
    

    registrators, authors, owners = parseAuthors(patentHTML)

    patent['registrators'] = general_utils.normalizeWhitespace(re.sub(',+',',', ', '.join(registrators).strip()))
    patent['owners'] = general_utils.normalizeWhitespace(re.sub(',+',',', ', '.join(owners).strip()))
    
    
    appNumber, appDate, appPublishedDate, publishedDate = parseApplicationData(patentHTML)
    patent['appNumber'] = appNumber.strip()
    patent['appDate'] = appDate.strip()
    if appPublishedDate:
        patent['appPublishedDate'] = appPublishedDate.strip()
    if publishedDate:
        patent['publishedDate'] = publishedDate.strip()
    title = parseTitle(patentHTML)
    patent['title'] = general_utils.normalizeWhitespace(title.lower().strip().capitalize())
    abstractText = parseAbstract(patentHTML)
    patent['abstractText'] = abstractText
    patent['analogues'] = espace_search.getAnaloguesForRussian(patentId, patentKC)
    patent['informationExtraction'] = information_extraction.extractInfo(abstractText, 'RU')
    
    
    if not('registrators' in patent and 'RU' in patent['registrators']) \
        and not('owners' in patent and 'RU' in patent['owners']):
        regCountry = getRegCountry(patent['registrators'],  patent['owners'])
        if regCountry != 'RU':
        #we have to look for the original app/patent in the foreign country
            foreignPatent = None
            if patent['analogues']: 
                foreignPatentNumber, kc = searchLastApp(patent['analogues'], regCountry)
                if not foreignPatentNumber:
                    regCountry = 'WO'
                    foreignPatentNumber, kc = searchLastApp(patent['analogues'], regCountry)
                if foreignPatentNumber:
                    print foreignPatentNumber
                    print regCountry
                    print ','.join(patent['analogues'])
                    foreignPatent = espace_search.parsePatentById(foreignPatentNumber, regCountry, kc)
            else:
                priority = parsePriority(patentHTML)
                print priority
                numPriority = priority.split(' ', 1)[1].replace(' ','').replace('-', '')
                print numPriority
                foreignPatent = espace_search.parsePatentByPriorityNumber(numPriority)
                
            if foreignPatent:
                if patent['title'] != '':
                    foreignPatent['title'] = patent['title']
                if patent['abstractText'] != '':
                    foreignPatent['abstractText'] = patent['abstractText']
                    foreignPatent['informationExtraction'] = patent['informationExtraction']
                """if not 'registrators' in foreignPatent and 'registrators' in patent:
                    foreignPatent['registrators'] = patent['registrators']
                if not 'owners' in foreignPatent and 'owners' in patent:
                    foreignPatent['owners'] = patent['owners']"""
                    
                abstract = ''
    
                if foreignPatent['abstractText'] != '':
                    abstract =  foreignPatent['abstractText']
                    
                foreignPatent['abstractText'] = patent['patentNumber'] + ' ' + abstract   
                    
                return foreignPatent
            
    
    abstract = ''
    
    if patent['abstractText'] != '':
        abstract =  patent['abstractText']
        
    patent['abstractText'] = patent['patentNumber'] + ' ' + abstract
    return patent
    
    
    
"""
parses the country information
"""   
def parseCountryReg(patentHTML):
    countryRegs = html_utils.getHTMLTagsByAttribute(patentHTML, COUNTRYREG_TAG, 'class', COUNTRYREG_CLASS)
    country = normalizeNonList(countryRegs[0].text)
    patentNumber = normalizeNonList(countryRegs[1].text) + ' ' + normalizeNonList(countryRegs[2].text)
    return country, patentNumber

"""parses the MPK information"""
def parseMPKClasses(patentHTML):
    mpkElement = html_utils.getFirstHTMLTagByAttribute(patentHTML, 
                                                                             MPK_TAG,
                                                                             MPK_ATTR,
                                                                             MPK_ATTR_VALUE)
    mpkText =  html_utils.normalize(html_utils.createString(mpkElement))
    mpkCodes = normalizeNonList(re.split(MPK_NUM_DESC_BIG, mpkText)[-1]).strip()
    mpkCodeList =  re.findall(MPK_PATTERN, mpkCodes)
    return mpkCodeList

"""parses the people information"""
def parseAuthors(patentHTML):
    bibliography = html_utils.getFirstHTMLTagByAttribute(patentHTML, BIBL_TAG, 'class', BIBL_CLASS)
    bibliographyContent = html_utils.unescape(html_utils.createString(bibliography))      
        
    registrators = processBiblioPeople(bibliographyContent, REGISTRATOR_DESC)
    authors = processBiblioPeople(bibliographyContent, AUTHOR_DESC)   
    owners = processBiblioPeople(bibliographyContent, OWNER_DESC)

    return registrators, authors, owners

"""parses the bibliograpy information"""
def processBiblioPeople(bibliographyContent, PEOPLE_DESC):
    if PEOPLE_DESC in bibliographyContent:
        peopleElement = bibliographyContent.split(PEOPLE_DESC)[-1]
        peopleText = peopleElement.split(BIBL_GROUP_DELIM)[0].strip()
        return prepareFipsList(splitHTMLList(peopleText))
    return []

"""parses the date information"""
def parseApplicationData(patentHTML):
    applicationElements = html_utils.getHTMLTagsByAttribute(patentHTML, 'p', 'class', 'lt')
    appNumber = None
    appDate = None
    appPublishedDate = None
    publishedDate = None
    for applicationElement in applicationElements:
        applicationElementText = applicationElement.text
        if APPLICATION_NUMBER in applicationElementText:
            applicationElementContents = html_utils.createString(applicationElement)
            appNumberDate = html_utils.normalize(applicationElementContents).split(APPLICATION_DESC)[-1].strip()
            appNumber, appDate = appNumberDate.split(',')
            
        elif PUBLISHED_NUMBER in applicationElementText:
            publishedContents = html_utils.createString(applicationElement)
            publishedDate = html_utils.normalize(publishedContents).split(PUBLISHED_DESC)[-1].strip()
            
        elif APP_PUBLISHED_NUMBER in applicationElementText:
            appPublishedContents = html_utils.createString(applicationElement)
            appPublishedDate = html_utils.normalize(appPublishedContents).split(APP_PUBLISHED_DESC)[-1].strip()
            
    return  appNumber.strip(), appDate, appPublishedDate, publishedDate

"""parses the title"""
def parseTitle(patentHTML):
    wholeTextString = html_utils.createString(patentHTML)
    return normalizeNonList(wholeTextString.split(TITLE_NUMBER)[-1].split(TITLE_END)[0])

"""parses the abstract"""
def parseAbstract(patentHTML):
    abstractElement = html_utils.getFirstHTMLTagByAttribute(patentHTML, ABSTRACT_TAG, 'class', ABSTRACT_CLASS)
    if abstractElement is None:
        return ''
    picturesToReplace = processPictures(abstractElement)
    abstractHTML = replacePicturesInHtml(picturesToReplace, html_utils.createString(abstractElement))
    
    abstractHTML  = replaceSpecialSymbolsInHtml(abstractHTML)
    abstractContent = html_utils.normalize(abstractHTML).split(ABSTRACT_DESC)[1].strip()
    return general_utils.normalizeWhitespace(parseOnlyMeaningfulAbstract(abstractContent))


"""
parses the priority information
"""   
def parsePriority(patentHTML):
    allBibTags = html_utils.getHTMLTagsByAttribute(patentHTML, PRIORITY_TAG, 'class', PRIORITY_CLASS)
    for bibTag in allBibTags:
        bibTagStr = html_utils.normalize(html_utils.createString(bibTag))
        if u'Конвенционный приоритет' in bibTagStr:
            return bibTagStr.split('Конвенционный приоритет:')[1].strip()
    return None

"""extracts the meaningful information from the abstract
(that is, omits sentences like figure 3 or table 2"""
def parseOnlyMeaningfulAbstract(abstractContent):
    abstractContentSentences = abstractContent.split('.')
    lastIndex = len(abstractContentSentences)-1
    goodLastIndex = lastIndex
    for i in range(lastIndex, -1, -1):
        curSentence = general_utils.normalizeWhitespace(abstractContentSentences[i])
        if curSentence!='' and not isNotMeaningful(curSentence):
            goodLastIndex = i
            break
    return '.'.join(abstractContentSentences[0:goodLastIndex + 1])+'.'

"""parses the patent id"""
def getPatentIdKC(patentNumber):
    patentNumberParts = patentNumber.split(' ')
    return patentNumberParts[0], patentNumberParts[1]

def normalizeNonList(element):
    return html_utils.normalize(element).replace(',','')

def splitHTMLList(htmlList):
    return [html_utils.normalize(element).strip() for element in splitHtmlIntoFipsElement(htmlList)]

def splitHtmlIntoFipsElement(htmlList):
    return htmlList.split(DELIMITER)

def prepareFipsList(fipsList):
    return [element.strip() for element in fipsList if element!='']


def getRegCountry(patentRegistrators, patentOwners):
    COUNTRY_REGEX = ur'.+?\((..)\)'
    if patentRegistrators:
        countryMatch = re.match(COUNTRY_REGEX, patentRegistrators)
        if countryMatch:
            return countryMatch.group(1)
    if patentOwners:
        countryMatch = re.match(COUNTRY_REGEX, patentOwners)
        if countryMatch:
            return countryMatch.group(1)
    return 'RU'

def searchLastApp(analogues, regCountry):
    toSearch = regCountry + '(.+?) \((.+?)\)'
    matchRes = None
    for analogue in analogues:
        for matchRes in re.finditer(toSearch, analogue):
            pass
        if matchRes:
            return matchRes.group(1), matchRes.group(2)
    return None, None

"""
replaces graphical elements (e. g., grade sign) with the corresponding characters
"""
def processPictures(abstractHTML):
    if abstractHTML is None:
        return None
    global uniqueSymbols
    allPictures = html_utils.getHTMLTags(abstractHTML, 'img')
    picturesToReplace = dict()
    for picture in allPictures:
        pictureSrc = picture.attrib['src']
        if not pictureSrc in uniqueSymbols:
            uniqueSymbols.append(pictureSrc)  
        if pictureSrc in PICTURES_SYMBOLS:
            pictureText = html_utils.createString(picture).split('>')[0]+'>' 
            picturesToReplace[pictureText] = PICTURES_SYMBOLS[pictureSrc]
    return picturesToReplace


def replacePicturesInHtml(picturesToReplace, html):
    for picture, symbol in picturesToReplace.iteritems():
        html = html.replace(picture, symbol)
    return html

def replaceSpecialSymbolsInHtml(html):
    for symbolOld, symbolNew in SPECIAL_CHARACTERS.iteritems():
        html = html.replace(symbolOld, symbolNew)
    return html

"""filtering meaningless information (references to pics,  formulae etc)
the sentence is considered meaningless if:
-it starts with a number
-it is too short
-it references to plots, formulae etc.
"""
def isNotMeaningful(abstractSentence):
    return isStartingWithNumber(abstractSentence)\
        or isTooShort(abstractSentence)\
        or hasSpecificTerms(abstractSentence)


def isStartingWithNumber(abstractSentence):
    clearText = abstractSentence.replace(',', '').strip()
    return re.match(ur'\d', clearText) is not None

def isTooShort(abstractSentence):
    return len(abstractSentence) < config.get('FIPS', 'MIN_SENTENCE_LENGTH')

def hasSpecificTerms(abstractSentence):
    for specTerm in SPECIFIC_TERMS:
        if re.search('^' + specTerm, abstractSentence) is not None\
          or re.search(specTerm + '$', abstractSentence) is not None\
          or re.search(specTerm + '\s', abstractSentence) is not None:
            return True
    return False



#print searchFirstApp('RU123 (C1) US123465(C2)', 'RU')

