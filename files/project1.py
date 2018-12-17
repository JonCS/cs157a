#HOW TO RUN THIS PROGRAM
'''
1. Edit the sql database strings for user and passwd with the same values that are used for your sql instance on your localhost

2. Run pip3 install nltk pandas mysql-connector prettytable

3. Run python3 project1.py [FILES]

[FILES] is all the files you would like the program run through
'''

#IMPORTS
import sys
import string
import re

#CONSTANTS
DOC_START = 1 
DOC_END = 1 
FILENAMES = 'newDocs'   
FILENAME = '1.txt'
TFIDF_POS = 3

encoding = 'unicode_escape'

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
    from mysql.connector import errorcode
except:
    print("Please make sure you have all the following libraries installed:")
    print("nltk, mysql-connector, prettytable")
    print("Use pip3 to install them")
    exit()

nltk.download('punkt') # Needs to download thing to use tokenizer function

#Connect to mysql database
#Update user and uncomment password if you need to

print("\nMake sure you have mysql installed on localhost.")
username = input("Enter your sql username: ")
password = input("Enter your sql password: ")
config = {
    'host':'localhost',
    'user':username,
    'passwd':password,
}
try:
    mydb = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    print("Could not connect to your sql database")
    print("Please make sure you have it installed and you entered the right credentials")
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

def splitDocument(document):
    documentArray = document.split('. ')
    return documentArray

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
                break

    idfScore = math.log10(fileNum / float(idfScore))
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
    sql = """SELECT doc_id, token_id, token, TFIDF, TF, IDF FROM tfidf_table
           WHERE doc_id = %s AND TFIDF IS NOT NULL 
           ORDER BY TFIDF DESC, token ASC;"""
    values = (docId,)
    mycursor.execute(sql, values)
    myTable = from_db_cursor(mycursor)
    print("Printing table for document number", docId)
    print(myTable)

def print2ConceptTable():
    sql = """SELECT * FROM 2Concept_table"""
    mycursor.execute(sql)
    myTable= from_db_cursor(mycursor)
    print("\nThis is the 2 Concept Table\n")
    print(myTable)

#Calculates the gap to find keywords
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
    print("TFIDF value for bigger one, which is %s, is:" % (bigToken[2]), bigToken[TFIDF_POS])
    print("TFIDF value for smaller one, which is %s, is:" % (smallToken[2]), smallToken[TFIDF_POS])
    keywords = []
    keywordStop = min(keywordStopIndex, 45) #Limit to 45 keywords so that we can always make a 2Concept table
    for x in range(keywordStop):
        flag = True
        for keyword in keywords:
            if(result[x][2] == keyword):
                flag = False
                break;
        if flag:
            #print("This is a keyword:", result[x][2])
            keywords.append(result[x][2])
    return keywords

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
        return token, punctuation
    else:
        return newToken, punctuation

#Tokenize the document
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

def make2ConceptTable(keywords, doc_Num):

    mycursor.execute("DROP TABLE IF EXISTS 2Concept_table")
    concepts = []
    for y in range(len(keywords)):
        for z in range(y, len(keywords)):
            if(y != z and len(concepts) < 1000):
                newConcept = keywords[y] + '_' + keywords[z]
                concepts.append(newConcept)

    columns = []
    for i in range(len(concepts)):
        columns.append(concepts[i] + ' int DEFAULT 0')

    if len(columns) == 0:
        print("Could not make 2Concept Table because there was only one keyword")
        return

    sql = 'CREATE TABLE 2Concept_table (doc_id int,' + ', '.join(columns) + ',PRIMARY KEY (doc_id));'
    mycursor.execute(sql)

    for doc in range(doc_Num):
        sql = """INSERT INTO 2Concept_table (doc_id) VALUES (%s);"""
        mycursor.execute(sql, (doc + 1,))


    for i in range(len(concepts)):
        sql = """SELECT DISTINCT doc_id FROM tfidf_table
                 WHERE token = %s OR token = %s;"""
        splitWord = concepts[i].split('_')
        values = (splitWord[0], splitWord[1])
        mycursor.execute(sql, values)
        ids = mycursor.fetchall()
        for anId in ids:
            sql = """SELECT COUNT(token) from tfidf_table where doc_id=%s
                     AND token IN (%s, %s)"""                  
            values = (anId[0], splitWord[0], splitWord[1])
            mycursor.execute(sql, values)
            count = mycursor.fetchall()
            if(count[0][0] > 1):
                sql = "UPDATE 2Concept_table SET %s=1 where doc_id=%s" % (concepts[i], anId[0])
                mycursor.execute(sql)

    mydb.commit()
    return concepts

