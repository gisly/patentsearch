# coding=utf-8
__author__ = 'gisly'
import ConfigParser
import time
import re

import html_utils
import general_utils
import information_extraction






FOREIGN_DB = 'EPODOC'
FOREIGN_II = '0'
FOREIGN_LOCALE = 'ru_ru'
FOREIGN_FT = 'D'
FOREIGN_AT = '7'


APP_HEADER = 'th'
APP_CLASS = 'printTableText'

MPK_TAG = 'a'
MPK_CLASS = 'ipc classTT'


REGISTRATOR_TAG = 'span'
REGISTRATOR_ATTR = 'id'
REGISTRATOR_CLASS = 'applicants'


DATE_PUBLISHED_TAG = 'h1'
DATE_PUBLISHED_CLASS = 'noBottomMargin'

ANALOGUE_NEXT_LINK = 'a'
ANALOGUE_NEXT_DESC = u'далее'
ANALOGUE_LESS_DESC = u'свернуть'

ANALOGUE_NEXT_DESC_EN = u'next'


APP_DATE_DESC = u'Номер заявки:'
PRIORITY_DESC = u'Номера приоритетных документов'
ANALOGOUS_DESC = u'Также опубликовано'
ANALOGOUS_DESC_EN = u'Also published as'


ABSTRACT_TAG = 'p'
ABSTRACT_CLASS = 'printAbstract'


FORMULA_TAG = 'div'
FORMULA_ID = 'claims'

LAW_COUNTRY_DESC = u'Designated contracting states'
LAW_TAG = 'table'
LAW_CLASS = 'tableType3 printTable'

#TODO: create a simple structure using country codes
PATENT_TYPES = {
                'WO':
                    {'A1':u'Международная заявка',
                     'A2':u'Международная заявка',
                     'A':u'Международная заявка'},
                    
                'EP':
                    {'A':u'Европейская заявка',
                     'A4':u'Европейская заявка',
                     'A1':u'Европейская заявка',
                     'B1':u'Европейский патент на изобретение'},
                    
                'DE':
                    {'A1':u'Заявка Германии на изобретение',
                    'B1':u'Патент Германии на изобретение',
                    'B4':u'Патент Германии на изобретение',
                    'T2':u'Патент Германии на изобретение (переведенный европейский патент)',
                    'C5':u'Патент Германии на изобретение',},
                
                
                 'NL':
                    {'A1':u'Заявка Нидерландов на изобретение',
                    'B1':u'Патент Нидерландов на изобретение',
                    'B4':u'Патент Нидерландов на изобретение',
                    'C2':u'Патент Нидерландов на изобретение',
                    'T2':u'Патент Нидерландов на изобретение (переведенный европейский патент)'},
                
                
                'FR':
                    {'A1':u'Заявка Франции на изобретение',
                    'B1':u'Патент Франции на изобретение',
                    'B4':u'Патент Франции на изобретение',
                    'T2':u'Патент Франции на изобретение (переведенный европейский патент)'},
                
                'ES':
                    {'A1':u'Заявка Испании на изобретение',
                    'B1':u'Патент Испании на изобретение',
                    'B4':u'Патент Испании на изобретение',
                    'T2':u'Патент Испании на изобретение (переведенный европейский патент)'},
                
                'CA':
                    {'A1':u'Заявка Канады на изобретение',
                    'B1':u'Патент Канады на изобретение'},
                
                
                'TW':
                    {'A':u'Заявка Тайваня на изобретение',
                    'B1':u'Патент Тайваня на изобретение',
                    'B':u'Патент Тайваня на изобретение'},
                
                
                'CN':
                    {'A':u'Заявка Китая на изобретение',
                     'A2':u'Заявка Китая на изобретение',
                    'B1':u'Патент Китая на изобретение',
                     'B':u'Патент Китая на изобретение',
                     'C':u'Патент Китая на изобретение'},
                'US':
                    {'A':u'Заявка США на изобретение',
                     'A1':u'Заявка США на изобретение',
                     'A2':u'Заявка США на изобретение',
                    'B1':u'Патент США на изобретение',
                    'B2':u'Патент США на изобретение',
                    },
                
                
                'UA':
                    {'A':u'Заявка Украины на изобретение',
                     'A1':u'Заявка Украины на изобретение',
                     'A2':u'Заявка Украины на изобретение',
                    'B1':u'Патент Украины на изобретение',
                    'C2':u'Патент Украины на изобретение'},
                
                
                'RU':
                    {'A1':u'Заявка России на изобретение',
                     'A':u'Заявка России на изобретение',
                    'B1':u'Патент России на изобретение',
                    'B4':u'Патент России на изобретение',
                    'T2':u'Патент России на изобретение (переведенный европейский патент)'},
                
                
                'KR':
                    {'A':u'Заявка Южной Кореи на изобретение',
                     'A2':u'Заявка Южной Кореи на изобретение',
                    'B1':u'Патент Южной Кореи на изобретение'},
                
                
                'JP':
                    {'A':u'Заявка Японии на изобретение',
                     'A2':u'Заявка Японии на изобретение',
                    'B1':u'Патент Японии на изобретение',
                    'B2':u'Патент Японии на изобретение'},
                
                }

