# coding=utf-8
__author__ = 'gisly'

from base64 import b64encode
import requests
import urllib2

def requestHTTPS(url, accessToken):
    print url
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Bearer '+ accessToken)
    usock = urllib2.urlopen(req)
    data = usock.read()
    usock.close()
    return data
    