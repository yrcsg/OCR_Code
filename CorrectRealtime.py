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
import datetime

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
global path_Mined
path_Mined='/home/ruichi/Documents/OCR/Dictionary/Mined.txt'
global path_error_mapping
path_error_mapping='/home/ruichi/Documents/OCR/Dictionary/error_mapping.txt'
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

# this function is to read DB information
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

# create_Mined_dict
def creat_Mined_dict(path1):
	file = open(path1)
	dictionary={} 
	while 1:
		line = file.readline().strip()
		if not line:
			break
		line=line.lower().split('/')[0].strip()
		if not dictionary.has_key(line):
			dictionary[line]=line
	file.close()
	return dictionary
# end of function



def creat_Mapping(path1):
	file = open(path1)
	dictionary={} 
	while 1:
		line = file.readline().strip()
		if not line:
			break
		error=line.lower().split('/')[0].strip()
		correct=line.lower().split('/')[1].strip()
		if not dictionary.has_key(line):
			dictionary[error]=correct
	file.close()
	return dictionary

# create special dictionary
def creat_special_dict(path1):
	file = open(path1)
	dictionary={} 
	while 1:
		line = file.readline().strip()
		if not line:
			break
		line=line.lower().split('/')[0]
		dictionary[line]=line
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
		#word2=re.sub(r'[^\w]', ' ', plural(word)).strip().lower() # remove any symbols
		word2=plural(word).strip().lower()
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

# check whether this is a wrong word
# if correct, return True
def Check_word(English_dict,transcript_dict,special_dict,word):
	p = inflect.engine()
	st = LancasterStemmer()
	if string.find(word,'MH17-?')!=-1 or string.find(word,'put|n\'s')!=-1 or string.find(word,'put|n')!=-1:
		return False
		index=1
	else:
		word=word.lower().strip()
	#word4=re.sub(r'[^\w]', ' ', plural(word)).strip().replace(' ','') # remove any symbols
		word4=plural(word).strip().replace(' ','')
		#print word4
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
		if string.find(word,'MH17-?')!=-1 or string.find(word,'PUT|N')!=-1:
			result==False
			index=1
	#print string.find(word,'MH17-?')
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
		if word!='' and word[-2]!='-':
			separated_word=word.split('-') # this is used to check the combined words
		else:
			separated_word=[]
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
	print radio
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
		if string.find(word,'\"')==-1:
			word='\"'+word+'\"'
	elif index==2:
		if string.find(word,'\"')==-1:
			word=word+'\"'
	elif index==3:
		if string.find(word,'\"')==-1:
			word='\"'+word
	elif index==4:
		if string.find(word,'\'s')==-1:
			word=word+'\'s'
	elif index==5:
		if string.find(word,':')==-1:
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
    elif word.endswith('+'):
    	return word[:-1]
    elif word.endswith('-'):
    	return word[:-1]   
    else:
        return word
# end of function

# this is used to for hierachical correction
def Hierachical_Correction(error_mapping,error,before_error,after_error,transcript_dict,daily_dict,event_dict,special_dict,number,alpha, beta):
	# merge the transcript_dict and special_dict
	#print error+" error"
	#print str(error_mapping.has_key(error))+" haserror"
	if error_mapping.has_key(error):
		return error_mapping[error]
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



