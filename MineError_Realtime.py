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
import traceback
import urllib2,urllib
import simplejson
import string
import time

# This version is for hierachical dictionary looking up alforithm

# threshold is the max edit distance that we tolerate
global Configuration_DB # this is the DB information of configuration 
global Caption_DB # this is the DB information of video caption
global DB_path
DB_path='/home/ruichi/Documents/OCR/Dictionary/DB_Config.txt'

global Threshold_Edit_Distance
Threshold_Edit_Distance=5
global Threshold_radio
Threshold_radio=0.33
global path_English_dict
path_English_dict='/home/ruichi/Documents/OCR/Dictionary/wordsEn.txt'
global path_special_dict
path_special_dict='/home/ruichi/Documents/OCR/Dictionary/special.txt'
global path_transcrip_dict
path_transcrip_dict='/home/ruichi/Documents/OCR/Transcripts'
global path_daily_dict
path_daily_dict='/home/ruichi/Documents/OCR/DailyDict'
global path_event_dict
path_event_dict='/home/ruichi/Documents/OCR/EventDict'
global path_result
path_result='/home/ruichi/Documents/OCR/Dictionary/result.txt'
global path_mining
path_mining='/home/ruichi/Documents/OCR/Dictionary/Mine.txt'
global num_invalid_sentence
num_invalid_sentence=0
global num_errors
num_errors=0
global num_corrected
num_corrected=0
global num_cannot_correct
num_cannot_correct=0
global num_no_error
num_no_error=0
global num_total_sentence
num_total_sentence=0

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
	caption=dictionary['Caption'].split('_')
	global Caption_DB
	Caption_DB=caption
	
def search_google(seachstr,path):
	num=0
	totle=0
	for x in range(5):
		#print "page:%s"%(x+1)
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
				#print ls 
				if(string.find(ls,seachstr)!=-1):
					num=num+1
	print 'num: '+str(num)
	print 'total: '+str(totle)
	if float(num)/float(totle)>0.5:
		append_to_file(path,str(num)+'\n')
		return True
	else:
		return False


def Mining_Special_words(path,seachstr,original):
	flag=True
	result=False;
	while(flag):
		try:		
			if search_google(seachstr,path):
				append_to_file(path,original+'\n')
				result=True
			flag=False
			print seachstr
		except:
			print 'error'
			time.sleep(30)
	return result

# check whether is a number
def check_number(a):
    nums = string.digits
    for i in a:
        if i not in nums:
            return False
    return True
# end of function

# check whether is a form of money
def check_money(word):
	if word.startswith('$') and ( word.endswith('m') or word.endswith('k')):
		if check_number(word[1:-1]):
			return True
		else: 
			return False
	elif word.startswith('$'):
		if check_number(word[1:]):
			return True
	else:
		return False

# check whether is a form of time
def check_time(word):
	if word.endswith('pm') or word.endswith('am'):
		if check_number(word[:-2]):
			return True
		else: 
			return False
	else:
		return False


# the following function is used to generate to English dictionary
# http://sourceforge.net/projects/wordlist/?source=typ_redirect
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
# end of function

# create special dictionary
def creat_special_dict(path1):
	file = open(path1)
	dictionary={} 
	while 1:
		line = file.readline().strip()
		line=line.lower().split('/')[0]
		dictionary[line]=line
		if not line:
			break
	file.close()

	return dictionary
# end of function


# create dict from transcript
def creat_transcript_dict(path1,id): 
	path=path1+'/'+str(id)+'.txt'
	file = open(path)
	word_array=file.read().split(' ')
	dictionary={} 
	st = LancasterStemmer()
	for word in word_array:
		word2=re.sub(r'[^\w]', ' ', plural(word)).strip().lower() # remove any symbols
		p = inflect.engine()
		word3=word2.replace(' ','')
		word3=str(p.singular_noun(str(word3)))
		if word3=='True' or word3=='False':
			word3='thisisnotaplural'
		dictionary[word2]=word2	
		if not dictionary.has_key(word2):
			dictionary[word2]=word2
		if not dictionary.has_key(word3) and word3!='thisisnotaplural':
			dictionary[word3]=word3		
		if not dictionary.has_key(word):
			dictionary[word]=word
	file.close()
	return dictionary
# end of function

