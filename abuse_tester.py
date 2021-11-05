import abuse_base as ab
from tensorflow.keras.preprocessing.sequence import pad_sequences

def ACC_Check(sentence):

    MODEL, BOW = ab.Load_Model('Abuse_Detect.h5', 'Abuse_Tokenizer.pickle')

    tokens = ab.Preprocess_Predict(sentence)
    token_score = []

    encoded = BOW.texts_to_sequences([tokens]) # 정수 인코딩
    pad_new = pad_sequences(encoded, 20) # 패딩
    total_score = float(MODEL.predict(pad_new)) # 예측

    for i in range(len(tokens)):
        encoded = BOW.texts_to_sequences([tokens[i]])  # 정수 인코딩
        pad_new = pad_sequences(encoded, 20)  # 패딩
        score = float(MODEL.predict(pad_new))
        score = str(round(score * 100, 2))# 예측
        token_score.append(score)



    if(total_score > 0):
        print("DATA total score : {0} ".format(round(total_score * 100, 4)))
        print(sentence)
        for i in range(len(tokens)):
            print("{0}  ==>  {1}".format(tokens[i], token_score[i]))



ACC_Check("val_acc did not improve from")