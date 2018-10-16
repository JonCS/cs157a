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

#CONSTANTS
DOC_NUM = 55 
FILENAMES = 'doc'
TFIDF_POS = 2

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
        token VARCHAR(255),
        doc_id int,
        TFIDF float,
        TF float,
        IDF float);""")


#Computes TF score, returns a word dictionary for unique tokens in the document with TF Scores
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

#Computes an IDF score for a particular token in a specific document
def computeIDF(token, files):
    idfScore = 0
    fileNum = len(files)

    for doc in files:
        if token in doc:
            idfScore += 1

    idfScore = math.log10(fileNum / float(idfScore))

    return idfScore

#Computes final TFIDF score
def computeTFIDF(tfScore, idfScore):

    tfidf = tfScore * idfScore

    return tfidf

#Inserts data into database, as well as python prettyTable
def insertIntoDB(token, doc_id, tfidf, tf, idf):
    #Add to the database
    sql = "INSERT INTO tfidf_table (token, doc_id, TFIDF, TF, IDF) VALUES (%s, %s, %s, %s, %s)"
    values = (token, doc_id, tfidf, tf, idf)
    mycursor.execute(sql, values)
    mydb.commit()
    

#Prints the sorted SQL table
def printTable(docId):
    sql = """SELECT token, TFIDF, TF, IDF FROM tfidf_table
           WHERE doc_id = %s 
           ORDER BY TFIDF DESC, token ASC;"""
    values = (docId,)
    mycursor.execute(sql, values)
    myTable = from_db_cursor(mycursor)
    print("Printing table for document number", docId)
    print(myTable)

def calculateGap():
    maxGap = 0
    sql = """SELECT * FROM tfidf_table;"""
    mycursor.execute(sql)
    result = mycursor.fetchall()

    bigToken = result[0]
    smallToken = result[0]

    for x in range(len(result)):
        for y in range(len(result)):
            if abs(maxGap < result[x][TFIDF_POS] - result[y][TFIDF_POS]):
                maxGap = abs(result[x][TFIDF_POS] - result[y][TFIDF_POS]) 
                if(result[x][TFIDF_POS] >= result[y][TFIDF_POS]):
                    bigToken = result[x]
                    smallToken = result[y]
                else:
                    bigToken = result[y]
                    smallToken = result[x]

    print("The max gap was", maxGap)
    print("The big token is", bigToken)
    print("The small token is", smallToken)


# Main
tfScores = []
fileTokens = []

print('Running program, please wait...')

#Collect all the tokens
for x in range(DOC_NUM):
    string = open('%s%d.txt' % (FILENAMES, (x + 1)), 'r').read() #Get data from one file
    tokens = nltk.word_tokenize(string) #Create tokens, this gives an array
    fileTokens.append(tokens)
    tfScores.append(computeTF(tokens)) #TF Score will act as a word dictionary as well

#Calculate TFIFD score and insert into DB for every token
for x in range(DOC_NUM):
    for token in tfScores[x]:
        tfScore = tfScores[x][token]
        idfScore = computeIDF(token, fileTokens)
        tfidfScore = computeTFIDF((tfScores[x])[token], idfScore)
        insertIntoDB(token, x + 1, tfidfScore, tfScore, idfScore)

#Print a table for each document
for x in range(DOC_NUM):
    printTable(x + 1)

calculateGap()
