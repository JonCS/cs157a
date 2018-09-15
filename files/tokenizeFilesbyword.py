import re, os, sys, csv, math
from collections import Counter
from collections import defaultdict

def files_2wordscsv(dirPath):
	files = dirPath.split(',')
	tokenID=0
	fileID=0
	for name in files:
	  fileID +=1
	  with open (name) as f:
			 for line in f:
					for word in re.findall(r'\w+',line):
						tokenID +=1
#						print(word +" ,"+`fileID`)
						print(`tokenID` +"," + word +","+`fileID`)

def count_tf(fileName):
	words= []
	with open(fileName, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for row in reader:
			words.append(row[1].strip()) #We take out word only and put into a words list so that same word will be counted in the file only.
	#now we are counting TF, term frequency in a document.
	words_counted = []
	maxCount=0
	#totalCount=0
	for item in words:
		x = words.count(item)
		if (x > maxCount):
			maxCount = x # we are find max counted word.
		#totalCount=totalCount+x
		words_counted.append(`item`+","+`x`)
	words_set= list(set(words_counted)) # to remove duplicates
	for item in words_set:
		items = item.split(",") #split word and word count item by item
		#word = items[0].rsplit('-',1)[0]
		count1=0.5+float((float(items[1]))/maxCount)*0.5#calculate TF
		print `item`+","+`count1`
	print "maxCount: "+`maxCount`
	#print `totalCount`

def count_idf(csvFileLists): #we read in all csv files take out the words and put them into one list for word counting. then print out word, DF
	# now we are going to count DF, i.e. a term appeared in how many documents.
	print "We are now calculate document frequencies >>>>>>>>>>>>>>\n\n\n"
	
	files = csvFileLists.split(',') #srting item splited will become list[' file1',' file2']
	totalDocs=len(files)
	words=[]
	fileID=0
	for name in files:
	  fileID +=1
	  name1=name.replace(' ','')
	  with open (name1) as f:
#			reader=csv.reader(f)
#			reader.next()
			for row in f:
				word=(row.replace('"','')).replace('\'','').split(',')[0]
				words.append(word.strip())
	words_counted=[]
	for item in words:
		x = words.count(item)
		idf=math.log(totalDocs) - math.log(1+x)
		words_counted.append(`item`+","+`x`+","+`idf`)
	words_set= list(set(words_counted)) # to remove duplicates
	for item in words_set:
		print item
		
def cal_tfidf(csvFileLists):
	
		
if (len(sys.argv) < 2):
 print ("You need to enter command like: Python tokenizeFilesbyword.py <csv filename> <-count_idf | -count_tf |-files_2wordscsv>")
 sys.exit(os.EX_OK)

csvFile = sys.argv[1]
methodOpt=sys.argv[2]
if (methodOpt=="-count_idf"):
	count_idf(csvFile)
if (methodOpt=="-count_tf"):
	count_tf(csvFile)
if (methodOpt=="-files_2wordscsv"):
	files_2wordscsv(csvFile)
