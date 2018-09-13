import nltk
import math

nltk.download('punkt') #Needs to download thing to use tokenizer function

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

def computeTFIDF(tfTokens, idTokens):
    tfidf = {}

    for token, tfScore in tfTokens:
        tfidf[token] = tfScore * idTokens[token]

    return tfidf

#Main
tfScores = []
idfScores = []
tfidfScores = []

for x in range(10): #Open 10 files
    string = open('Data_%d.txt' % (x + 1), 'r').read() #Get data from one file
    tfTokens = nltk.word_tokenize(string) #Create tokens, this gives an array
    idfTokens = nltk.word_tokenize(string)

    tfScores.append(computeTF(tfTokens))
    idfScores.append(computeIDF(idfTokens))

tfidfScores.append(computeTFIDF(tfScores, idfScores))
print(tfidfScores)
