# Import the corpus and functions used from nltk library
import MySQLdb
from nltk.stem.lancaster import LancasterStemmer
import re
import string
import nltk
from nltk.corpus import brown
from nltk.probability import LidstoneProbDist
from nltk.model import NgramModel
from nltk.metrics import edit_distance
import os
from nltk.stem.snowball import SnowballStemmer
import inflect
import urllib2,urllib
import traceback
import simplejson
import string
import time
st = LancasterStemmer()
#print st.stem(word)

# logic:
# 1. read dictionary from Mine, which is the new result mining from whole dataset
# 2. remove the errors showed up in MinedError
# 3. run google search on candidates
# 4. store words passed the google search

global Configuration_DB # this is the DB information of configuration 
global DB_path
DB_path='/home/ruichi/Documents/OCR/Dictionary/DB_Config.txt'

global path_English_dict
path_English_dict='/home/ruichi/Documents/OCR/Dictionary/English.txt'
#path_English_dict='/Users/Rich/Desktop/OCR/English.txt'
global path_Mine
path_Mine='/home/ruichi/Documents/OCR/Dictionary/Mine.txt'
#path_Mine='/Users/Rich/Desktop/OCR/Mine.txt'
global path_MinedError
path_MinedError='/home/ruichi/Documents/OCR/Dictionary/MinedError.txt'
#path_MinedError='/Users/Rich/Desktop/OCR/MinedError.txt'
global path_after_search
path_after_search='/home/ruichi/Documents/OCR/Dictionary/AfterMine.txt'
#path_after_search='/Users/Rich/Desktop/OCR/AfterMine.txt'

# this function is used to remove the dupilication in AfterMine.txt
def CleanUp(path):
    file = open(path)
    dictionary={} 
    while 1:
        line = file.readline().strip()
        if not line:
            break
        if not dictionary.has_key(line):
            dictionary[line]=line

    write_to_file(path,'')
    for key in dictionary:
        append_to_file(path,dictionary[key]+'\n')
    file.close()


def DB_Info(path):
    file = open(path)
    dictionary={} 
    while 1:
        line = file.readline().strip()
        if not line:
            break
        tmp=line.split('/')
        if not dictionary.has_key(line):
            dictionary[tmp[0]]=tmp[1]
    file.close()
    config=dictionary['Config'].split('_')
    global Configuration_DB
    Configuration_DB=config



# used to write to file
def append_to_file(path,content):
    file = open(path,"a")
    file.write(content)
    file.close()
# end of function
# used to write to file
def write_to_file(path,content):
	file = open(path,"w")
	file.write(content)
	file.close()

#print i 

def creat_English_dict(path1):
    file = open(path1)
    dictionary={} 
    while 1:
        line = file.readline().strip()
        line=line.lower().split('/')[0].strip()
        if not dictionary.has_key(line):
            dictionary[line]=line
        if not line:
            break
    file.close()
    return dictionary

def creat_MinedError(path1):
    file = open(path1)
    dictionary={} 
    while 1:
        line = file.readline().strip()
        if not line:
            break
        line=line.lower().strip()
        if not dictionary.has_key(line):
            dictionary[line]=line
            print line
    file.close()
    return dictionary

def plural(word):
    if word.endswith('ies'):
    	print 1
        return word[:-3]+'y'
    elif word.endswith('es'):
    	print 2
    	return word[:-2]
    elif word.endswith('\"') and word.startswith('\"'):
    	print 3
    	return word[1:-1]
    elif word.endswith('ed'):
    	print 4
    	return word[:-2]
    elif word.endswith('\'s'):
    	print 6
    	return word[:-2]
    elif word.endswith('\"'):
    	print 7
    	return word[:-1]
    elif word.startswith('\"'):
    	print 8
    	return word[1:]
    elif word.endswith('s'):
    	print 11
        return word[:-1]
    elif word.endswith(':'):
    	print 12
        return word[:-1]
    elif word.endswith('%'):
    	print 13
        return word[:-1]
    elif word.endswith(';'):
    	print 14
    	return word[:-1]
    elif word.endswith('.'):
    	print 15
    	return word[:-1]
    elif word.endswith(','):
    	print 144
    	return word[:-1]
    elif word.endswith('?'):
    	print 111
    	return word[:-1]
    elif word.endswith('!'):
    	print 1111
    	return word[:-1]
    else:
        return word
