import tensorflow_hub as hub
import pandas as pd
import tensorflow_text as text
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

df = pd.read_csv('/dataset/spam_data.csv')

df.head()

#분리
df_spam = df[df['Category']=='spam']
df_ham = df[df['Category']=='ham']

print("Ham Dataset Shape:", df_ham.shape)

print("Spam Dataset Shape:", df_spam.shape)

df_ham_downsampled = df_ham.sample(df_spam.shape[0])
df_ham_downsampled.shape

df_balanced = pd.concat([df_spam , df_ham_downsampled])

df_balanced['Category'].value_counts()
df_balanced.sample(10)

#spam 1 ham 0
df_balanced['spam'] = df_balanced['Category'].apply(lambda x:1 if x=='spam' else 0)
df_balanced.sample(4)

from sklearn.model_selection import train_test_split
X_train, X_test , y_train, y_test = train_test_split(df_balanced['Message'], df_balanced['spam'], stratify = df_balanced['spam'])

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

print(model.evaluate(X_test,y_test))

y_pred = model.predict(X_test)
y_pred = y_pred.flatten() # require to be in one-dimensional array , for easy manipulation