def creat_daily_dict(path1,day): 
	path=path1+'/'+day+'.txt'
	if os.path.isfile(path):
		file = open(path)
		word_array=file.read().split(' ')
		dictionary={} 
		st = LancasterStemmer()
		for word in word_array:
			word2=re.sub(r'[^\w]', ' ', plural(word)).strip().lower() # remove any symbols
			p = inflect.engine()
		word3=word2.replace(' ','')
		word3=str(p.singular_noun(str(word3)))
		if word3=='True' or word3=='False':
			word3='thisisnotaplural'			
		if not dictionary.has_key(word2):
			dictionary[word2]=word2
		if not dictionary.has_key(word3)and word3!='thisisnotaplural':
			dictionary[word3]=word3		
		if not dictionary.has_key(word):
			dictionary[word]=word
		file.close()
		return dictionary
	else:
		dictionary={}
	return dictionary
	
# end of function

# create dict from event
def creat_event_dict(path1,eventid): 
	path=path1+'/'+str(eventid)+'.txt'
	if os.path.isfile(path):
		file = open(path)
		word_array=file.read().split(' ')
		dictionary={} 
		st = LancasterStemmer()
		for word in word_array:
			word2=re.sub(r'[^\w]', ' ', plural(word)).strip().lower() # remove any symbols
			p = inflect.engine()
			word3=word2.replace(' ','')
			word3=str(p.singular_noun(str(word3)))
			if word3=='True' or word3=='False':
				word3='thisisnotaplural'
			if not dictionary.has_key(word2):
				dictionary[word2]=word2
			if not dictionary.has_key(word3)and word3!='thisisnotaplural':
				dictionary[word3]=word3		
			if not dictionary.has_key(word):
				dictionary[word]=word
		file.close()
	else:
		dictionary={}
	return dictionary
# end of function


# used to write to file
def write_to_file(path,content):
	file = open(path,"w")
	file.write(content)
	file.close()
# end of function

# used to write to file
def append_to_file(path,content):
	file = open(path,"a")
	file.write(content)
	file.close()
# end of function

# check whether this is a wrong word
# if correct, return True
def Check_word(English_dict,transcript_dict,special_dict,word):
	p = inflect.engine()
	st = LancasterStemmer()
	word=word.lower().strip()
	word4=re.sub(r'[^\w]', ' ', plural(word)).strip().replace(' ','') # remove any symbols
	p = inflect.engine()
	#print word
	word3=str(p.singular_noun(str(word)))
	if word3=='True' or word3=='False':
		word3='thisisnotaplural'
	word2=plural(word).strip()
	word1=word
	#print word
	#print English_dict.has_key(word)
	#print word3
	#print word1
	#print 'word2'+word2
	#print dictionary2.has_key(word1)
	#print dictionary2.has_key(word1)
	#print dictionary2.has_key(word1)
	#print ((check_number(word2) or dictionary.has_key(word3) or dictionary.has_key(word) or dictionary.has_key(word2) or dictionary.has_key(plural(word1)) or dictionary2.has_key(word) or dictionary2.has_key(word2) or dictionary.has_key(word3) or dictionary2.has_key(plural(word1))or dictionary3.has_key(word) or dictionary3.has_key(word2) or dictionary.has_key(word3) or dictionary3.has_key(plural(word1))))
	result=check_time(word)or check_time(word2) or check_time(word4) or check_money(word)or check_money (word2) or check_number(word4) or check_number(word2) or English_dict.has_key(word3) or English_dict.has_key(word) or English_dict.has_key(word2) or English_dict.has_key(plural(word1)) or transcript_dict.has_key(word) or transcript_dict.has_key(word2) or transcript_dict.has_key(word3) or transcript_dict.has_key(plural(word1)) or special_dict.has_key(word3) or special_dict.has_key(word) or special_dict.has_key(word2) or special_dict.has_key(plural(word1))

	#print result
	return result
# end of function

# used to check whether the sentence contains wrong word. If contains, return true
def Check_Sentence(English_dict,transcript_dict, special_dict,sentence):
	index=1
	errorIndex=[]
	errornum=0
	sentence_len=len(sentence)
	st = LancasterStemmer()
	for word in sentence:
		separated_word=word.split('-') # this is used to check the combined words
		if len(separated_word)<2: # this is not a combined word			
			if not Check_word(English_dict,transcript_dict,special_dict,word):
				errorIndex.append(index)
				errornum=errornum+1
			index=index+1
		else: # if this is a separated word
			if not (Check_word(English_dict,transcript_dict,special_dict,separated_word[0]) and Check_word(English_dict,transcript_dict,special_dict,separated_word[1])):
				errorIndex.append(index)
				errornum=errornum+1
			index=index+1
	radio=float(errornum)/float(sentence_len)
	print str(radio)+'\n'
	if radio<Threshold_radio: # if too many errors, cannot modify
		return errorIndex
	else:
		return "thissentencemakesnosense"

	# the erorrIndex contains the exact indexs of error word
