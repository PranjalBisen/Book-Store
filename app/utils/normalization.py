import re

def normalize(text:str)->str:
    """Convert to lowercase and remove special characters and extra spaces"""
    if not text:
        return ""
    text=text.lower()
    text=re.sub(r'[^a-z0-9\s]','',text)
    text=re.sub(r'\s+',' ',text).strip()
    return text