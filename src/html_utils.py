# coding=utf-8
__author__ = 'gisly'

import urllib2
import urllib
import re, urlparse


import lxml.html
from HTMLParser import HTMLParser


from lxml import etree

htmlParser = HTMLParser()

"""
creates a string out of HTML
"""
def htmlToString(html):
    return lxml.html.tostring(html)

"""
returns HTML from a URL
"""
def getHTMLData(url, encoding, paramDict, isProxy = False):
    if paramDict:
        encodedParams = urllib.urlencode(paramDict)
    else:
        encodedParams = None
    urlData = getURLData(url, encoding, encodedParams, isProxy)
    if urlData:
        return lxml.html.document_fromstring(urlData)
    return None

def getURLData(url,encoding, encodedParams, isProxy = False):
    try:
        if encodedParams:
            url = url + '?%s'%encodedParams
        urlEncoded = iriToUri(url)
        
        print urlEncoded
        print 'isProxy:' + str(isProxy)
        
        """if isProxy:
            proxy_support = urllib2.ProxyHandler({"http":"194.154.74.210:8080"})
            opener = urllib2.build_opener(proxy_support)
            urllib2.install_opener(opener)"""

        usock = urllib2.urlopen(urlEncoded)
        data = usock.read()
        usock.close()
        return data.decode(encoding)
    except Exception, e:
        print str(e)
        return None

"""utulity functions for processing various xpath conditions"""

def getHTMLAttributeByAttribute(html, tagName, conditionAttribute, conditionValue, targetAttribute):
    resultsFound = html.xpath('.//'+tagName+'[@'+conditionAttribute+'="'+conditionValue+'"]/@'+targetAttribute)
    if resultsFound:
        return resultsFound[0]
    return None


def getFirstHTMLTag(html,tagName):
    results = html.xpath('.//'+tagName)
    if results:
        return results[0]
    return None

def getFirstHTMLTagByAttribute(html,tagName,attrName, attrValue):
    results = html.xpath('.//'+tagName+'[@'+attrName+'="'+attrValue+'"]')
    if results:
        return results[0]
    return None


def getChildrenByParentTagAttribute(html,tagName,attrName, attrValue):
    return html.xpath('.//'+tagName+'[@'+attrName+'="'+attrValue+'"]/child::node()')



def getHTMLAttribute(html, tagName, targetAttribute):
    resultsFound = html.xpath('.//'+tagName+'/@'+targetAttribute)
    if resultsFound:
        return resultsFound[0]
    return None


def getAllLinksByTag(html, tagName, attributeName, attributeValue):
    return html.xpath('.//'+tagName+'[@'+attributeName+'="'+attributeValue+'"]/a/@href')

def getHTMLTagsByAttribute(html,tagName,attrName, attrValue):
    return html.xpath('.//'+tagName+'[@'+attrName+'="'+attrValue+'"]')

def getAllTagsByAttribute(html, attrName, attrValue):
    return html.xpath('.//*[@'+attrName+'="'+attrValue+'"]')


def getHTMLTags(html,tagName):
    return html.xpath('.//'+tagName)

def getHTMLAttributesByAttribute(html,tagName,attrName, attrValue, targetAttribute):
    return html.xpath('.//'+tagName+'[@'+attrName+'="'+attrValue+'"]/@' + targetAttribute)


def createString(html):
    return etree.tostring(html)


def getParams(URL):
    toSearchIn  = URL
    if '?' in toSearchIn:
        toSearchIn = toSearchIn.split('?')[1]
    keyValuePairs = toSearchIn.split('&')
    paramDict = dict()
    for keyValuePair in keyValuePairs:
        keyValue = keyValuePair.split('=')
        paramDict[keyValue[0]] = keyValue[1]
    return paramDict

"""
handling some URI problems
"""

#http://stackoverflow.com/questions/4389572/how-to-fetch-a-non-ascii-url-with-python-urlopen
def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )
#http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

"""
strips tags
"""
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

"""
unescapes text from an html string
"""
def unescape(html):
    return htmlParser.unescape(html)


def getHTTPLinkLastPart(httpLink):
    return httpLink.strip('/').split('/')[-1].split('.')[0]

"""
normalizes html data:
-strips tags
-unescapes the text
"""
def normalize(htmlData):
    return strip_tags(unescape(htmlData))

