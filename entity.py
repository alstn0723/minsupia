import re
import spacy
import pandas as pd
from spacy.training import Example

data = pd.read_csv("inbound.csv", encoding='latin')
data = data['CONTENT']
SPACY_LOAD = spacy.load('C:/Users/trumpia/anaconda3/Lib/site-packages/en_core_web_sm/en_core_web_sm-3.1.0')

#REGEX
EMAIL_REGEX = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
ADDRESS_REGEX = re.compile(r'\d{3,5}(.){15,}\D\d{5}')
URL_REGEX = re.compile(r'http\S{7,}')
DATE_REGEX1 = re.compile(r'((0)?[1-9]|1[012])([-/ .])(3[01]|[12][0-9]|(0)?[1-9])')
DATE_REGEX2 = re.compile(r'((0)?[1-9]|1[012])([-/ .])(3[01]|[12][0-9]|(0)?[1-9])([-/ .])(([1-9][0-9]{3})|([0-9]{2}))')
TIME_REGEX = re.compile(r'^((([0]?[1-9]|1[0-2])(:|\.)?[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$')
NEEDS = "PERSON|DATE|TIME|CARDINAL|ORDINAL"






def URL_EXTRACTOR(str):
    search = re.search(URL_REGEX, str)
    if search != None:
        result = search.group()
        return result
    else:
        return None

def ADDRESS_EXTRACTOR(str):
    search = re.search(ADDRESS_REGEX, str)
    if search != None:
        result = search.group()
        return result
    else:
        return None



for i in range(len(data)):

    if URL_EXTRACTOR(data[i]) != None:
        URL = URL_EXTRACTOR(data[i])
        data[i] = data[i].replace(URL, "")

    if ADDRESS_EXTRACTOR(data[i]) != None:
        ADDRESS = ADDRESS_EXTRACTOR(data[i])
        data[i] = data[i].replace(ADDRESS, "")



    doc = SPACY_LOAD(data[i])
    print('---------------------------------')
    print("Data No. {0}".format(i))
    print("<-- Original = " + data[i] + " -->")


    for e in doc:

        TYPE = e.ent_type_

        if (DATE_REGEX1.match(str(e)) != None) or (DATE_REGEX2.match(str(e)) != None):
            TYPE = "DATE"

        if (TIME_REGEX.match(str(e)) != None):
            TYPE = "TIME"

        #DATE 중에서 only digit, 길이 6 이하 제한, yyyymmdd 포맷 안지켜진거 다 태그 제거
        #OCT 20 같은거 처리
        #PERSON 도 조금만 더 올릴 방법 없나

        if (TYPE in NEEDS) and (TYPE != ""):
            print(f"{e} ==> {TYPE}")

