#HOW TO RUN THIS PROGRAM
'''
1. Put the documents into the same directory as this program with a filename structure such as 'docName+Num.txt'
   For example, if you choose to have the base filename be doc, then document 1 will have the name 'doc1.txt'
   document 2 will have the name 'doc2.txt'.

2. Edit the constants in the CONSTANTS section to match the name of the documents + the number of documents

3. Edit the sql database strings for user and passwd with the same values that are used for your sql instance on your localhost
'''

#IMPORTS
import sys
import string
import re

#CONSTANTS
DOC_START = 1 
DOC_END = 55
FILENAMES = 'doc'   
TFIDF_POS = 3

#RUNTIME CHECKS
if sys.version_info < (3,0):
    print("Please use python 3 to run this program and try again. Thank you!")
    exit()
try:
    import nltk
    import math
    import mysql.connector
    from prettytable import PrettyTable
    from prettytable import from_db_cursor
except:
    print("Please make sure you have all the following libraries installed:")
    print("nltk, mysql-connector, prettytable")
    print("Use pip3 to install them")
    exit()

nltk.download('punkt') # Needs to download thing to use tokenizer function

#Connect to mysql database
#Update user and uncomment password if you need to
try:
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      #passwd="",
    )
except:
    print("Could not connect to your sql database")
    print("Please make sure you have it installed and you edited this file with your credentials")
    exit()

mycursor = mydb.cursor() #Define cursor

#Drop database for project if it exists and create a fresh new one
mycursor.execute("DROP DATABASE IF EXISTS project1")
mycursor.execute("CREATE DATABASE project1")
mycursor.execute("USE project1")
mycursor.execute("DROP TABLE IF EXISTS TFIFD_TABLE")
mycursor.execute("""CREATE TABLE tfidf_table(
        token_id int,
        doc_id int,
        token VARCHAR(255),
        TFIDF float,
        TF float,
        IDF float);""")

#Might use this later, not used right now.
def makeAlpha(token):
    nonCharDict = {} 
    alphaToken = ""
    for char in token:
        if not char.isalpha() and not char.isdigit():
            if not char in nonCharDict:
                nonCharDict[char] = 1
            else:
                nonCharDict[char] += 1
        else:
            alphaToken += char
    return alphaToken, nonCharDict

#Computes TF score, returns a word dictionary for unique tokens in the document with TF Scores
def computeTF(tokens):
    tfDict = {}
    for token in tokens: # Loop through all tokens
        if not token['token'].lower() in tfDict: #If key doesn't exist, make new key and set to 1
            tfDict[token['token'].lower()] = 1
        else: #If key already exists, increment key
            tfDict[token['token'].lower()] += 1
    
    #Only update TFScore with calculated TFScore if the key is alphaNumerical
    wordTokenCount = 0
    for key in tfDict:
        if key.isalpha():
            wordTokenCount += tfDict[key]

    for key in tfDict: #Once all tokens are counted, compute TF score for each token in the document
        if key.isalpha():
            tfDict[key] = tfDict[key] / float(wordTokenCount)
        else:
            tfDict[key] = None
    return tfDict


#Computes an IDF score for a particular token in a specific document
def computeIDF(token, files):
    #Return none if not alpha
    if not token.isalpha():
        return None

    idfScore = 0
    fileNum = len(files)

    for doc in files:
        for docToken in doc:
            if docToken['token'].lower() == token.lower():
                idfScore += 1

    idfScore = math.log(fileNum / float(idfScore))
    return idfScore

#Computes final TFIDF score
def computeTFIDF(tfScore, idfScore):

    #Return none if not alpha
    if tfScore is None or idfScore is None:
        return None
    tfidf = tfScore * idfScore
    return tfidf

#Inserts data into database, as well as python prettyTable
def insertIntoDB(token, doc_id, token_id, tfidf, tf, idf):
    #Add to the database
    sql = "INSERT INTO tfidf_table (doc_id, token_id, token, TFIDF, TF, IDF) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (doc_id, token_id, token, tfidf, tf, idf)
    mycursor.execute(sql, values)
    

#Prints the sorted SQL table
def printTable(docId):
    sql = """SELECT token_id, token, TFIDF, TF, IDF FROM tfidf_table
           WHERE doc_id = %s AND TFIDF IS NOT NULL 
           ORDER BY TFIDF DESC, token ASC;"""
    values = (docId,)
    mycursor.execute(sql, values)
    myTable = from_db_cursor(mycursor)
    print("Printing table for document number", docId)
    print(myTable)

def calculateGap():
    maxGap = 0
    sql = """SELECT * FROM tfidf_table
             WHERE TFIDF IS NOT NULL
             ORDER BY TFIDF DESC;"""
    mycursor.execute(sql)
    result = mycursor.fetchall()

    bigToken = result[0]
    smallToken = result[0]
    gapValues = []

    for x in range(0, len(result), 1):
        if (x+1) != len(result):
            gapValues.append((abs(result[x][TFIDF_POS] - result[x + 1][TFIDF_POS])))
            if maxGap < abs(result[x][TFIDF_POS] - result[x + 1][TFIDF_POS]):
                maxGap = abs(result[x][TFIDF_POS] - result[x + 1][TFIDF_POS]) 
                bigToken = result[x]
                smallToken = result[x + 1]
                keywordStopIndex = x + 1


    print("The biggest gap in TFIDF value is:", maxGap)
    print("TFIDF value for bigger one is:", bigToken[TFIDF_POS])
    print("TFIDF value for smaller one is:", smallToken[TFIDF_POS])
    for x in range(keywordStopIndex):
        print("This is a keyword:", result[x][2])

def removePunctuation(token):
    newToken = ""
    punctuation = []
    if(not token[0].isalpha() and not token[0].isdigit()):
        newToken = token[1:] #Delete first character
        punctuation.insert(0, token[0])
        if(not newToken[-1].isalpha() and not newToken[-1].isdigit()):
            newToken = newToken[0:-1] #last character is excluded
            punctuation.insert(1, newToken[-1])
    if newToken == "":
        #print(token)
        #print(token)
        return token, punctuation
    else:
        #print(token)
        #print(newToken)
        return newToken, punctuation

def tokenizeString(documentString):
    newWord = ""
    tokens = []
    newToken = {}
    tokenId = 1
    for char in documentString:
        if (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z'):
            newWord += char
        else:
            if len(newWord) > 0:
                newToken['token'] = newWord
                newToken['tokenId'] = tokenId
            else:
                newToken['token'] = char
                newToken['tokenId'] = tokenId
            tokenId += 1
            tokens.append(newToken)
            newToken = {}
            newWord = ""

    return tokens
# Main
tfScores = []
fileTokens = []

print('Running program, please wait...')

#Collect all the tokens
for x in range(DOC_START - 1, DOC_END):
    documentString = open('%s%d.txt' % (FILENAMES, (x + 1)), 'r').read() #Get data from one file
    tokens = tokenizeString(documentString)
    fileTokens.append(tokens)
    tfScores.append(computeTF(tokens)) #TF Score will act as a word dictionary as well

#Calculate TFIFD score and insert into DB for every token
for x in range(DOC_END - DOC_START + 1):
    token_id = 0
    for token in tfScores[x]:
        token_id += 1
        tfScore = tfScores[x][token]
        idfScore = computeIDF(token, fileTokens)
        tfidfScore = computeTFIDF((tfScores[x])[token], idfScore)
        insertIntoDB(token, DOC_START + x, token_id, tfidfScore, tfScore, idfScore)

mydb.commit()
#Print a table for each document
for x in range(DOC_START, DOC_END + 1):
    printTable(x)

calculateGap()
