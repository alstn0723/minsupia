import re
import spacy
import pandas as pd
#from spacy.training import Example

#SPACY package Load
SPACY_LOAD = spacy.load('C:/Users/trumpia/anaconda3/Lib/site-packages/en_core_web_sm/en_core_web_sm-3.1.0')

#REGEX
PHONE_REGEX = re.compile(r'([0-9]( |-|\.|,)?)?(\(?[0-9]{3}\)?)( |-|\.|,)?([0-9]{3}( |-|\.|,)?[0-9]{4})')
EMAIL_REGEX = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
ADDRESS_REGEX = re.compile(r'(?!2021)\d{3,5}(.){15,}\D\d{5}')
URL_REGEX = re.compile(r'http\S{7,}')
YEAR_REGEX = re.compile(r'((19)|(20))([0-9]{2})')
#MONTH_REGEX = re.compile(r'
DATE_REGEX_MONTH = re.compile(r'((0)?[1-9]|1[012])([-/ .])(3[01]|[12][0-9]|(0)?[1-9])')
DATE_REGEX_YEAR = re.compile(r'((0)?[1-9]|1[012])([-/ .])(3[01]|[12][0-9]|(0)?[1-9])([-/ .])(([1-9][0-9]{3})|([0-9]{2}))')
DATE_REGEX_DIGITONLY = re.compile(r'(([1-9][0-9]{3})|([0-9]{2}))((0)[1-9]|1[012])(3[01]|[12][0-9]|(0)[1-9])')
TIME_REGEX = re.compile(r'^((([0]?[1-9]|1[0-2])(:|\.)?[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$')
NEEDS = "DATE|TIME|ORDINAL"



#MESSAGE 속 PHONE 찾아서 리턴
def PHONE_EXTRACTOR(str):
    search = re.search(PHONE_REGEX, str)
    if search != None:
        result = search.group()
        return result
    else:
        return None

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

    if PHONE_EXTRACTOR(DATA) != None:
        PHONE = PHONE_EXTRACTOR(DATA)
        DATA = DATA.replace(PHONE, "")

    #SPACY의 토큰화된 자체 객체로 DATA 변환
    OBJ = SPACY_LOAD(DATA)


    print("<--  " + DATA + "  -->")


    for TOKEN in OBJ:

        #토큰 별 타입 예측
        TYPE = str(TOKEN.ent_type_)

        if str(TOKEN) == "-":
            TYPE = ""

        #길이 2인 digit DATE로 오판한 것 필터
        if (TYPE == "DATE") and (str(TOKEN).isdigit()) and (len(TOKEN) == 2):
                if int(str(TOKEN)) > 31:
                    TYPE = ""


        if (TYPE == "TIME") or (TYPE == "DATE") :
            isdigit = re.findall("\d+", str(TOKEN))
            isalpha = re.findall("[a-zA-z]+", str(TOKEN))
            # 영문 숫자 복합 토큰(대부분 띄어쓰기 안 한 경우)
            if (isdigit != []) and (isalpha != []):
                if int(isdigit[0]) > 31:
                    TYPE = ""


        #REGEX로 못찾은거 뽑기
        #DATE CLASSIFY
        if (DATE_REGEX_MONTH.match(str(TOKEN)) != None):
            TYPE = "DATE"

        if (DATE_REGEX_YEAR.match(str(TOKEN)) != None):
            TYPE = "DATE"

        #TIME CLASSIFY
        if (TIME_REGEX.match(str(TOKEN)) != None):
            MONEY_INDEX = DATA.find(str(TOKEN))

            #MONEY가 TIME_REGEX에 들어가는 경우 예외처리
            if MONEY_INDEX < 2:
                print("Amibiguous")
            if '$' in DATA[(MONEY_INDEX - 2): MONEY_INDEX]:
                TYPE = "MONEY"
            else: TYPE = "TIME"

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
        #wednesday 를 wed 에서 we'd ( we had ) 로 판단해버림

        if (TYPE in NEEDS) and (TYPE != ""):
            print(f"{TOKEN} ==> {TYPE}")

    print('----------------------------')




trm = pd.read_csv("inbound.csv", encoding='latin')
trm = trm['CONTENT']


for i in range(len(trm)):
    NER_TAG(trm[i])

NER_TAG("AutoReturn message 3587: You have reached a highly classified phone. If this message was in error, please notify us at 857-386-2000. This message will be traced and you will be contacted by one of our field agents within 24 hours. End message 3587.")
NER_TAG("i want to reservate on next Friday")
NER_TAG("Last Christmas, I was born")
NER_TAG("How about 15:00 or 9:00aM of 09/04/21?")
print(re.search(PHONE_REGEX, "AutoReturn message 3587: You have reached a highly classified phone. If this message was in error, please notify us at 857-386-2000. This message will be traced and you will be contacted by one of our field agents within 24 hours. End message 3587."))
print(re.search(PHONE_REGEX, "857-386-2000"))





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
        if len(TOKEN) > 4:git s
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