#Prints out Where the 2Concepts are located
def print2ConceptLocations(concepts, doc_Num, files):
    sql = """SELECT * FROM 2Concept_table"""
    mycursor.execute(sql)
    rows = mycursor.fetchall()
    for i in range(len(rows)):
        for j in range(1, len(rows[i])):
            if (rows[i][j] == 1):
                print("Found Concept " + concepts[j - 1] + " in doc_id " + str(rows[i][0]))

#Makes a binary table for the keywords
def makeBinaryTable(keywords, doc_Num):
    columns = []
    for keyword in keywords:
        columns.append('_' + keyword  + ' int DEFAULT 0')
    mycursor.execute("DROP TABLE IF EXISTS binary_table")
    sql = 'CREATE TABLE binary_table (doc_id int,' + ', '.join(columns) + ',PRIMARY KEY (doc_id));'
    mycursor.execute(sql)

    for doc in range(doc_Num):
        sql = """INSERT INTO binary_table (doc_id) VALUES (%s);"""
        mycursor.execute(sql, (doc + 1,))

    for keyword in keywords:
        sql = "SELECT DISTINCT doc_id from tfidf_table where token = %s"
        values = (keyword,)
        mycursor.execute(sql, values)
        ids = mycursor.fetchall()
        for id in ids:
            sql = "UPDATE binary_table SET _%s=1 where doc_id=%s" % (keyword, id[0])
            mycursor.execute(sql)

    mydb.commit()


# Main
print('\n')
splitSentences = input("Split the Documents by sentences? Enter yes or no: ")
if(splitSentences == 'yes'):
    splitSentences = True
elif(splitSentences == 'no'):
    splitSentences = False
else:
    print("You did not enter a valid input, please enter yes or no exactly next time.")
    exit()
files = []
for i in range(1, len(sys.argv)):
    files.append(sys.argv[i])

print('\n')
print("The files are: " + str(files))
print('\n')

tfScores = [] #keeps track of tfScores
fileTokens = [] #keeps track of filetokens

documentArray = [] #Keeps track of the documents

print('Running program, please wait...')

for fileName in files:

    try:
        documentString = open(fileName, encoding='utf-8').read() #Get data from one file
    except:
        documentString = open(fileName, encoding='windows-1252').read()
    if(splitSentences):
        documentArray.extend(splitDocument(documentString))
    else:
        documentArray.append(documentString)
            


#print("Length of document array is %d" % (len(documentArray)))
#Collect all the tokens
for y in range(len(documentArray)):
    tokens = tokenizeString(documentArray[y])
    fileTokens.append(tokens)
    tfScores.append(computeTF(tokens)) #TF Score will act as a word dictionary as well

#Calculate TFIFD score and insert into DB for every token
for z in range(len(documentArray)):
    token_id = 0
    for token in tfScores[z]:
        token_id += 1
        tfScore = tfScores[z][token]
        idfScore = computeIDF(token, fileTokens)
        tfidfScore = computeTFIDF((tfScores[z])[token], idfScore)
        insertIntoDB(token, z + 1, token_id, tfidfScore, tfScore, idfScore)

mydb.commit()
#Print a table for each document

keywords = calculateGap()
print("\nThe keywords are:")
print(keywords)

makeBinaryTable(keywords, len(documentArray))

two_concepts = make2ConceptTable(keywords, len(documentArray))
print("\nThe 2 concepts are: ")
print(two_concepts)

print2ConceptLocations(two_concepts, len(documentArray), files)

print2ConceptTable()
