import nltk
nltk.download('punkt') #Needs to download thing to use tokenizer function

def computeTF(tokens):
    tfDict = {} 
    for token in tokens: # Loop through all tokens
        if not tfDict.has_key(token): #If key doesn't exist, make new key and set to 1
            tfDict[token] = 1
        else: #If key already exists, increment key
            tfDict[token] = tfDict[token] + 1
    for key in tfDict: #Once all tokens are counted, compute TF score for each token in the document
        tfDict[key] = tfDict[key] / float(len(tokens))
    return tfDict
#Main
tfScores = []
for x in range(10): #Open 10 files
    string = open('Data_%d.txt' % (x + 1), 'r').read() #Get data from one file
    tokens = nltk.word_tokenize(string) #Create tokens, this gives an array
    tfScores.append(computeTF(tokens))
    print(tfScores)