def correct(English_dict,r):
	if str(r[3])=='ProgramTitle':
		update='' # update is the one we send to database 
		global num_total_sentence
		num_total_sentence=num_total_sentence+1
		id=r[0]
		print id
		program=r[1].split('_')
		time=str(program[len(program)-2])
		time=time[0:4]+'-'+time[4:6]+'-'+time[6:8]  # this is the time of this video
		daily_dict=creat_daily_dict(path_daily_dict,time) # daily_dict
		sentence=r[4]
		sentence=sentence.replace('\n',' Thisisusedtoseparatelines ')
		sentence=sentence.lower()
		sentence1=sentence.split(' ')
		correct_sentence=sentence.split(' ')
		transcript_dict=creat_transcript_dict(path_transcrip_dict,id) # transcript_dict
		special_dict=creat_special_dict(path_special_dict); # special_dict
		error_mapping=creat_Mapping(path_error_mapping)
		# build event_dict
		program_title=(r[1]+'_'+r[2]).strip()
		cursor_event_id = conn.cursor()
		count1=cursor_event_id.execute('select distinct(eventId) from EventVideoLinking where videoId=\''+program_title+'\'')
		results_event_id = cursor_event_id.fetchall()
		eventid=''
		for event in results_event_id:
			eventid=str(event[0])
		event_dict=creat_event_dict(path_event_dict,eventid)# event_dict
		# end of building event_dict

		errorlist=Check_Sentence(English_dict,transcript_dict,special_dict, sentence1)
		#  Case 1: sentence make no sense
		if errorlist=="thissentencemakesnosense":  
			update='This sentence makes no sense.'
			global num_invalid_sentence
			num_invalid_sentence=num_invalid_sentence+1
		#  Case 2: No error
		elif len(errorlist)==0:
			update=r[4]
			global num_no_error
			num_no_error=num_no_error+1
		#  Case 3: Have errors
		else:
			for errorid in errorlist:  # errorid start from 1 to len(sentence1)-1
				global num_errors
				num_errors=num_errors+1
				if errorid==1:
					before_error=''
					after_error=correct_sentence[errorid+1]
				elif errorid==len(sentence1)-1:
					before_error=correct_sentence[errorid-2]
					after_error=''
				else:
					before_error=correct_sentence[errorid-2]
					after_error=correct_sentence[errorid+1]
				error=correct_sentence[errorid-1]
				#print error
				corr=Hierachical_Correction(error_mapping,error,before_error,after_error,transcript_dict,daily_dict,event_dict,special_dict,5,1,0)
				# Case4: if we cannot correct this word
				if corr.strip()==error.strip():
					global num_cannot_correct
					num_cannot_correct=num_cannot_correct+1
					correct_sentence[errorid-1]="[cannot correct: "+corr+"]" 
				# Case5: if we can correct this word 
				else:
					global num_corrected
					num_corrected=num_corrected+1
					special_index=special_symbol(error)
					#print corr+' before'
					corr=recover_special_symbot(corr,special_index);
					#print corr+' after'
					correct_sentence[errorid-1]=corr
			for word1 in correct_sentence:
				update=update+word1+' '
		update=update.replace(' thisisusedtoseparatelines ','\n')
		return update	


# Main function

# 30.000->30,000
def correct_number (sentence):
	words=sentence.split(' ')
	result=''
	for word in words:
		wordnumber=word.replace('.','')
		wordnum1=word.replace(',','')
		if check_number(wordnumber) or check_number(wordnum1):
			after1=word.split('.')
			if len(after1)>1:
				after=after1[1]
				#print after+' fff'
				if after!='':
					if len(after)==3: # if 30.000 000=0, we replace . with ,
						word=word.replace('.',',')
		result=result+word+' '
	return result

# 40 000-> 40,000
def correct_number_without_comma(sentence):
	flag=0;
	temp=''
	words=sentence.split(' ')
	index=0
	theone=0;
	result=''
	for word in words:
		if flag==0:
			if check_number(word):
				flag=1
				temp=word
			else:
				flag=0
				temp=''
		else:
			if check_number(word) and len(word)==3: # the word is a number and 3 digits
				theone=index
			else: 
				flag=0
				temp=''
		index=index+1
	if theone==0: # which means this sentence is correct
		return sentence
	else:
		for i in range(0,len(words)-1):
			realword=words[i]
			if i==theone-1:
				realword=realword+','
				result=result+realword
			else:
				result=result+realword+' '
		return result









now = datetime.datetime.now()
print now
starttime = {}
for i in range(0,25):
    time=24*i
    starttime[str(now - datetime.timedelta(hours=time)).split(' ')[0].replace('-','')]=1


