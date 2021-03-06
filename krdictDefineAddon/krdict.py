import sys
import requests
from .libs import xmltodict # type: ignore
from typing import Dict, List


APP_KEY = "REPLACE WITH YOUR OWN"

BASE_URL = "https://krdict.korean.go.kr/api"
LANGUAGE = 'en-gb'

def setKrdictKey(appKey) -> None:
    global APP_KEY
    APP_KEY = appKey

def getTargetCodes(word, appKey=None, language=LANGUAGE) -> List[str]:
    """krdict requires finding the target_code of the word"""
    if appKey is None:
        appKey = APP_KEY

    #print("getLemmas", file=sys.stderr)

    url = BASE_URL + '/search'
    r = requests.get(url,
            params={
                'key': appKey,
                'q': word,
                'sort': 'popular'
            })

    res: List[str] = []
    if not r.ok:
        raise requests.exceptions.HTTPError(response=r)
    xml = xmltodict.parse(r.text.strip())
    if 'error' in xml:
        raise requests.exceptions.HTTPError(response=r)

    items = xml["channel"]["item"]
    if not isinstance(items, list):
        item = items
        items = [item]

    for item in items:
        if item["word"] != word:
            break
        res.append(item["target_code"]);
        
    return res

def getView(targetCode, appKey=None, language=LANGUAGE) -> object:
    """returns an empty dict if the entry can't be found
    returning: {
        word: str,
        pronunciation: str, (NOT IMPL)
        etymology: {
            originalWord: str,
            originalLanguage: str
        }
        partOfSpeech: str,
        senses: List[{
            definition: str,
            example: str
        }]
    }"""
    if appKey is None:
        appKey = APP_KEY

    #print("getEntry", file=sys.stderr)

    url = BASE_URL + '/view'
    r = requests.get(url,
            params={
                'key': appKey,
                'q': targetCode,
                'method': 'target_code',
                'translated': 'y',
                'trans_lang': '1' # This is English
            })

    returning: Dict = {}
    if not r.ok:
        raise requests.exceptions.HTTPError(response=r)
    xml = xmltodict.parse(r.text.strip())
    if 'error' in xml:
        raise requests.exceptions.HTTPError(response=r)

    wordInfo = xml['channel']['item']["word_info"]

    returning['word'] = wordInfo["word"]
    returning['pronunciation'] = ""

    if 'original_language_info' in wordInfo:
        orglang = wordInfo['original_language_info'][0] \
            if isinstance(wordInfo['original_language_info'], list) \
            else wordInfo['original_language_info']
        returning['etymology'] = {
            'originalWord': orglang['original_language'],
            'originalLanguage': orglang['language_type']
        }

    partOfSpeech = wordInfo['pos']
    if isinstance(partOfSpeech, list):
        partOfSpeech = partOfSpeech[0]
    returning['partOfSpeech'] = partOfSpeech

    returning['senses'] = []
    senses = wordInfo['sense_info']
    if not isinstance(senses, list):
        sense = senses
        senses = [sense]
    for sense in senses:
        returning['senses'].append({
            'definition': sense['translation']['trans_dfn'],
            'example': sense['example_info'][0]['example'] if 'example_info' in sense else ""
        })

    return returning
