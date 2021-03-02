import sys
import requests
import xmltodict # type: ignore
from typing import Dict, List

APP_KEY = "REPLACE WITH YOUR OWN"

base_url = "https://krdict.korean.go.kr/api"
language = 'en-gb'

def setOxfordKey(app_key) -> None:
    global APP_KEY
    APP_KEY = app_key

def getTargetCodes(word, app_key=None, language=language) -> List[str]:
    """krdict requires finding the target_code of the word"""
    if app_key is None:
        app_key = APP_KEY

    #print("getLemmas", file=sys.stderr)

    url = base_url + '/search'
    r = requests.get(url,
            params={
                'key': app_key,
                'q': word
            })

    res: List[str] = []
    if not r.ok:
        raise requests.exceptions.HTTPError(response=r)

    items = xmltodict.parse(r.text)["channel"]["item"]
    if not isinstance(items, list):
        item = items
        items = [item]

    for item in items:
        if item["word"] != word:
            break
        res.append(item["target_code"]);
        
    return res

def getView(target_code, app_key=None, language=language) -> object:
    """returns an empty dict if the entry can't be found
    returning: {
        word: str,
        pronunciation: str, (NOT IMPL)
        etymology: {
            originalWord: str,
            originalLanguage: str
        }
        partOfSpeech: str,
        definition: str,
    }"""
    if app_key is None:
        app_key = APP_KEY

    #print("getEntry", file=sys.stderr)

    url = base_url + '/view'
    r = requests.get(url,
            params={
                'key': app_key,
                'q': target_code,
                'method': 'target_code',
                'translated': 'y',
                'trans_lang': '1' # This is English
            })

    returning: Dict = {}
    if not r.ok:
        raise requests.exceptions.HTTPError(response=r)
    xml = xmltodict.parse(r.text)
    if 'error' in xml:
        raise requests.exceptions.HTTPError(response=r)

    wordInfo = xml['channel']['item']["word_info"]

    returning['word'] = wordInfo["word"]
    returning['pronunciation'] = ""

    if 'original_language_info' in wordInfo:
        orglang = wordInfo['original_language_info']
        returning['etymology'] = {
            'originalWord': orglang['original_language'],
            'originalLanguage': orglang['language_type']
        }

    partOfSpeech = wordInfo['pos']
    if isinstance(partOfSpeech, list):
        partOfSpeech = partOfSpeech[0]
    returning['partOfSpeech'] = partOfSpeech

    returning['definition'] = wordInfo['sense_info']['translation']['trans_dfn']

    return returning