# we merge the english dict and the mined dict 
English_dict=creat_English_dict(path_English_dict) #http://www-01.sil.org/linguistics/wordlists/english/
Mined_dict=creat_Mined_dict(path_Mined)
dictMerged2=dict(English_dict, **Mined_dict)
English_dict=dictMerged2
# merge dictions end

num_invalid_sentence=0
num_errors=0
num_corrected=0
num_cannot_correct=0
num_no_error=0
num_total_sentence=0

# this is used to set up the DB sentence
DB_Info(DB_path)


conn_lock = MySQLdb.connect(host=Configuration_DB[0], user=Configuration_DB[1],passwd=Configuration_DB[2], db=Configuration_DB[3])
cursor_lock = conn_lock.cursor()
#count = cursor.execute(sqlcommand)
count_lock = cursor_lock.execute('select * from Configuration where id=1')
cursor_lock.scroll(0,mode='absolute')
results_lock = cursor_lock.fetchall()  
lock_index='0'
transcriptIndex=''

for r in results_lock:
	lock_index=str(r[10])
	transcriptIndex=str(r[1])
	print r[10]
#lock_index='0'

if lock_index=='0':
	cursor_update1 = conn_lock.cursor()
	sql='update Configuration set Lock_Correction=1 where id=1'		
	cursor_update1.execute(sql)
	conn_lock.commit()

	conn = MySQLdb.connect(host=Caption_DB[0], user=Caption_DB[1],passwd=Caption_DB[2], db=Caption_DB[3])
	conn_update = MySQLdb.connect(host=Caption_DB[0], user=Caption_DB[1],passwd=Caption_DB[2], db=Caption_DB[3])
	cursor = conn.cursor()
	#count = cursor.execute(sqlcommand)
	count = cursor.execute('select * from VideoCaption where id<+'+transcriptIndex)
	#count = cursor.execute('select * from VideoCaption where id=53456')
	#count = cursor.execute('select * from VideoCaption where id<100')
	cursor.scroll(0,mode='absolute')
	results = cursor.fetchall()  

	for r in results: 

		program=r[1].split('_')
		time=str(program[len(program)-2])
		#if str(r[3])=='ProgramTitle' :
		if str(r[3])=='ProgramTitle' and starttime.has_key(time):
			id=r[0]
			
			update=''
			try:
				update=correct(English_dict,r)
			except Exception, e:
				print e
				print traceback.format_exc()
				update=''
				num_invalid_sentence=num_invalid_sentence+1
		
			cursor_update = conn_update.cursor()
			update=update.replace('\\','')
			update=update.replace('\'','\\\'').strip();
			print update
			# if a sentense makes no sense or it contains word that cannot be corrected, we just do not update it.
			if (update.find('This sentence makes no sense') == -1) and (update.find('[cannot correct:') == -1):
				# if the sentence makes no sense, does not update it
				update=update.upper()
				update=correct_number(update)
				update=correct_number_without_comma(update)
				sql='update VideoCaption set CorrectedText=\''+update+'\' where id='+str(id)		
				print sql
				cursor_update.execute(sql)
				conn_update.commit()

	
	Evaluation="Results of correction:"+'\n' +'Number of invalid sentences: '+str(num_invalid_sentence)+'\n'+'Number of sentences with no error: '+str(num_no_error)+'\n'+'Number of errors: '+str(num_errors)+'\n'+'Number of errors that cannot be corrected: '+str(num_cannot_correct)+'\n'+'Number of errors can be corrected: '+str(num_corrected)+'\n'+'Number of total sentences: '+str(num_total_sentence)+'\n'

	write_to_file(path_result,Evaluation)

	sql='update Configuration set Lock_Correction=0 where id=1'		
	cursor_update1.execute(sql)
	conn_lock.commit()
	conn_lock.close()
	conn_update.close()
	conn.close() 