INTERNATIONAL_CODE = 'WO'
EUROPEAN_CODE = 'EP'
RUSSIAN_CODE = 'RU'
AMERICAN_CODE = 'US'
JAPANESE_CODE = 'JP'

ENCODING = 'utf-8'

config = ConfigParser.RawConfigParser()
config.read('patentSettings.ini')

#TODO: ESPACES provides web-services
#we should try using them instead of parsing HTML


"""
returns patent information
"""
def parsePatentById(patentId, patentCC, patentKC, patentTitle = None, patentAbstract = None):
    patentHTML = getPatentHtml(patentId, patentCC, patentKC)
    return parsePatentHTML(patentHTML, patentId, patentCC, patentKC, patentTitle, patentAbstract)

def parsePatentByPriorityNumber(priorityNumber, patentTitle = None, patentAbstract = None):
    prioritySearchResulsHTML = getPrioritySearchResults(priorityNumber)

    firstLink = html_utils.getFirstHTMLTagByAttribute(prioritySearchResulsHTML, 'a', 'class', 'publicationLinkClass')
    if firstLink is None:
        print 'cannot find the priority'
        return None
    linkParams = html_utils.getParams(html_utils.unescape(firstLink.attrib['href']))
    curNumber = linkParams['NR']
    kcIndex = curNumber.index(linkParams['KC']) 
    if kcIndex > 0:
        curNumber = curNumber[0:kcIndex]
    foundPatentHtml = getPatentHtml(curNumber, linkParams['CC'], linkParams['KC'])
    regCountry = priorityNumber[0:2]
    #if we've found the patent mentioned in the priority document
    if linkParams['CC']  == regCountry:
        return parsePatentHTML(foundPatentHtml, curNumber, linkParams['CC'], linkParams['KC'], patentTitle, patentAbstract)
    #else we've got to look fot the analogues
    appNumber, appDate, priorityDates, pct, analogues = parseApplicationData(foundPatentHtml)
    if analogues:
        return parsePatentAnalogue(analogues, regCountry, patentTitle, patentAbstract)
    return None


def parsePatentAnalogue(patentAnalogues, regCountry, patentTitle = None, patentAbstract = None):
    if patentAnalogues is None:
        return None
    firstAnalogueNumber, firstAnalogueKC = findFirstAnalogueByCountry(patentAnalogues, regCountry)
    if firstAnalogueNumber and firstAnalogueKC:
        return parsePatentById(firstAnalogueNumber, regCountry, firstAnalogueKC, patentTitle, patentAbstract)
    return None

def getPatentHtml(patentId, patentCC, patentKC):
    time.sleep(config.getint('ESPACE', 'PAUSE_SEC'))
    params = {'DB':FOREIGN_DB, 
              'II':FOREIGN_II,
              'locale':FOREIGN_LOCALE,
              'FT':FOREIGN_FT,
              'at':FOREIGN_AT,
              'CC':patentCC,
              'NR':patentId + patentKC,
              'KC':patentKC,
              }
    
    return html_utils.getHTMLData(config.get('ESPACE', 'URL_BIBLIO'), ENCODING, params, isProxy = True)


