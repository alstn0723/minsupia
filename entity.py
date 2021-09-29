import datefinder
import dateutil.parser as dp

import re
import spacy
import pandas as pd
data = pd.read_csv("inbound.csv", encoding='latin')
data = data['CONTENT']
nlp = spacy.load('C:/Users/trumpia/anaconda3/Lib/site-packages/en_core_web_sm/en_core_web_sm-3.1.0')
doc = nlp("Google Apple $ 5.1 billion Wednesday Korea America USA baseball")
def  ner_tag(sentence):
    sentence = nlp(sentence)
    for e in sentence:
        if e.ent_type_ == "PERSON":
            print(f"{e} ==> {e.ent_type_}")

    return

data2 = pd.read_csv("finset.csv")
del data2['Unnamed: 0']
data2 = data2.reset_index(drop=True)
data3 = data2['CONTENT']
print(len(data2))
for i in reversed(range(len(data2))):
    if (type(data3[i]) == float):
        data2 = data2.drop([i])
        continue
    if any(c.isalpha() for c in data3[i]) == False:
        del data2[i]
data2 = data2.reset_index(drop=True)
data2.to_csv("final.csv", mode='w')

'''
for i in range(len(data)):
    print('-----------------------')
    print(data[i])
    ner_tag(data[i])
    print('-----------------------')
'''

'''
matches = datefinder.find_dates("9/29 is Wednesday .Do you mean Tuesday 9/28 or Wednesday 9/29 ??")
for match in matches:
    print("match found ",match)


def refine_pattern_start_end(pattern: str) -> str:
    """
    The updated Regex pattern doesn't allow alpha characters prepended or appended
    to the match.
    :param pattern: monday|tuesday
    :return: (?<![^\W\d_])monday(?![^\W\d_])|(?<![^\W\d_])tuesday(?![^\W\d_])
    """
    return '|'.join([fr'(?<![^\W\d_]){p}(?![^\W\d_])' for p in pattern.split('|')])

DIGITS_MODIFIER_PATTERN = r'\d+st|\d+th|\d+rd|first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|next|last'
DIGITS_PATTERN = r'\d{1,4}'
DAYS_PATTERN = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun'
DAYS_PATTERN = refine_pattern_start_end(DAYS_PATTERN)
MONTHS_PATTERN = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec'
MONTHS_PATTERN = refine_pattern_start_end(MONTHS_PATTERN)
'''