# end of function

# this is used to recover errors with special symbol
def special_symbol(word):
	if word.endswith('\"') and word.startswith('\"'):
		return 1
	elif word.endswith('\"'):
		return 2
	elif word.startswith('\"'):
		return 3
	elif word.endswith('\'s'):
		return 4
	elif word.endswith(':'):
	    return 5
	else:
		return 0
# end of function

# given the word and index, recover
def recover_special_symbot(word,index):
	if index ==1:
		word='\"'+word+'\"'
	elif index==2:
		word=word+'\"'
	elif index==3:
		word='\"'+word
	elif index==4:
		word=word+'\'s'
	elif index==5:
		word=word+':'
	else:
		word=word
	return word
# end of function



# s
def plural(word):
    if word.endswith('ies'):
        return word[:-3]+'y'
    elif word.endswith('es'):
    	return word[:-2]
    elif word.endswith('\"') and word.startswith('\"'):
    	return word[1:-1]
    elif word.endswith('ed'):
    	return word[:-2]
    elif word.endswith('\'s'):
    	return word[:-2]
    elif word.endswith('\"'):
    	return word[:-1]
    elif word.startswith('\"'):
    	return word[1:]
    elif word.endswith('s'):
        return word[:-1]
    elif word.endswith(':'):
        return word[:-1]
    elif word.endswith('%'):
        return word[:-1]
    elif word.endswith(';'):
    	return word[:-1]
    elif word.endswith('.'):
    	return word[:-1]
    elif word.endswith(','):
    	return word[:-1]
    elif word.endswith('?'):
    	return word[:-1]
    elif word.endswith('!'):
    	return word[:-1]
    else:
        return word
# end of function

# this is used to for hierachical correction
def Hierachical_Correction(error,before_error,after_error,transcript_dict,daily_dict,event_dict,special_dict,number,alpha, beta):
	# merge the transcript_dict and special_dict
	if error=='fught' or error=='fjiahl':
		return 'flight'
	elif error=='mh3?o\'s':
		return 'mh370'
	elif error=='3?o' or error=='3?o?':
		return '370'
	elif error=='t0':
		return 'to'	
	elif error=='n0':
		return 'no'		
	else: 	
		dictMerged2=dict(transcript_dict, **special_dict)
		transcript_dict=dictMerged2
		correction=correct_error(error,before_error,after_error,transcript_dict,number,alpha, beta)
		if correction==error and len(event_dict)<0 and len(daily_dict)>0:
			correction=correct_error(error,before_error,after_error,daily_dict,number,alpha, beta)
		if correction==error and len(event_dict)>0:
			correction=correct_error(error,before_error,after_error,event_dict,number,alpha, beta)
			if correction==error and len(daily_dict)>0: # if event_dict is not enough to correct
				correction=correct_error(error,before_error,after_error,daily_dict,number,alpha, beta)		
		return correction


# given a local dictionary, correct based on both SM and LM
def correct_error(error,before_error,after_error,dictionary,number,alpha, beta):
	edit_dist={}
	for (k,v) in  dictionary.items(): 
		edit_dist[k]=edit_distance(error,str(k))		
	d=edit_dist
	LM_score=[] # contains the LM score
	SM_score=[] # contains the edit distance
	correct_list=[] # contains the potential word
	Total_score=[] # TS=alpha*SM+beta*LM
	estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
	lm = NgramModel(2, brown.words(categories='news'), estimator=estimator)
	SM1=sorted(d.items(), key=lambda d:d[1])[0][1]
	#print 'SM1'
	#print SM1
	SM2=sorted(d.items(), key=lambda d:d[1])[1][1]
	#print 'SM2'
	#print SM2
	if SM1<Threshold_Edit_Distance: # if this are too many char needs to be correct, break
		if SM1==SM2: # if SM cannot determine which word to correct
			for num in range(0,number):  
				correct_potential=sorted(d.items(), key=lambda d:d[1])[num][0]
				#print correct_potential 
				correct_list.append(correct_potential)
				SM_score.append(float(1)/(sorted(d.items(), key=lambda d:d[1])[num][1]))
				#print correct_potential
				#print (sorted(d.items(), key=lambda d:d[1])[num][1])
				if (1/lm.prob(correct_potential, [after_error]))>(1/lm.prob(before_error, [correct_potential])):
					LM_score.append(1/lm.prob(correct_potential, [after_error]))
				else:
					LM_score.append(1/lm.prob(before_error, [correct_potential]))
			LM_score=normalize(LM_score)
			SM_score=normalize(SM_score)
			for i in range(0,len(LM_score)-1):
				Total_score.append(alpha*SM_score[i]+beta*LM_score[i])
			correctIndex=Total_score.index(max(Total_score))
			#print correctIndex
			return correct_list[correctIndex]
		else:
			return sorted(d.items(), key=lambda d:d[1])[0][0]
	else:
		return error
	
