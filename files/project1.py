import nltk
import math
import pandas as pd

nltk.download('punkt') # Needs to download thing to use tokenizer function

def computeTF(tokenCount, tokens):
    tfDict = {}
    tokenNum = len(tokens)

    for key, count in tokenCount.items(): #Once all tokens are counted, compute TF score for each token in the document
        tfDict[key] = count / float(tokenNum)

    return tfDict

def computeIDF(files):
    idfDict = dict.fromkeys(files[0].keys(), 0)
    fileNum = len(files)

    for data in files:
        for token, score in data.items():
            if score > 0:
                idfDict[token] += 1

    for token, score in idfDict.items():
        idfDict[token] = math.log10(fileNum / float(score))

    return idfDict

def computeTFIDF(tfScores, idfScores):
    tfidf = {}

    for token, tfScore in tfScores.items():
        tfidf[token] = tfScore * idfScores[token]

    return tfidf

# Main
data = []
tfScores = []
tfidfScores = []

fileDict = []
tokenSet = set()

for x in range(10):
    string = open('Data_%d.txt' % (x + 1), 'r').read() #Get data from one file
    tokens = nltk.word_tokenize(string) # Create tokens, this gives an array
    data.append(tokens)
    tokenSet = tokenSet.union(tokens)

for tokens in data:

    tokenCount = dict.fromkeys(tokenSet, 0)

    for token in tokens: # Loop through all tokens
        tokenCount[token] += 1 # Inc count

    tfScores.append(computeTF(tokenCount, tokens))
    fileDict.append(tokenCount)

idfScore = computeIDF(fileDict)

for tf in tfScores:
    tfidfScores.append(computeTFIDF(tf, idfScore))

print(pd.DataFrame(tfidfScores))
