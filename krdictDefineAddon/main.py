import os
import sys
import json

from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo, tooltip
from requests.exceptions import HTTPError

from .krdict import setKrdictKey, getTargetCodes, getView

KEY_FIELD = 0 # already contains word and must append audio
DEFINITION_FIELD = 1
PRIMARY_SHORTCUT = "ctrl+alt+k"
FORMAT = "full"

def insertDefinition(editor):
    # Get the word
    orgWord = ""
    try:
        orgWord = editor.note.fields[0]
        if orgWord == "" or orgWord.isspace():
            raise KeyError() # Purely to jump to the tooltip here
    except (AttributeError, KeyError) as e:
        tooltip("KrdictDefine: No text found in note fields.")
        return

    try:
        words = [getView(targetCode) for targetCode in getTargetCodes(orgWord)]
    except (HTTPError, KeyError) as e:
        tooltip(f"KrdictDefine: Could not find root words for {orgWord} or API key unauthorized")
        return

    # Format word
    definition = ""
    soundURLs = set()
    for word in words:
        ########## Definition format ##########
        definition += '<hr>'
        definition += '<b>' + word['partOfSpeech'] + '.</b><br>'

        if word['pronunciation']: # sounds saved for later
            soundURLs.add(word['pronunciation'])

        for sense in word['senses']:
            definition += '<p>'
            if sense['word']:
                definition += sense['word'] + '<br>'
            if FORMAT == "full":
                definition += sense['definition'] + '<br>'
                if sense['example']:
                    definition += '<b>e.g.</b> ' + '"' + sense['example'] + '"' + '<br>'
                definition += '</p>'

        if FORMAT == "full" and 'etymology' in word:
            etymology = word['etymology']
            definition += '<h5>Origins: ' + etymology['originalLanguage'] + '</h5>'
            definition += etymology['originalWord'] + '<br>'

    ############# Output ##############
    sounds = [editor.urlToLink(url).strip() for url in soundURLs]
    editor.note.fields[KEY_FIELD] = orgWord + ''.join(sounds)
    editor.note.fields[DEFINITION_FIELD] = definition
    editor.loadNote()

    # Focus back on zero field
    if editor.web:
        editor.web.eval("focusField(0);")

def addMyButton(buttons, editor):
    oxfordButton = editor.addButton(icon=os.path.join(os.path.dirname(__file__), "images", "korean_flag.ico"),
                                    cmd="krDict",
                                    func=insertDefinition,
                                    tip=f"krdict Define Word {PRIMARY_SHORTCUT}",
                                    toggleable=False,
                                    label="",
                                    keys=PRIMARY_SHORTCUT,
                                    disables=False)
    buttons.append(oxfordButton)
    return buttons

addHook("setupEditorButtons", addMyButton)

config = mw.addonManager.getConfig(__name__) # type: ignore
setKrdictKey(config["APP_KEY"]) # type: ignore
FORMAT = config["FORMAT"] # type: ignore
