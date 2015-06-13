# coding=utf-8
__author__ = 'gisly'
import requests
from base64 import b64encode

AUTH_URL = 'https://ops.epo.org/3.1/auth/accesstoken'
KEY = 'mGBQRejZe7vpxGxZQD6bfgehwq7OCBMD'
SECRET = 'q4CYSLfGaGUnKnvn'

CURRENT_TOKEN = None



def acquire_token():
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
    responseJson = response.json()
    return responseJson['access_token'], datetime.now() + \
            timedelta(seconds=int(responseJson['expires_in'])

