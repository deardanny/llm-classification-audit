"""Quote presence is necessary, not proof of semantic support."""
import re

PUNCT=str.maketrans({'’':"'",'‘':"'",'“':'"','”':'"'})

def normalize(text):
    return re.sub(r'\s+',' ',text.translate(PUNCT)).strip()

def quote_present(quote,text):
    return isinstance(quote,str) and bool(normalize(quote)) and normalize(quote) in normalize(text)
