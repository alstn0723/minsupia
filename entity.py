import datetime

import datefinder
import dateutil.parser as dp

import re
import spacy
import pandas as pd
data = pd.read_csv("inbound.csv", encoding='latin')
data = data['CONTENT']
SPACY_LOAD = spacy.load('C:/Users/trumpia/anaconda3/Lib/site-packages/en_core_web_sm/en_core_web_sm-3.1.0')




def refine_pattern_start_end(pattern: str) -> str:
    """
    The updated Regex pattern doesn't allow alpha characters prepended or appended
    to the match.
    :param pattern: monday|tuesday
    :return: (?<![^\W\d_])monday(?![^\W\d_])|(?<![^\W\d_])tuesday(?![^\W\d_])
    """
    return '|'.join([fr'(?<![^\W\d_]){p}(?![^\W\d_])' for p in pattern.split('|')])

DAYS_PATTERN = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun'
DAYS_PATTERN = refine_pattern_start_end(DAYS_PATTERN)
MONTHS_PATTERN = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec'
MONTHS_PATTERN = refine_pattern_start_end(MONTHS_PATTERN)
NUM_PATTERN = r'[1-3]?[0-9]'





for i in range(len(data)):
    
    ORIGINAL_DATA = data[i]
    SPACY_DATA = SPACY_LOAD(data[i])

    CHECKER = 0

    for token in SPACY_DATA:
        if (token.ent_type_ == 'DATE') or (token.ent_type_ == 'CARDINAL'):
            print(f"{token} ==> {token.ent_type_}")
            CHECKER += 1

    if CHECKER != 0:

        NUM_FIND = re.findall(NUM_PATTERN, ORIGINAL_DATA)
        MONTHS_FIND = re.findall(MONTHS_PATTERN, ORIGINAL_DATA)
        DAYS_FIND = re.findall(DAYS_PATTERN, ORIGINAL_DATA)

        matches = datefinder.find_dates(ORIGINAL_DATA)
        LISTED_MATCH = list(matches)
        
        if len(NUM_FIND) == 1:
            
            if len(MONTHS_FIND) > 0:

                if len(LISTED_MATCH) != 0:
                    
                    for i in reversed(range(len(LISTED_MATCH))):
                        MATCH_YEAR = LISTED_MATCH[i].year
                        
                        if not(1970 < MATCH_YEAR < 2025):
                            del LISTED_MATCH[i]
                    print('----------------')
                    print("Data number ", i + 2)
                    print("Original data : ", data[i])
                    for match in matches:
                        print("match found :", match)
                    print('----------------')
                
                else:
                    print('----------------')
                    print("Original data : ", data[i])
                    print("DATETIME NOT FOUND.")
                    print('----------------')
                    
            else:
                print('----------------')
                print("Original data : ", data[i])
                print("DATETIME NOT FOUND.")
                print('----------------')
    
        else:
            
            matches = datefinder.find_dates(ORIGINAL_DATA)
            
            if len(LISTED_MATCH) != 0:
                
                print('----------------')
                print("Data number ", i+2)
                print("Original data : ", data[i])
                for match in matches:
                    print("match found :", match)
                print('----------------')
                
            else:
                print('----------------')
                print("Original data : ", data[i])
                print("DATETIME NOT FOUND.")
                print('----------------')

DIGITS_MODIFIER_PATTERN = r'\d+st|\d+th|\d+rd|first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|next|last'
DIGITS_PATTERN = r'\d{1,4}'