def getLawHtml(patentId, patentCC, patentKC):
    time.sleep(config.getint('ESPACE', 'PAUSE_SEC'))
    params = {'CY':'RU', 
              'DB':'REG',
              'LG':'ru',
              'PN': patentCC + patentId,
            'locale':'ru_RU'
              }

    return html_utils.getHTMLData(config.get('ESPACE', 'URL_LAW'), ENCODING, params, isProxy = True)


def getPrioritySearchResults(priorityNumber):
    time.sleep(config.getint('ESPACE', 'PAUSE_SEC'))
    params = {'DB':FOREIGN_DB, 
              'II':FOREIGN_II,
              'locale':FOREIGN_LOCALE,
              'FT':FOREIGN_FT,
              'at':FOREIGN_AT,
              'PR':priorityNumber
              }

    return html_utils.getHTMLData(config.get('ESPACE', 'URL_SEARCH'), ENCODING, params, isProxy = True)

"""
returns patent information
patentHTML -- patentHTML
patentId, patentCC, patentKC -- parts of the patent identifier
patentTitle -- the translation of the patent's title (default is None)
patentAbstract -- the translation of the patent's abstract (default is None)
"""
def parsePatentHTML(patentHTML, patentId, patentCC, patentKC, patentTitle = None, patentAbstract = None):
    patent = dict()
    patent['type'] = defineType(patentCC, patentKC)
    patent['patentNumber'] = patentCC + patentId + '(' +patentKC + ')'
    patent['mpkClasses'] = parseMPKClasses(patentHTML)    
    appNumber, appDate, priorityDates, pct, analogues = parseApplicationData(patentHTML)

    
    if appNumber:    
        patent['appNumber'] = appNumber.strip()
    patent['appDate'] = appDate.strip()
    patent['priorityDates'] = priorityDates
    if pct is not None:
        patent['pctNumber'] = pct[0].strip()
        patent['pctDate'] = pct[1].strip()
        
    if analogues is not None:
        patent['analogues'] = analogues

    if isPatent(patentKC):
        #have to get the original app
        try:
            appId = None
            appKC = None
            if not (patentCC in [AMERICAN_CODE, JAPANESE_CODE]):
                appId = patentId
                if len(patentKC) == 1:
                    appKC = 'A'
                else:
                    appKC = 'A1' 
            elif analogues:
                analogueMatch = re.match('(..)(\d+?) \((.+?)\)', analogues[0])
                print analogues[0]
                if analogueMatch:
                    firstAnalogueCC = analogueMatch.group(1)
                    appId = analogueMatch.group(2)
                    appKC = analogueMatch.group(3)
            if appId:
                originalAppHtml = getPatentHtml(appId, patentCC, appKC)
                patent['appPublishedDate'] = parsePublishedDate(originalAppHtml).strip()
                regs = parseAuthors(originalAppHtml)
                if regs:
                    patent['registrators'] = regs.strip() 
        except Exception, e:
            print 'no original app: ' + str(e)
            
        
        patent['publishedDate'] = parsePublishedDate(patentHTML).strip()
        authorsParse = parseAuthors(patentHTML)
        if authorsParse is None:
            print '!!!authorsParse is None'
            print html_utils.createString(patentHTML)
        else:
            patent['owners'] = parseAuthors(patentHTML).strip()
        
    else: 
        if analogues:
            print 'searching for the patent'
            analogueMatch = re.match('(..)(\d+?) \((.+?)\)', analogues[0])
            print analogues[0]
            if analogueMatch:
                firstAnalogueCC = analogueMatch.group(1)
                firstAnalogueId = analogueMatch.group(2)
                firstAnalogueKC = analogueMatch.group(3)
                if firstAnalogueCC == patentCC and (firstAnalogueKC[0] == 'B' or firstAnalogueKC[0] == 'C'):
                    print 'patentId:'+firstAnalogueId
                    return parsePatentById(firstAnalogueId, firstAnalogueCC, firstAnalogueKC, patentTitle, patentAbstract)
        patent['appPublishedDate'] = parsePublishedDate(patentHTML).strip()
        regs = parseAuthors(patentHTML)
        if regs:
            patent['registrators'] = regs.strip()    
    #if the country matches then go on
    #TODO: check it!
    if  not(patent.get('registrators') and '[' + patentCC+']' in patent.get('registrators')) and \
        not (patent.get('owners') and '[' + patentCC+']' in patent.get('owners')):
            
        regCountry = getRegCountry(patent.get('registrators'),  patent.get('owners'))
    
        if regCountry and regCountry != patentCC:  
            print 'INEQUAL!: '+regCountry+'!='+patentCC
            foreignPatent = None 
            if analogues:
                foreignPatentNumber, kc = searchLastApp(patent['analogues'], regCountry)
                if not foreignPatentNumber:
                    regCountry = 'WO'
                    foreignPatentNumber, kc = searchLastApp(patent['analogues'], regCountry)
                if foreignPatentNumber:
                    print foreignPatentNumber
                    print regCountry
                    print ','.join(patent['analogues'])
                    foreignPatent = parsePatentById(foreignPatentNumber, regCountry, kc)
            else:
                if priorityDates:
                    numPriority = priorityDates[0][0]
                    print 'numPriority:'+numPriority
                    foreignPatent = parsePatentByPriorityNumber(numPriority)    
            if foreignPatent:
                if 'title' in patent and patent['title'] != '':
                    foreignPatent['title'] = patent['title']
                if 'abstractText' in patent and patent['abstractText'] != '':
                    foreignPatent['abstractText'] = patent['abstractText']
                    foreignPatent['informationExtraction'] = patent['informationExtraction']
                if not 'registrators' in foreignPatent and 'registrators' in patent:
                    foreignPatent['registrators'] = patent['registrators']
                if not 'owners' in foreignPatent and 'owners' in patent:
                    foreignPatent['owners'] = patent['owners']
                return foreignPatent
        
    if isEuropean(patentCC):
        patent['lawData'] = parseLawData(patentId, patentCC, patentKC)
        
    if patentTitle:
        patent['title'] =     patentTitle
    else:
        patent['title'] = parseTitle(patentHTML).strip()
       
    patentAbstractOriginal = parseAbstract(patentHTML) 
       
    
        
    if patentAbstract:
        patent['abstractText'] =     patentAbstract
        patent['informationExtraction'] = information_extraction.extractInfo(patent['abstractText'], 'RU') 
    else:
        patent['abstractText'] = patentAbstractOriginal
        if patentAbstractOriginal:
            patent['informationExtraction'] = information_extraction.extractInfo(patent['abstractText'], 'EN') 
    
    
    
   
    if 'informationExtraction' in patent:   
        if len(patent['informationExtraction']['chemical']) == 0:
            patentFormula = parseFormula(patentId, patentCC, patentKC)    
            if patentFormula:
                patent['informationExtractionAdditional'] = u'см. формулу:'+ patentFormula
            else:
                patent['informationExtractionAdditional'] = u'нет формулы'
    
    return patent

