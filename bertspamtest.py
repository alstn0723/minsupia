import tensorflow_hub as hub
import pandas as pd
import tensorflow_text as text
import tensorflow as tf
import numpy as np



df = pd.read_csv('dataset/spam_data.csv', encoding='latin')
del df['Unnamed: 0']
df = df.reset_index(drop=True)
print(df)



print(df['SPAM'].value_counts())
df.sample(10)

#spam 1 ham 0


from sklearn.model_selection import train_test_split
X_train, X_test , y_train, y_test = train_test_split(df['CONTENT'], df['SPAM'], test_size=0.2)
print(len(X_train))
print(len(y_train))
print(len(X_test))
print(len(y_test))


bert_preprocessor = hub.KerasLayer('https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3')
bert_encoder = hub.KerasLayer('https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4')
print("model loaded")

text_input = tf.keras.layers.Input(shape = (), dtype = tf.string, name = 'Inputs')
preprocessed_text = bert_preprocessor(text_input)
embeed = bert_encoder(preprocessed_text)
dropout = tf.keras.layers.Dropout(0.1, name = 'Dropout')(embeed['pooled_output'])
outputs = tf.keras.layers.Dense(1, activation = 'sigmoid', name = 'Dense')(dropout)

model = tf.keras.Model(inputs = [text_input], outputs = [outputs])

model.summary()

Metrics = [tf.keras.metrics.BinaryAccuracy(name = 'accuracy'),
           tf.keras.metrics.Precision(name = 'precision'),
           tf.keras.metrics.Recall(name = 'recall')
           ]


model.compile(optimizer ='adam',
               loss = 'binary_crossentropy',
               metrics = Metrics)

history = model.fit(X_train, y_train, epochs = 10)
model.save('bert_model.h5')
print(model.evaluate(X_test,y_test))

y_pred = model.predict(X_test)
y_pred = y_pred.flatten() # require to be in one-dimensional array , for easy manipulation

predict_text = [
                # Spam
                'We’d all like to get a $10,000 deposit on our bank accounts out of the blue, but winning a prize—especially if you’ve never entered a contest',
                'Netflix is sending you a refund of $12.99. Please reply with your bank account and routing number to verify and get your refund',
                'Your account is temporarily frozen. Please log in to to secure your account ',
                #ham
                'The article was published on 18th August itself',
                'Although we are unable to give you an exact time-frame at the moment, I would request you to stay tuned for any updates.',
                'The image you sent is a UI bug, I can check that your article is marked as regular and is not in the monetization program.'
]

test_results = model.predict(predict_text)

print(test_results)