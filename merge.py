import pandas as pd
import re


#csv파일 로드, Null 데이터 삭제
def loadcsv(directory):
    data = pd.read_csv(directory, encoding='latin', low_memory=False)
    data.drop_duplicates(subset=['CONTENT'], inplace=True)
    data = data['CONTENT']
    data.dropna(inplace=True)
    data = data.reset_index(drop=True)

    print("CSV file loaded.")

    return data


#정제화 함수
def refinery(list):
    for i in reversed(range(len(list))):

        list[i] = list[i].split(' ')

        for j in reversed(range(len(list[i]))):
            if '@' in list[i][j]:
                del list[i][j]
            elif '&' in list[i][j]:
                del list[i][j]
            elif 'RT' in list[i][j]:
                del list[i][j]
            elif 'http' in list[i][j]:
                del list[i][j]
            elif '#' in list[i][j]:
                del list[i][j]


        list[i] = ' '.join(list[i])
        list[i] = list[i].replace('\n', ' ')
        list[i] = re.sub(r"[^a-zA-Z ]", " ", list[i])

        print("{0}번 data done.".format(i))

    return list


#태깅
def tagging(series, tag):
    frame = series.to_frame(name='CONTENT')
    frame.insert(1, 'ABUSE', tag)

    return frame

def main():
    #욕설 트윗
    abuse = loadcsv("abuse_twt.csv")
    #trumpia outbound
    normal = loadcsv("normal_sms.csv")

    abuse = refinery(abuse)
    normal = refinery(normal)

    abuse_tag = tagging(abuse, '1')
    normal_tag = tagging(normal, '0')

    extracted = pd.concat([abuse_tag, normal_tag])
    extracted.dropna(inplace=True)
    extracted = extracted.reset_index(drop=True)
    extracted.to_csv("extracted1.csv", mode='w')
    print(extracted)


'''
hi = pd.read_csv("extracted1.csv")
plus = pd.read_csv("normal_sms2.csv")
plus = plus['CONTENT']
plus.dropna(inplace=True)
plus = plus.reset_index(drop=True)
plus = refinery(plus)
plus_tag = tagging(plus, '0')
print(plus_tag)
del hi['Unnamed: 0']

extracted = pd.concat([hi, plus_tag])
extracted.dropna(inplace=True)
extracted = extracted.reset_index(drop=True)
extracted.to_csv("extracted2.csv", mode='w')
print(extracted)


'''


yok = loadcsv("abuse_twt.csv")
yok = refinery(yok)
yok = tagging(yok, 1)
noyok = pd.read_csv("steelo.csv")
del noyok["Unnamed: 0"]
print(noyok)
print(yok)
finset = pd.concat([yok, noyok])
finset.dropna(inplace=True)
finset = finset.reset_index(drop=True)
finset.to_csv("finset.csv", mode='w')