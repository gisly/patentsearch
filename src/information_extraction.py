# coding=utf-8
__author__ = 'gisly'
import re
import language_utils
import general_utils



CHEMICAL_ELEMENTS_FILE = '../resources/chemicalElements.csv'
CHEMICAL_ELEMENTS_FILE_EN = '../resources/chemicalElementsEn.csv'
CHEMICAL_DELIMITER = '\t'
CHEMICAL_ELEMENTS_RU = dict()
CHEMICAL_ELEMENTS_EN = dict()

CHEMICAL_PATTERNS_RU = [ur'ELEMENT( до | не более | *≤ *)(?P<upper>\d+([\.,]\d+)?)',
                        ur'ELEMENT *< *(?P<upperNotIncl>\d+([\.,]\d+)?)',
                            ur'ELEMENT (?P<lower>\d+([\.,]\d+)?)—(?P<upper>\d+([\.,]\d+)?)',
                            ur'ELEMENT (?P<lower>\d+([\.,]\d+)?)-(?P<upper>\d+([\.,]\d+)?)',
                           ]



CHEMICAL_PATTERNS_EN = [ur'(?P<lower>\d+([\.,]\d+)?)( ?(\%|percent))?(( to )|-|~)(?P<upper>\d+([\.,]\d+)?)( ≤ | <= | = )?( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))? (of )?ELEMENT',
                        ur'\(?ELEMENT\)?(:| of)? (?P<lowerPPM>\d+([\.,]\d+)?)( ?(\%|percent))?(( to )|-|~)(≤ |<= |= )?(?P<upperPPM>\d+([\.,]\d+)?) ppm',
                        ur'\(?ELEMENT\)?(:| of)? (?P<lower>\d+([\.,]\d+)?)( ?(\%|percent))?(( to )|-|~)(≤ |<= |= )?(?P<upper>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))?',
                        ur'\(?ELEMENT\)?(:| of)?(( *< *)| less than )(?P<upperNotInclPPM>\d+([\.,]\d+)?) ppm',
                        ur'\(?ELEMENT\)?(:| of)?(( *< *)| less than )(?P<upperNotIncl>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))?',
                        ur'\(?ELEMENT\)?(:| of)?( to )(≤ |<= |= )?(?P<upperPPM>\d+([\.,]\d+)?) ppm',
                        ur'\(?ELEMENT\)?(:| of)?( to )(≤ |<= |= )?(?P<upper>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))?',
                        ur'(up to | *≤ *)(≤ |<= |= )?(?P<upperPPM>\d+([\.,]\d+)?) ppm (of )?ELEMENT',
                        ur'(up to | *≤ *)(≤ |<= |= )?(?P<upper>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))? (of )?ELEMENT',
                        ur'\(?ELEMENT\)?(:| of )?(?P<upper>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))? or less',
                        ur'(?P<upper>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))? or less (of )?ELEMENT',
                        
                        ur'equal to or less than (?P<upper>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))? (of )?ELEMENT',
                        ur'less than (?P<upperNotIncl>\d+([\.,]\d+)?)( ?((wt(\.)?( )?)|mass |weight( )?)?(\%|percent))? (of )?ELEMENT',
                        
                        ur'ELEMENT \(?(?P<lower>\d+([\.,]\d+)?)(-|~)(?P<upper>\d+([\.,]\d+)?)\)?',
                           ]


TOPIC_PATTERNS_RU = [ur'Техническим результатом изобретения является (?P<topicInfo>.*?)[\.$]',]

TOPIC_PATTERNS_EN = [ur'PURPOSE: (?P<topicInfo>.*?)[\.$]',
                     ur'[\.^](?P<topicInfo>.*?) (is|are) achieved',
                     ]


"""
extracts chemical and topic information from a patent text
text - an UTF-8 encoded patent text
language - EN or RU
"""
def extractInfo(text, language):
    information = dict()
    information['chemical'] = extractChemicalInfo(text, language)
    information['topic'] = extractTopicInfo(text, language)   
    
    return information

"""
extracts chemical information from a patent text
text - an UTF-8 encoded patent text
language - EN or RU
"""
def extractChemicalInfo(text, language):
    readChemicalElementsIfNecessary()
    chemInfo = dict()
    if language == 'RU':
        chemElements = CHEMICAL_ELEMENTS_RU
    elif language == 'EN':
        chemElements = CHEMICAL_ELEMENTS_EN
    else:
        raise Exception('unknown language for chemical composition extraction:' + language)    
    for chemicalCode in chemElements:
        #process every chemical element in the periodic table
        elementInfo = extractInformationForElement(chemicalCode, text, language, chemElements[chemicalCode])
        if elementInfo:
            chemInfo[chemicalCode] = elementInfo
    return chemInfo

