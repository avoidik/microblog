import json
import requests
from flask_babel import _
from app import app

def translate(text, source_lang, dest_lang):
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _("Error: translation service is not configured.")
    auth = {"Ocp-Apim-Subscription-Key": app.config['MS_TRANSLATOR_KEY']}
    r = requests.get("https://api.microsofttranslator.com/v2/Ajax.svc/Translate?text={}&from={}&to={}". \
                    format(text, source_lang, dest_lang), headers=auth)
    if r.status_code != 200:
        return _("Error: translation service has failed.")
    return json.loads(r.content.decode("utf-8-sig"))