# end of function

# normalization
def normalize(array):
	vmax=max(array)
	vmin=min(array)
	if vmax>vmin:
		for num in range(0,len(array)-1):
			array[num]=(array[num]-vmin)/(vmax-vmin)
	return array

# end of function

# if this method returns true, which means the system believe that this word needs to be searched by google to make sure
def Should_Search(dictionary,error,path):
	edit_dist={}
	for (k,v) in  dictionary.items(): 
		edit_dist[k]=edit_distance(error,str(k))		
	d=edit_dist
	SM1=sorted(d.items(), key=lambda d:d[1])[0][1]
	ratio=float(SM1)/float(len(error))
	if ratio>0.3:
		#append_to_file(path,str(ratio)+'\n')
		return True
	else:
		return False

# Main function

# this is the dictionary of error. Key is the error and value is the show up time of this error
errordict={}

# this is used to set up the DB sentence
DB_Info(DB_path)


conn_lock = MySQLdb.connect(host=Configuration_DB[0], user=Configuration_DB[1],passwd=Configuration_DB[2], db=Configuration_DB[3])
cursor_lock = conn_lock.cursor()
#count = cursor.execute(sqlcommand)
count_lock = cursor_lock.execute('select * from Configuration where id=1')
cursor_lock.scroll(0,mode='absolute')
results_lock = cursor_lock.fetchall()  
lock_index=''
conn = MySQLdb.connect(host=Caption_DB[0], user=Caption_DB[1],passwd=Caption_DB[2], db=Caption_DB[3])

for r in results_lock:
	lock_index=str(r[8])
	print r[8]

if lock_index=='0':
	cursor_update = conn_lock.cursor()
	sql='update Configuration set Lock_MineError=1 where id=1'		
	cursor_update.execute(sql)
	conn_lock.commit()
	
	cursor = conn.cursor()
	#count = cursor.execute(sqlcommand)
	count = cursor.execute('select * from VideoCaption')
	cursor.scroll(0,mode='absolute')
	results = cursor.fetchall()  
	English_dict=creat_English_dict(path_English_dict) #http://www-01.sil.org/linguistics/wordlists/english/
	special_dict=creat_special_dict(path_special_dict); # special_dict
	for r in results: 
		try:
			if str(r[3])=='ProgramTitle':
				id=r[0]
				program=r[1].split('_')
				print id
				sentence=r[4]
				sentence=sentence.replace('\n',' ')
				sentence=sentence.lower()
				sentence1=sentence.split(' ')
				correct_sentence=sentence.split(' ')
				transcript_dict=creat_transcript_dict(path_transcrip_dict,id) # transcript_dict
				errorlist=Check_Sentence(English_dict,transcript_dict,special_dict, sentence1)
				#  Case 1: sentence make no sense
				if errorlist=="thissentencemakesnosense":  
					errorlist="thissentencemakesnosense"
				#  Case 2: No error
				elif len(errorlist)==0:
					errorlist=errorlist
				#  Case 3: Have errors
				else:
					for errorid in errorlist:  # errorid start from 1 to len(sentence1)-1
						error=correct_sentence[errorid-1]
						if Should_Search(transcript_dict,error,path_mining):
							if not errordict.has_key(error):
								errordict[error]=1
							else:
								errordict[error]=errordict[error]+1
								# if an error shows up twice, then add to Mine.txt
								if errordict[error]==2:
									append_to_file(path_mining,error+'\n')
									print error
								#time.sleep(2)
							

		except Exception, e:
			print e
			print traceback.format_exc()

	sql='update Configuration set Lock_MineError=0 where id=1'		
	cursor_update.execute(sql)
	conn_lock.commit()

conn_lock.close()

conn.close() 
