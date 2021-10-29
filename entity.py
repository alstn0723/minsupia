import re
import spacy
import pandas as pd
import flask_reqparse as reqparse
from flask import Flask
#from spacy.training import Example

#SPACY package Load
SPACY_LOAD = spacy.load('C:/Users/trumpia/anaconda3/Lib/site-packages/en_core_web_sm/en_core_web_sm-3.1.0')

#REGEX
EMAIL_REGEX = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
ADDRESS_REGEX = re.compile(r'\d{3,5}(.){15,}\D\d{5}')
URL_REGEX = re.compile(r'http\S{7,}')
YEAR_REGEX = re.compile(r'((19)|(20))([0-9]{2})')
DATE_REGEX_MONTH = re.compile(r'((0)?[1-9]|1[012])([-/ .])(3[01]|[12][0-9]|(0)?[1-9])')
DATE_REGEX_YEAR = re.compile(r'((0)?[1-9]|1[012])([-/ .])(3[01]|[12][0-9]|(0)?[1-9])([-/ .])(([1-9][0-9]{3})|([0-9]{2}))')
DATE_REGEX_DIGITONLY = re.compile(r'(([1-9][0-9]{3})|([0-9]{2}))((0)[1-9]|1[012])(3[01]|[12][0-9]|(0)[1-9])')
TIME_REGEX = re.compile(r'^((([0]?[1-9]|1[0-2])(:|\.)?[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$')
NEEDS = "PERSON|DATE|TIME|ORDINAL"


#MESSAGE 속 URL 찾아서 리턴
def URL_EXTRACTOR(str):
    search = re.search(URL_REGEX, str)
    if search != None:
        result = search.group()
        return result
    else:
        return None

#MESSAGE 속 주소를 찾아서 리턴
def ADDRESS_EXTRACTOR(str):
    search = re.search(ADDRESS_REGEX, str)
    if search != None:
        result = search.group()
        return result
    else:
        return None


def NER_TAG(DATA):

    if URL_EXTRACTOR(DATA) != None:
        URL = URL_EXTRACTOR(DATA)
        DATA = DATA.replace(URL, "")

    if ADDRESS_EXTRACTOR(DATA) != None:
        ADDRESS = ADDRESS_EXTRACTOR(DATA)
        DATA = DATA.replace(ADDRESS, "")


    #SPACY의 토큰화된 자체 객체로 DATA 변환
    OBJ = SPACY_LOAD(DATA)


    print("<--  " + DATA + "  -->")


    for TOKEN in OBJ:

        #토큰 별 타입 예측
        TYPE = TOKEN.ent_type_


        #REGEX로 2차 필터링
        #DATE CLASSIFY
        if (DATE_REGEX_MONTH.match(str(TOKEN)) != None) or (DATE_REGEX_YEAR.match(str(TOKEN)) != None):
            TYPE = "DATE"

        #TIME CLASSIFY
        if (TIME_REGEX.match(str(TOKEN)) != None):
            TYPE = "TIME"

        #DIGITONLY CLASSIFY
        if str(TOKEN).isdigit():
            if len(TOKEN) > 4:
                if ((len(TOKEN) == 6) or (len(TOKEN) == 8)):
                    if DATE_REGEX_DIGITONLY.match(str(TOKEN)) != None:
                        TYPE = "DATE"
                    else:
                        TYPE = "CARDINAL"
                else:
                    TYPE = "CARDINAL"
            if len(TOKEN) == 4:
                if YEAR_REGEX.match(str(TOKEN)) != None:
                    TYPE = "DATE"
                else:
                    TYPE = "CARDINAL"


        #해야 할 일
        #OCT 20 같은거 처리
        # wednesday 를 wed 에서 we d 로 판단해버림

        if (TYPE in NEEDS) and (TYPE != ""):
            print(f"{TOKEN} ==> {TYPE}")




data = pd.read_csv("inbound.csv", encoding='latin')
data = data['CONTENT']
NER_TAG(data[1564])

#for Test
'''

doc = SPACY_LOAD("Oct Wed wedding Thu Tue wed WED")

for TOKEN in doc:

    TYPE = TOKEN.ent_type_

    if (DATE_REGEX_MONTH.match(str(TOKEN)) != None) or (DATE_REGEX_YEAR.match(str(TOKEN)) != None):
        TYPE = "DATE"

    if (TIME_REGEX.match(str(TOKEN)) != None):
        TYPE = "TIME"


    print(TOKEN)
    #DIGIT CLASSIFY
    if str(TOKEN).isdigit():
        if len(TOKEN) > 4:
            if ((len(TOKEN) == 6) or (len(TOKEN) == 8)):
                if DATE_REGEX_DIGITONLY.match(str(TOKEN)) != None:
                    TYPE = "DATE"
                else:
                    TYPE = "CARDINAL"
            else:
                TYPE = "CARDINAL"
        if len(TOKEN) == 4:
            if YEAR_REGEX.match(str(TOKEN)) != None:
                TYPE = "DATE"
            else:
                TYPE = "CARDINAL"

    # wednesday 를 wed 에서 we d 로 판단해버림;
    #OCT 20 같은거 처리
    #PERSON 도 조금만 더 올릴 방법 없나
    

    if (TYPE in NEEDS) and (TYPE != ""):
        print(f"{TOKEN} ==> {TYPE}")


'''