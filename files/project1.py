import sys
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
        tfidf float);""")


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
def insertIntoDB(token, doc_id, tfidf):
    #Add to the database
    sql = "INSERT INTO tfidf_table (token, doc_id, tfidf) VALUES (%s, %s, %s)"
    values = (token, doc_id, tfidf)
    mycursor.execute(sql, values)
    mydb.commit()
    

#Prints the sorted SQL table
def printTable():
    sql = """SELECT * FROM tfidf_table
           ORDER BY doc_id ASC, tfidf DESC, token ASC;"""
    mycursor.execute(sql)
    myTable = from_db_cursor(mycursor)
    print(myTable)

# Main
tfScores = []
fileTokens = []

print('Running program, please wait...')

#Collect all the tokens
for x in range(10):
    string = open('Data_%d.txt' % (x + 1), 'r').read() #Get data from one file
    tokens = nltk.word_tokenize(string) #Create tokens, this gives an array
    fileTokens.append(tokens)
    tfScores.append(computeTF(tokens)) #TF Score will act as a word dictionary as well

#Calculate TFIFD score and insert into DB for every token
for x in range(10):
    for token in tfScores[x]:
        idfScore = computeIDF(token, fileTokens)
        tfidfScore = computeTFIDF((tfScores[x])[token], idfScore)
        insertIntoDB(token, x + 1, tfidfScore)

#Print the Table
printTable()