# end of function

# If most of google search contains the word, return true, otherwise return false
def search_google(seachstr):
	num=0
	totle=0
	for x in range(5):
		page = x * 4
		url =('https://ajax.googleapis.com/ajax/services/search/web'
					'?v=1.0&q=%s&rsz=8&start=%s') %(urllib.quote(seachstr),page)
		try:
			request = urllib2.Request(
			url, None, {'Referer': 'http://www.sina.com'})
			response = urllib2.urlopen(request)

		# Process the JSON string.
			results = simplejson.load(response)
			infoaaa = results['responseData']['results']
		except Exception,e:
			print e
		else:
			for minfo in infoaaa:
				ls=minfo['titleNoFormatting'].encode('utf8').lower()
				totle=totle+1
				print ls 
				if(string.find(ls,seachstr)!=-1):
					num=num+1
	print num
	print totle
	if float(num)/float(totle)>0.875:
		return True
	else:
		return False

# this function is to mine special word from google search. If this is a special word, return true.
def Mining_Special_words(path,seachstr,original):
    flag=True
    result=False;
    while(flag):
        try:        
            if search_google(seachstr):
                append_to_file(path,original+'\n')
                result=True
            flag=False
            print 'this is the word'
        except Exception, e:
            print e
            print traceback.format_exc()
            time.sleep(30)
    return result


# This function is used to determine whether an error should be searched on google
def Should_Search(dictionary,error):
    edit_dist={}
    for (k,v) in  dictionary.items(): 
        edit_dist[k]=edit_distance(error,str(k))        
    d=edit_dist
    SM1=sorted(d.items(), key=lambda d:d[1])[0][1]
    print sorted(d.items(), key=lambda d:d[1])[0][0]
    ratio=float(SM1)/float(len(error))
    if SM1>1:
        #append_to_file(path,str(ratio)+'\n')
        return True
    else:
        return False

def Mining(dictionary,MinedError,source_path,dest_path,path_Mined):
    file = open(source_path)
    while 1:
        line = file.readline().lower().strip()
        if not line:
            break
        error=line
        # if one word is in Mine.txt but not in Mined.txt, add it into Mined.txt
        print 'if this word mined? '+error
        print MinedError.has_key(error)
        if not MinedError.has_key(error):
            append_to_file(path_Mined,error+'\n')
            print 'should search? ' +error
            print Should_Search(dictionary,error)
            if Should_Search(dictionary,error):
                if Mining_Special_words(dest_path,error,error):
                    print Mining_Special_words(dest_path,error,error)
                    print '1 '+error
                else:
                    error1=error.replace('.','')
                    if Mining_Special_words(dest_path,error1,error):
                        print '2 '+error
                    else:
                        if Mining_Special_words(dest_path,plural(error),error):
                            print '3 '+error

    file.close()

# this is used to set up the DB sentence
DB_Info(DB_path)
conn_lock = MySQLdb.connect(host=Configuration_DB[0], user=Configuration_DB[1],passwd=Configuration_DB[2], db=Configuration_DB[3])
cursor_lock = conn_lock.cursor()
#count = cursor.execute(sqlcommand)
count_lock = cursor_lock.execute('select * from Configuration where id=1')
cursor_lock.scroll(0,mode='absolute')
results_lock = cursor_lock.fetchall()  
lock_index=''

for r in results_lock:
    lock_index=str(r[9])
    print r[9]

if lock_index=='0':
    cursor_update = conn_lock.cursor()
    sql='update Configuration set Lock_GoogleSearch=1 where id=1'      
    cursor_update.execute(sql)
    conn_lock.commit()

    English_dict=creat_English_dict(path_English_dict)
    MinedError=creat_MinedError(path_MinedError)
    Mining(English_dict,MinedError,path_Mine,path_after_search,path_MinedError)

    # this is used to clean up Mine.txt
    write_to_file(path_Mine,'')
    CleanUp(path_after_search)

    sql='update Configuration set Lock_GoogleSearch=0 where id=1'      
    cursor_update.execute(sql)
    conn_lock.commit()

conn_lock.close()


