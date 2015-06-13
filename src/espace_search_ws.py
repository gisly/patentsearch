# coding=utf-8
__author__ = 'gisly'

import html_utils
import web_utils
from base64 import b64encode
import requests
import urllib2
import datetime
import json
import re


import gettext
import pycountry

#import information_extraction

KEY = 'mGBQRejZe7vpxGxZQD6bfgehwq7OCBMD'
SECRET = 'q4CYSLfGaGUnKnvn'
AUTH_URL = 'https://ops.epo.org/3.1/auth/accesstoken'
BIBLIO_URL = 'https://ops.epo.org/rest-services/published-data/publication/epodoc/'
BIBLIO_URL_INTERNATIONAL = 'https://ops.epo.org/rest-services/published-data/publication/docdb/'
FAMILY_URL_INTERNATIONAL ='https://ops.epo.org/rest-services/family/publication/docdb/'
FAMILY_URL ='https://ops.epo.org/rest-services/family/publication/epodoc/'

ACCESS_TOKEN = None
EXPIRATION_TIME = None

ENCODING = 'utf-8'

#used code from epo_ops
def authorize():
    global ACCESS_TOKEN
    global EXPIRATION_TIME
    
    headers = {
            'Authorization': 'Basic {0}'.format(
                b64encode(
                    '{0}:{1}'.format(KEY, SECRET).encode('ascii')
                ).decode('ascii')
            ),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    payload = {'grant_type': 'client_credentials'}
    response = requests.post(
        AUTH_URL, headers=headers, data=payload
    )
    jsonContent = json.loads(response.content);
    ACCESS_TOKEN = jsonContent['access_token']
    intervalExpiresSeconds = int(jsonContent['expires_in'])
    currentTime = datetime.datetime.now()
    EXPIRATION_TIME = currentTime + datetime.timedelta(0, 0, intervalExpiresSeconds)
    

def parsePatentById(patentId, patentCC, patentKC, patentTitle = None, patentAbstract = None, historicalCC = None):
    if EXPIRATION_TIME is None or EXPIRATION_TIME <= datetime.datetime.now():
        authorize()
    patentJSON = getPatentJSON(patentId, patentCC, patentKC)
    return parsePatentJSON(patentJSON, patentId, patentCC, patentKC, patentTitle, patentAbstract, historicalCC)


def getPatentJSON(patentId, patentCC, patentKC):
    try:
        patentUrl =   BIBLIO_URL + patentCC  + patentId + patentKC +'/biblio,full-cycle.json'
        data = web_utils.requestHTTPS(patentUrl, ACCESS_TOKEN)
        jsonResult =  json.loads(data.decode(ENCODING))
        firstDoc = jsonResult['ops:world-patent-data']['exchange-documents']['exchange-document']
        if (type(firstDoc) is dict) and (firstDoc['@status'] == 'not found'):
            patentUrl =   BIBLIO_URL + patentCC + '.'+patentId + '.'+  patentKC +'/biblio,full-cycle.json'
            print patentUrl                    
            req = urllib2.Request(patentUrl)
            req.add_header('Authorization', 'Bearer '+ ACCESS_TOKEN)
            usock = urllib2.urlopen(patentUrl)
            data = usock.read()
            usock.close()
            jsonResult = json.loads(data.decode(ENCODING))
    except Exception, e:
        patentUrl =   BIBLIO_URL_INTERNATIONAL + patentCC  + patentId + patentKC +'/biblio,full-cycle.json'
        data = web_utils.requestHTTPS(patentUrl, ACCESS_TOKEN)
        jsonResult =  json.loads(data.decode(ENCODING))
        firstDoc = jsonResult['ops:world-patent-data']['exchange-documents']['exchange-document']
        if (type(firstDoc) is dict) and (firstDoc['@status'] == 'not found'):
            patentUrl =   BIBLIO_URL_INTERNATIONAL + patentCC + '.'+patentId + '.'+  patentKC +'/biblio,full-cycle.json'
            data = web_utils.requestHTTPS(patentUrl, ACCESS_TOKEN)
            jsonResult = json.loads(data.decode(ENCODING))
        
    return jsonResult

def getPatentFamily(patentId, patentCC, patentKC):
    
    familyUrl = FAMILY_URL
    if patentCC in ['WO', 'EP']:
        familyUrl = FAMILY_URL_INTERNATIONAL
    patentUrl =  familyUrl + patentCC  + patentId  +patentKC +'.json'    
    data = None                         
    try:
        data = web_utils.requestHTTPS(patentUrl, ACCESS_TOKEN)
    except Exception, e:
        patentUrl =  FAMILY_URL_INTERNATIONAL + patentCC + '.'  + patentId + '.' +patentKC +'.json' 
        data = web_utils.requestHTTPS(patentUrl, ACCESS_TOKEN)
    return json.loads(data.decode(ENCODING))



def parsePatentJSON(patentJSON, patentId, patentCC, patentKC, patentTitle = None, 
                        patentAbstract = None, historicalCC = None):
    patent = dict()
    

    
    appJSONBiblio = None
    patentJSONBiblio = None
    isApp = False  
    
    
    patentAbstractOriginal = ''
    
    patentDocuments = patentJSON['ops:world-patent-data']['exchange-documents']['exchange-document']

    
    if type(patentDocuments) is list:
        for patentDoc in patentDocuments:
            if patentDoc['@kind'].startswith('A'):
                appJSONBiblio = patentDoc['bibliographic-data']
                if 'abstract' in patentDoc:
                    patentAbstractOriginal = parseAbstract(patentDoc) 
            else:
                patentJSONBiblio = patentDoc['bibliographic-data']
                if 'abstract' in patentDoc:
                    patentAbstractOriginal = parseAbstract(patentDoc)  
            if appJSONBiblio is not None and patentJSONBiblio is not None:
                break
    else:
        appJSONBiblio = patentDocuments['bibliographic-data']
        patentJSONBiblio = appJSONBiblio
        isApp = True
        if 'abstract' in patentDocuments:
            patentAbstractOriginal = parseAbstract(patentDocuments)  
           
        
        
    if patentJSONBiblio is None:
        isApp = True
        patentJSONBiblio = appJSONBiblio
        
    
    priorityNumbersDates, firstPriorityNumber, pctNumberDate, originalPctNumber =\
                                                        parsePriorityClaims(patentJSONBiblio)
    
    patent['priorityDates'] = priorityNumbersDates 
    if pctNumberDate is not None:
        patent['pctNumber'] = pctNumberDate[0].strip()
        patent['pctDate'] = pctNumberDate[1].strip() 
      
        
    
    patent['mpkClasses'] = parseIPCClasses(patentJSONBiblio)  
    
    appNumber, appDate = parseAppData(patentJSONBiblio)
    if appNumber:    
        patent['appNumber'] = appNumber
    patent['appDate'] = appDate
    
    
    
    
    newPatentCC = None
    newPatentId  = None
    newPatentKC  = None
    
    
    if appJSONBiblio:
        newCC, newId, newKC, patent['appPublishedDate'] = parsePublishedData(appJSONBiblio)
        registrators, originalRegistrators = parseApplicants(appJSONBiblio)
        patent['registrators'] = formatApplicants(registrators, originalRegistrators)
        
    if not isApp:
        newPatentCC, newPatentId, newPatentKC, patent['publishedDate'] = parsePublishedData(patentJSONBiblio)
        if 'parties' in patentJSONBiblio:
            owners, originalOwners = parseApplicants(patentJSONBiblio)
            patent['owners'] = formatApplicants(owners, originalOwners)
        if (not 'owners' in patent) and ('registrators' in patent):
            patent['owners'] = patent['registrators'] 
            
    if patentTitle:
        patent['title'] =     patentTitle
    else:
        patent['title'] = parseTitle(patentJSONBiblio, appJSONBiblio)    
        
        
        
    
    
    
    if newPatentId: 
        
        patentId = newPatentId
        patentCC = newPatentCC
        patentKC = newPatentKC
        
       
    patent['patentNumber'] = patentCC + patentId + '(' +patentKC + ')'
    patent['type'] = defineType(patentCC, patentKC)
    
    
    patent['analogues'] = parseAnalogues(patentId, patentCC, patentKC)    
        
    if patentAbstract:
        patent['abstractText'] =     patentAbstract
        #patent['informationExtraction'] = information_extraction.extractInfo(patent['abstractText'], 'RU') 
    else:
        patent['abstractText'] = patentAbstractOriginal
        """if patentAbstractOriginal:
            patent['informationExtraction'] = information_extraction.extractInfo(patent['abstractText'], 'EN') 
        """
    
    
    priorityCC = historicalCC
    if firstPriorityNumber is not None:
        priorityCC = extractCC(firstPriorityNumber) 
        if not re.match('[A-Z]+', priorityCC):
            pctToUse = pctNumberDate[0]
            priorityCC = extractCC(pctToUse) 

    if (not priorityCC in [ 'EP']) and (patentCC != priorityCC):
        newAppId = None
        newAppKC = None
        
        newPatentId = None
        newPatentKC = None
        for analogue in patent['analogues']:
            newCC = extractCC(analogue)
            if newCC == priorityCC:
                print analogue
                newAppKcRes = re.match(ur'[A-Z]+?(\d+?)([ABCDT]D?\d?)', analogue)
                if newAppKcRes:
                    newAppId = newAppKcRes.group(1)
                    newAppKC = newAppKcRes.group(2)
                else:
                    newAppId = analogue.split(' ')[0][2:]
                    newAppKC = 'A'
                if newAppKC.startswith('B'):
                    newPatentId = newAppId
                    newPatentKC = newAppKC
        if newPatentId is not None:
            return parsePatentById(newPatentId, priorityCC, newPatentKC, patentTitle, patentAbstract, priorityCC)
        elif newAppId is not None:
            return parsePatentById(newAppId, priorityCC, newAppKC, patentTitle, patentAbstract, priorityCC)   
    
    return patent

def defineType(patentCC, patentKC):
    patentType = defineAppPatent(patentKC)
    russian = gettext.translation('iso3166', pycountry.LOCALES_DIR,
                              languages=['ru'])
    russian.install()
    #TODO: a separate file?
    if patentCC == 'WO':
        if patentType == u'патент на изобретение':
            return u'Мировой патент на изобретение'
        return u'Мировая заявка на изобретение'
    elif patentCC == 'EP':
        if patentType == u'патент на изобретение':
            return u'Европейский патент на изобретение'
        return u'Европейская заявка на изобретение'
    country = pycountry.countries.get(alpha2 = patentCC)    
    return russian.gettext(country.name).decode('utf-8') + ', ' + patentType

def parseIPCClasses(patentJSONBiblio):
    classifications = patentJSONBiblio['classifications-ipcr']['classification-ipcr']
    if type(classifications) is dict:
        return [formatIPC(classifications['text']['$'].replace(' ','')[0:9])]
    return [formatIPC(classification['text']['$'].replace(' ','')[0:9]) for classification in  classifications] 

def parseAppData(patentJSONBiblio):
    patentJSONReference = patentJSONBiblio['application-reference']['document-id']
    for docId in patentJSONReference:
        if docId['@document-id-type'] == 'epodoc':
            return docId['doc-number']['$'], formatDate(docId['date']['$'])
    return None, None

def parsePriorityClaims(patentJSONBiblio):
    firstNumberDate = None
    pctNumberDate = None
    originalPctNumber = None
    priorityClaims = patentJSONBiblio['priority-claims']['priority-claim']
    priorityNumbersDates = []
    isFirst = True
    isLastPCT = False
    
    if type(priorityClaims) is list:
        for priorityClaim in priorityClaims:
            for documentId in priorityClaim['document-id']:
                if type(documentId) is dict and documentId['@document-id-type'] == 'epodoc':
                    if isFirst:
                        firstNumberDate = documentId['doc-number']['$']
                        isFirst = False
                    if isInternational(documentId['doc-number']['$']):
                        pctNumberDate = documentId['doc-number']['$'], formatDate(documentId['date']['$'])
                        isLastPCT = True
                    priorityNumbersDates.append((documentId['doc-number']['$'], formatDate(documentId['date']['$'])))
                elif isLastPCT:
                    originalPctNumber =  documentId['doc-number']['$']
                    isLastPCT = False
                        
    else:
        documentId = priorityClaims['document-id']
        if type(documentId) is dict and documentId['@document-id-type'] == 'epodoc':
            if isFirst:
                firstNumberDate = documentId['doc-number']['$']
                isFirst = False
            if isInternational(documentId['doc-number']['$']):
                pctNumberDate = documentId['doc-number']['$'], formatDate(documentId['date']['$'])
                isLastPCT = True
            priorityNumbersDates.append((documentId['doc-number']['$'], formatDate(documentId['date']['$'])))
        else:
            for document in documentId:
                if document['@document-id-type'] == 'epodoc':
                    if isFirst:
                        firstNumberDate = document['doc-number']['$']
                        isFirst = False
                    if isInternational(document['doc-number']['$']):
                        pctNumberDate = document['doc-number']['$'], formatDate(document['date']['$'])
                        isLastPCT = True
                    priorityNumbersDates.append((document['doc-number']['$'], formatDate(document['date']['$'])))
                elif isLastPCT:
                    originalPctNumber =  document['doc-number']['$']
                    isLastPCT = False
                    
                
                
                
    return priorityNumbersDates, firstNumberDate, pctNumberDate, originalPctNumber
        
def parseAnalogues(patentId, patentCC, patentKC):
    familyJSON = getPatentFamily(patentId, patentCC, patentKC) 
    familyData = familyJSON['ops:world-patent-data']['ops:patent-family']['ops:family-member']
    analogues = []
    if type(familyData) is list:
        for familyMember in familyData:
            docIds = familyMember['publication-reference']['document-id']
            docKind = ''
            for docId in docIds:
                
                if docId['@document-id-type'] == 'docdb':
                    docKind = docId['kind']['$']
                else:
                    docNumber = docId['doc-number']['$'] +  docKind 
                    if not docNumber.startswith(patentCC + patentId) and (not docKind.startswith('D')):
                        docNumber = docNumber.replace('BB', 'B')
                        docNumber = docNumber.replace('DD', 'D')
                        docDate = docId['date']['$']
                        
                        analogues.append(docNumber)
                    break
                    
                    
    else:
        docIds = familyData['publication-reference']['document-id']
        docKind = ''
        for docId in docIds:
            if docId['@document-id-type'] == 'docdb':
                docKind = docId['kind']['$']
            else:
                docNumber = docId['doc-number']['$'] +  docKind 
                docNumber = docNumber.replace('BB', 'B')
                if not docNumber.startswith(patentCC + patentId):
                    docDate = docId['date']['$']
                    if docKind.startswith('A'):
                        kindToAppend = u' (заявка)'
                    else:
                        kindToAppend = u' (патент)'
                    analogues.append(docNumber + kindToAppend)
                break
    return analogues


def parsePublishedData(patentJSONBiblio):
    patentJSONReference = patentJSONBiblio['publication-reference']['document-id']
    docDate = None
    docNumber = None
    docKC = None
    docCC = None
    for docId in patentJSONReference:
        if docId['@document-id-type'] == 'docdb':
            docCC = docId['country']['$']
            docKC = docId['kind']['$'] 
            docNumber = docId['doc-number']['$'] 
        else:
            docDate = formatDate(docId['date']['$'])
    return docCC, docNumber, docKC, docDate

def parseApplicants(patentJSONBiblio):
    
    
    applicants = []
    originalApplicants = []
    if 'parties' in patentJSONBiblio:
        parties = patentJSONBiblio['parties']
    
        if 'applicants' in parties:
            patentJSONReference = parties['applicants']['applicant']
            
            for applicant in patentJSONReference:
                if applicant['@data-format'] == 'epodoc':
                    applicants.append(applicant['applicant-name']['name']['$'])
                else:
                    originalApplicants.append(applicant['applicant-name']['name']['$'])
    return applicants, originalApplicants


                
def parseTitle(patentJSONBiblio, appJSONBiblio):
    if 'invention-title' in patentJSONBiblio:
        return parseTitleFromBiblio(patentJSONBiblio)
    elif (appJSONBiblio is not None) and ('invention-title' in appJSONBiblio):
        return parseTitleFromBiblio(appJSONBiblio)
    return ''  


def parseAbstract(patentJSONBiblio):
    abstract= patentJSONBiblio['abstract']
    if type(abstract) is list:
        for abstractVariant in abstract:
            if abstractVariant['@lang'] == 'en':
                return parseAbstractParts(abstractVariant) 
        return ''
    return parseAbstractParts(abstract)
        
    

def parseAbstractParts(abstract):
    abstractParagraphs = abstract['p']
    if type(abstractParagraphs) is list:
        return ' '.join([par['$'] for par in abstractParagraphs])
    return abstractParagraphs['$']
    

def parseTitleFromBiblio(patentJSONBiblio):
    titles =    patentJSONBiblio['invention-title']
    if type(titles) is dict:
        return titles['$']
    for title in titles:
        if '@lang' in title and title['@lang'] == 'en':
            return title['$']
    return ''


    

def defineAppPatent(patentKC):
    if patentKC.startswith('A'):
        return u'заявка на изобретение'
    return u'патент на изобретение'

def isInternational(patentCC):
    return patentCC.startswith('WO')

def extractCC(patentNumber):
    return patentNumber[0:2]

def extractId(patentNumber):
    return patentNumber.split('(')[0][2:]

def extractKC(patentNumber):
    return patentNumber.split(' ')[0].split('(')[1].strip(')')


def formatApplicants(applicants, originalApplicants):
    return (','.join(applicants)).strip(',') + ' (' + (','.join(originalApplicants)).strip(',') + ')'\
                                                                    .replace('()', '')\
                                                                    .replace(',,', ',')


def formatDate(opsDate):
    normalDate =  opsDate.strip()
    return normalDate[6:] + '.' + normalDate[4:6] + '.' + normalDate[0:4]

def formatIPC(ipc):
    ipcParts = ipc.split('/')
    return ipcParts[0] + '/' + ipcParts[1][0:2]

#print parsePatentById('6190469', 'US', 'B1')

#print parsePatentById('7442268', 'US', 'B2')