"""
extracts topic information from a patent text
text - an UTF-8 encoded patent text
language - EN or RU
"""
def extractTopicInfo(text, language):
    if language == 'RU':
        topicPatterns = TOPIC_PATTERNS_RU
    elif language == 'EN':
        topicPatterns = TOPIC_PATTERNS_EN
    else:
        raise Exception('unknown language for topic extraction:' + language)  
    for topicPattern in topicPatterns:
        topicMatch = re.search(topicPattern, text)
        if topicMatch:
            return topicMatch.group('topicInfo').strip()
    # if topics cannot be extracted using regular expressions, just use the last sentence 
    return language_utils.splitIntoSentences(text)[-1]

"""
extracts chemical information for a given element
elementCode -- the chemical code of an element (e. g. He, Cr etc)
text -- an UTF-8 encoded patent text
language -- EN or RU
elementInLanguage -- the element title in the language (like oxygen for O)
"""
def extractInformationForElement(elementCode, text, language, elementInLanguage):
    if language == 'RU':
        #we will look for all case forms and for the element code
        allForms = language_utils.generateForms(elementInLanguage) + [elementCode]
    else:
        allForms = [elementInLanguage.capitalize(), elementInLanguage.lower(), elementCode]
    for elementForm in allForms:
        limits = extractChemByPatterns(elementForm, text, language)
        if limits is not None:
            (lower,upper) = limits
            return (lower, upper)
    return None

"""
extracts chemical information for a given element
elementForm -- the exact form of the element
text -- an UTF-8 encoded patent text 
language -- EN or RU
"""
def extractChemByPatterns(elementForm, text, language):
    if language == 'RU':
        chemPatterns = CHEMICAL_PATTERNS_RU
    elif language == 'EN':
        chemPatterns = CHEMICAL_PATTERNS_EN
    else:
        raise Exception('unknown language for chemical composition extraction:' + language)    

    for pattern in chemPatterns:        
        patternWithSubsitution = pattern.replace('ELEMENT', elementForm)
        match = re.search(patternWithSubsitution, text)
        lower = dict()
        upper = dict()       
        
        if match:
            if 'lower' in match.groupdict():
                lower['number'] = parseNumber(match.group('lower'))
                lower['isIncl'] = True
            elif 'lowerNotIncl' in match.groupdict():
                lower['number'] = parseNumber(match.group('lowerNotIncl'))
                lower['isIncl'] = False
            else:
                lower = None
                
            if 'upper' in match.groupdict():
                upper['number'] = parseNumber(match.group('upper'))
                upper['isIncl'] = True
            elif 'upperNotIncl' in match.groupdict():
                upper['number'] = parseNumber(match.group('upperNotIncl'))
                upper['isIncl'] = False
            #ppm is 10000-th of a percent
            elif 'upperPPM' in match.groupdict():
                upper['number'] = parseNumber(match.group('upperPPM'), mode=10000)
                upper['isIncl'] = True 
            elif 'upperNotInclPPM' in match.groupdict():
                upper['number'] = parseNumber(match.group('upperNotInclPPM'), mode=10000)
                upper['isIncl'] = False
            else:
                upper = None
            return (lower,upper)
    return None


def parseNumber(numAsString, mode = 1):
    numAsString = numAsString.replace(',', '.')
    return float(numAsString)/float(mode)
            
            
"""
cache chemical element information
"""            
def readChemicalElementsIfNecessary():
    global CHEMICAL_ELEMENTS_RU
    if len(CHEMICAL_ELEMENTS_RU) == 0:
        CHEMICAL_ELEMENTS_RU = general_utils.readDictFromFile(CHEMICAL_ELEMENTS_FILE, CHEMICAL_DELIMITER)
        
    global CHEMICAL_ELEMENTS_EN
    if len(CHEMICAL_ELEMENTS_EN) == 0:
        CHEMICAL_ELEMENTS_EN = general_utils.readDictFromFile(CHEMICAL_ELEMENTS_FILE_EN, CHEMICAL_DELIMITER)
            
    
    