from tensorflow.keras.models import load_model
from nltk.corpus import stopwords
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re, pickle
import pandas as pd


stop_words = set(stopwords.words('english'))

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)



loaded_model = load_model('best_model.h5')

def sentiment_predict(sentence):

    sentence = sentence.lower()  # 소문자로 변환
    tokens = sentence.split(' ')  # 공백 기준 스플릿
    for i in reversed(range(len(tokens))):
        if '@' in tokens[i]:
            del tokens[i]
        elif '&' in tokens[i]:
            del tokens[i]
        elif 'http' in tokens[i]:
            del tokens[i]
        elif '#' in tokens[i]:
            del tokens[i]
        else:
            tokens[i] = re.sub(r"[^a-zA-Z ]", " ", tokens[i])

    tokens = ' '.join(tokens)
    tokens = tokens.split(' ')

    tokens = [word for word in tokens if not word in stop_words]  # 불용어 제거

    for i in reversed(range(len(tokens))):
        # 불용어 처리 이후 남은 null 제거
        if tokens[i] == '':
            del tokens[i]
        # 길이 1인 찌꺼기 제거
        elif len(tokens[i]) < 3:
            del tokens[i]

    print(tokens)

    encoded = tokenizer.texts_to_sequences([tokens]) # 정수 인코딩
    pad_new = pad_sequences(encoded, 12) # 패딩
    score = float(loaded_model.predict(pad_new)) # 예측

    if(score > 0.5):
        print("{:.2f}% 확률로 욕설 포함.\n".format(score * 100))

    else:
        print("{:.2f}% 확률로 욕설 미포함.\n".format((1 - score) * 100))



sentiment_predict("bitch check my profile fuck you")
sentiment_predict("bitches in beach shit")
sentiment_predict("i love my job and payment")
sentiment_predict("today's lunch menu is noodle")
sentiment_predict("Oh man...was ironing @jeancjumbe's fave top to wear to a meeting. Burnt it ")
sentiment_predict("Almost died! My pant leg got caught in my bike chain while riding ")
sentiment_predict("Morninnn! Gotta do the piano bitch course in an hour, still sleepy.. Don't get much of sleep lastnight, had trouble sleeping ugh.. ")
sentiment_predict("marks this day with sadness faggot ang regret--my first and only iPod is officially missing. ")
sentiment_predict("@hexmurda that shit ")
