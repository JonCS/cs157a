# cs157a
Authors: Jonathan Su, Kevin Liu, Filip Koperwas, Vicson Moses

# Dependencies:<br>
nltk `pip3 install nltk`<br>
pandas `pip3 install pandas`<br>
mysql.connector `pip3 install mysql-connector`<br>
prettytable `pip3 install prettytable`<br>

# Running Program: 
In the files directory, run: python3 project1.py<br>
Make sure you are using python3

If you run into an error that says you can't connect to your sql database, edit files/project1.py and change the database username and password to connect to your local database

If you run this download error `error at nltk.download() `, do the following:<br>
Change directory to the python folder: `cd /Applications/Python 3.6/`<br>
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