"""
checks if it's a patent(True) or an application (False)
"""
def isPatent(patentKC):
    return patentKC.startswith('B') or patentKC.startswith('C')

"""
returns the MPK classes
"""

def parseMPKClasses(patentHTML):
    allMpkElements = html_utils.getHTMLTagsByAttribute(patentHTML, MPK_TAG , 'class', MPK_CLASS)
    return [mpkElement.text.strip() for mpkElement in allMpkElements]


"""
returns the people information
"""
def parseAuthors(patentHTML):
    registratorText = html_utils.getFirstHTMLTagByAttribute(patentHTML, REGISTRATOR_TAG , 
                                                            REGISTRATOR_ATTR, REGISTRATOR_CLASS)

    if registratorText is None:
        return None
    return general_utils.normalizeWhitespace(registratorText.text.strip())


"""
returns the date information
"""
def parseApplicationData(patentHTML):
    appNumber = None
    appDate = None
    priorityData = None
    pct = None
    analogues = None
    allAppElements = html_utils.getAllTagsByAttribute(patentHTML, 'class', APP_CLASS)

    
    
    for i in range(0, len(allAppElements)):
        curElement = allAppElements[i]
        if curElement.tag == APP_HEADER and APP_DATE_DESC in curElement.text:
            appNumberDate = allAppElements[i + 1].text.strip().split(' ')
            appNumber = appNumberDate[0]
            appDate = formatDate(appNumberDate[1])
        elif curElement.tag == APP_HEADER and PRIORITY_DESC in curElement.text:
            priorityElements = html_utils.normalize(html_utils.createString(allAppElements[i + 1])).strip().split(';')
            priorityData = []
            for priorityElement in priorityElements:
                priorityElementParts = priorityElement.strip().split(' ')
                priorityNum = priorityElementParts[0].strip()
                priorityDate = formatDate(priorityElementParts[1].strip())
                if isInternational(priorityNum):
                    pctNum = formatPCT(priorityNum)
                    pct = (pctNum, priorityDate)
                priorityData.append((priorityNum,priorityDate))
        if curElement.tag == APP_HEADER and (ANALOGOUS_DESC in curElement.text or ANALOGOUS_DESC_EN in curElement.text):
            analogues = parseAnalogueDataCheckNext(curElement, allAppElements, i)
                
    return appNumber, appDate, priorityData, pct, analogues


