# coding=utf-8
__author__ = 'gisly'


import codecs
import re



def createPatentList(filename, readyFilename, outputFilenameNumbers, outputFilenameAll):
    patents = getPatentsFromFile(filename)
    patentIds = getPatentIdsFromFile(readyFilename)
    with codecs.open(outputFilenameNumbers, 'w', 'utf-8') as foutNumbers:
        with codecs.open(outputFilenameAll, 'w', 'utf-8') as foutAll:
            """for patent in patents:
                
                foutNumbers.write(patent['patentNum'] + '\r\n')
                              
                foutAll.write(patent['patentNum'] + '+++' +
                           patent['patentTitle'] + '+++' +
                           patent['patentBody'] + '+++' + '\r\n')"""
            for patentId in patentIds:
                foutNumbers.write(patentId + '\r\n')
                

def getPatentsFromFile(filename):
    with codecs.open(filename, 'r', 'utf-8') as fin:
        isTitle = False
        allPatents = []
        patentNum = None
        patentTitle = None
        patentBody = ''
        for line in fin:
            if line.strip()=='':
                continue
            if isPatentNum(line):
                if patentNum:
                    allPatents.append({
                                       'patentNum':patentNum,
                                       
                                       'patentTitle':patentTitle,
                                       
                                       'patentBody':patentBody,
                                       
                                       }
                                      
                                      )
                
                patentNum = formatPatentNum(line.strip())
                isTitle = True
            elif isTitle:
                patentTitle = line.strip()
                isTitle = False
                patentBody = ''
            else:
                patentBody += line.strip()
            
        allPatents.append({
                                       'patentNum':patentNum,
                                       
                                       'patentTitle':patentTitle,
                                       
                                       'patentBody':patentBody,
                                       
                                       }
                                      
                                      )
        return allPatents
    
    
def getPatentIdsFromFile(filename):
    patentIds = []
    with codecs.open(filename, 'r', 'utf-8') as fin:
        for line in fin:
            patentIds.append(formatPatentNum(line.strip()))
    return patentIds
            
    
    
def isPatentNum(line):
    return re.match('[A-Z][A-Z]', line) is not None


def formatPatentNum(patentNum):
    patentNum = patentNum.replace(' ','')
    patentNum = patentNum.replace(u'–','-')
    patentCC = patentNum[0:2]
    patentId_KCParts = patentNum[2:].split('(')
    patentId = patentId_KCParts[0]
    patentKC = patentId_KCParts[1].replace('(','').split(')')[0]
    return '#'.join([patentCC, patentId, patentKC])



createPatentList('../resources/foreignPatentsTranslations.txt', 
                 '../resources/foreignPatentsReady.txt',
                 '../resources/foreignPatentsTransformed.txt', 
                 '../resources/foreignPatentsAll.txt')
                

                
                