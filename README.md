# cs157a
Authors: Jonathan Su, Kevin Liu, Filip Koperwas, Vicson Moses

# Dependencies:<br>
nltk `pip3 install nltk`<br>
pandas `pip3 install pandas`<br>
mysql.connector `pip3 install mysql-connector`<br>
prettytable `pip3 install prettytable`<br>

Edit files/project1.py and change the database username and password to connect to your local database

May have to do this if you run into a download error `error at nltk.download() `

Change directory to the python folder: `cd /Applications/Python 3.6/`

Run the command: `./Install Certificates.command`

# Notes:

*Some information may be outdated*

- use the 10 documents in the projects/temp_data
- find a tokenizer to turn every file into a tuple of (token_id, token, document_id)
- Use it to get the TFIDF ratios for each token.
- Make a table of tokens where the tuple is (doc_id, TFIDF ratio).

1. recognize tokens by 
1.1 'alphabet' , 
1.2 'numeral'  and 
1.3 rest of them will be one byte one token
2. Please look at the data in TT20