def parsePublishedDate(patentHTML):
    appPublishedElement = html_utils.getFirstHTMLTagByAttribute(patentHTML, DATE_PUBLISHED_TAG, 
                                                                'class', DATE_PUBLISHED_CLASS)
    return formatHeaderDate(appPublishedElement.text.strip().split(' ')[-1])

"""
returns the title information
"""

def parseTitle(patentHTML):
    titleElement = html_utils.getFirstHTMLTagByAttribute(patentHTML, 'span', 'id', 'bookmarkTitle')
    return titleElement.text.strip()


"""
returns the abstract information
"""

def parseAbstract(patentHTML):
    abstractElement = html_utils.getFirstHTMLTagByAttribute(patentHTML, ABSTRACT_TAG, 
                                                            'class', ABSTRACT_CLASS)
    
   
    if abstractElement is None or abstractElement.text is None:
        return ''
        
    return abstractElement.text.strip()

"""
parses additional data (legal data, such as countries which accept the patent)
"""

def parseLawData(patentId, patentCC, patentKC):
    lawHtml = getLawHtml(patentId, patentCC, patentKC)
    
    appLawDataElements = html_utils.getChildrenByParentTagAttribute(lawHtml, LAW_TAG, 
                                                                    'class', LAW_CLASS)
       
    for i in range(0, len(appLawDataElements)):
        curElement = appLawDataElements[i]
        if curElement.text and LAW_COUNTRY_DESC in curElement.text:
            
            nextElement = appLawDataElements[i + 1]
            nextElementCountryContent = nextElement.text.strip().split('[')[0]
            lawCountryData =  ''.join(nextElementCountryContent.split()).replace(',', ' ')
            return lawCountryData
    return None


"""
looks for analogues for a Russian patent
"""
def getAnaloguesForRussian(russianPatentId, russianPatentKC):
    time.sleep(config.getint('ESPACE', 'PAUSE_SEC'))
    russianPatentHtml = getPatentHtml(russianPatentId, RUSSIAN_CODE, russianPatentKC)
    if russianPatentHtml is None:
        return None
    allAppElements = html_utils.getAllTagsByAttribute(russianPatentHtml, 'class', APP_CLASS)
    for i in range(0, len(allAppElements)):
        curElement = allAppElements[i]
        if curElement.tag == APP_HEADER and (ANALOGOUS_DESC in curElement.text or ANALOGOUS_DESC_EN in curElement.text):
            return parseAnalogueDataCheckNext(curElement, allAppElements, i)   
    return None

"""
returns analogue data
"""

def getAnaloguesByURL(url):
    time.sleep(config.getint('ESPACE', 'PAUSE_SEC'))
    urlPatentHTML = html_utils.getHTMLData(url, ENCODING, None, isProxy = True)
    return parseAnalogueData(urlPatentHTML)
    


