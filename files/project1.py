import nltk
import math
import pandas as pd

nltk.download('punkt') # Needs to download thing to use tokenizer function

def computeTF(tokens):
    tfDict = {}
    for token in tokens: # Loop through all tokens
        if not token in tfDict: #If key doesn't exist, make new key and set to 1
            tfDict[token] = 1
        else: #If key already exists, increment key
            tfDict[token] = tfDict[token] + 1
    for key in tfDict: #Once all tokens are counted, compute TF score for each token in the document
        tfDict[key] = tfDict[key] / float(len(tokens))
    return tfDict

def computeIDF(files):
    idfDict = {}
    fileNum = len(files)

    for doc in files:
        for token, score in doc.items():
            if score > 0:
                idfDict[token] += 1

    for token, score in idfDict.items():
        idfDict[token] = math.log10(fileNum / float(score))

    return idfDict

def computeTFIDF(tfScores, idfScores):
    tfidf = {}

    for token, tfScore in tfScores:
        tfidf[token] = tfScore * idfScores[token]

    return tfidf

# Main
tfScores = []
idfScore = {}
tfidfScores = []

fileDict = []
tokenSet = set()

for x in range(10):
    string = open('Data_%d.txt' % (x + 1), 'r').read() #Get data from one file
    tokens = nltk.word_tokenize(string) #Create tokens, this gives an array
    tfScores.append(computeTF(string))
    fileDict.append(tokens)
    tokenSet = tokenSet.union(tokens);

wordDict = dict.fromkeys(tokenSet, 0)
tfScores.append(computeTF(wordDict))

#print (tfScores)
idfScore = computeIDF(tokenSet)


'''
# Compute TF Score for each document
for tokens in files:
    tfScores.append(computeTF(tokens))

for tfScore in tfScores:
    tfidfScores.append(computeTFIDF(tfScore, idfScores))
pd.DataFrame([tfidfScoresA, tfidfScoresB])

#idfScores = computeIDF(files)
#tfidfScores = computeTFIDF(tfScores, idfScores)
#print(tfidfScores)
'''