def parseAnalogueDataCheckNext(headerElement, allAppElements, curIndex):
    nextElement = allAppElements[curIndex + 1]
    children = nextElement.getchildren()
    for child in children:
        if child.tag == ANALOGUE_NEXT_LINK and ANALOGUE_NEXT_DESC in child.text:   
            #there is a link saying "next"
            #we've got to go there to get the rest of the analogues
            return getAnaloguesByURL(config.get('ESPACE', 'MAIN_ESPACE_URL') + general_utils.normalizeWhitespace(child.attrib['href']))
    #we are happy to have got all the analogues at once
    return getAnalogues(nextElement)

def parseAnalogueData(patentHTML):
    allAppElements = html_utils.getAllTagsByAttribute(patentHTML, 'class', APP_CLASS)
    for i in range(0, len(allAppElements)):
        curElement = allAppElements[i]
        if curElement.tag == APP_HEADER and (ANALOGOUS_DESC in curElement.text or ANALOGOUS_DESC_EN in curElement.text):
            print 'has analogues'
            # we do not need to check the next link now
            return getAnalogues(allAppElements[i + 1])
    return None   


def getAnalogues(analogueElement):
    analogueDataNormalized = general_utils.normalizeWhitespace(html_utils.normalize((html_utils.createString(analogueElement))).split(ANALOGUE_LESS_DESC)[0])
    return analogueDataNormalized.split(';')


def findFirstAnalogueByCountry(analogues, regCountry):
    for analogue in analogues:
        analogueMatch = re.search(regCountry+'(.+?) \((.+?)\)', analogue)
        if analogueMatch:
            return analogueMatch.group(1), analogueMatch.group(2)
    return None, None


#TODO: refactor
def getRegCountry(patentRegistrators, patentOwners):
    COUNTRY_REGEX = ur'.+?\[(..)\]'
    if patentRegistrators:
        countryMatch = re.match(COUNTRY_REGEX, patentRegistrators)
        if countryMatch:
            return countryMatch.group(1)
    if patentOwners:
        countryMatch = re.match(COUNTRY_REGEX, patentOwners)
        if countryMatch:
            return countryMatch.group(1)
    return None


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
returns the so-called formula (the description)
"""   
def parseFormula(patentId, patentCC, patentKC):
    formulaHTML = getFormulaHTML(patentId, patentCC, patentKC)    
    formulaElement = html_utils.getFirstHTMLTagByAttribute(formulaHTML, FORMULA_TAG, 
                                                            'id', FORMULA_ID)
    if formulaElement is not None:
        return html_utils.normalize(html_utils.createString(formulaElement)).strip()
    return None

def getFormulaHTML(patentId, patentCC, patentKC):
    time.sleep(config.getint('ESPACE', 'PAUSE_SEC'))
    params = {'DB':FOREIGN_DB, 
              'II':FOREIGN_II,
              'locale':FOREIGN_LOCALE,
              'FT':FOREIGN_FT,
              'at':FOREIGN_AT,
              'CC':patentCC,
              'NR':patentId + patentKC,
              'KC':patentKC,
              }
    
    return html_utils.getHTMLData(config.get('ESPACE', 'URL_CLAIMS'), ENCODING, params, isProxy = True)
    
def isInternational(appNum):
    return appNum.startswith(INTERNATIONAL_CODE)


def isEuropean(patentCC):
    return patentCC == EUROPEAN_CODE
    
    
def defineType(patentCC, patentKC):
    return PATENT_TYPES[patentCC][patentKC]


def formatPCT(patentNum):
    return patentNum.split(INTERNATIONAL_CODE)[-1]

def formatDate(appDate):
    return appDate[6:] + '.' + appDate[4:6] + '.' + appDate[0:4]


def formatHeaderDate(headerDate):
    return headerDate[8:] + '.' + headerDate[5:7] + '.' + headerDate[0:4]




#print parsePatentById('6312536', 'US', 'B1')

#print findFirstAnalogueByCountry(['RU2012143205 (A) JP2013241636 (A)'], 'JP')
