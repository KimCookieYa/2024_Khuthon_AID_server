from datetime import datetime
from dateutil.relativedelta import relativedelta
import imapclient
import re
import pyzmail
import pandas as pd
import random
import numpy as np
from bs4 import BeautifulSoup
from keybert import KeyBERT
import urllib


def cleasing(text):
    pattern = r"(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
    text = re.sub(pattern, '  ', text)
    pattern = '[\t\n\r\f\v]'
    text = re.sub(pattern, '  ', text)
    pattern = '[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]'
    text = re.sub(pattern, '  ', text)
    return text



def make_mail_list(id, password) :
    imap_obj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    imap_obj.login(id, password)
    imap_obj.select_folder('INBOX')
    
    tmp = datetime.today() - relativedelta(months=2)
    base_date = str(tmp.day) + '-' + tmp.strftime('%B')[:3] + '-' + str(tmp.year)
    

    ids_old = imap_obj.search(['BEFORE', base_date])
    ids_new = imap_obj.search(['SINCE', base_date])
    
    how_many_mail = 3
    np.random.seed(3)
    ids_old_tmp = np.random.choice(ids_old, how_many_mail, replace=False)
    ids_new_tmp = np.random.choice(ids_new, how_many_mail, replace=False)
    
    ids = np.append(ids_new_tmp, ids_old_tmp).tolist()
    random.shuffle(ids)
    
    raw_msg = imap_obj.fetch(ids, ['BODY[]'])
    

    base_key = list(raw_msg[ids[0]].keys())[1]

    
    tmp = []
    for i in ids :
        msg = pyzmail.PyzMessage.factory(raw_msg[i][base_key])
        if msg.text_part != None :
            a = msg.text_part.get_payload().decode(msg.text_part.charset)
            clean_a = cleasing(a)
            tmp.append([i, clean_a, msg.get_addresses('from')])
        else :
            a = msg.html_part.get_payload().decode(msg.html_part.charset)
            clean_a = BeautifulSoup(str(a), "lxml").text
            clean_a = cleasing(clean_a)
            tmp.append([i, clean_a, msg.get_addresses('from')])
            
    tmp = pd.DataFrame(tmp, columns = ['Mail_ID', '내용', '보낸 사람'])
    
    kw_model = KeyBERT()
    
    all_answer = []
    for i in tmp['내용'] :
        doc = str(i)
        keywords_mmr = kw_model.extract_keywords(doc,keyphrase_ngram_range=(3,5),use_maxsum=True,use_mmr=True,top_n = 1,diversity = 0.3)
        tmp_b = keywords_mmr[0][0].split()
        tmp_a = []
        for j in tmp_b :
            for k in range(len(tmp_b)) :
                if len(tmp_b[k]) < 10 and tmp_b[k] not in tmp_a:
                    tmp_a.append(tmp_b[k])
        all_answer.append(tmp_a)
    tmp = tmp[['Mail_ID', '보낸 사람']]
    tmp['태그'] = all_answer
    
    tmp = tmp.to_json(orient='records', force_ascii=False)
    return tmp


def delete_mail(ids, id = 'gktjrgus8@gmail.com', password = 'yimnwkfnqrflsgxd') : 
    
    imap_obj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    imap_obj.login(id, password)
    imap_obj.select_folder('INBOX')
    print(imap_obj.delete_messages(ids))
    imap_obj.logout()
    
    return 0
    
def check_mail(ids, id = 'gktjrgus8@gmail.com', password = 'yimnwkfnqrflsgxd') :
    
    imap_obj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    imap_obj.login(id, password)
    imap_obj.select_folder('INBOX')
    
    tmp = datetime.today() - relativedelta(months=2)
    raw_msg = imap_obj.fetch(ids, ['BODY[]'])
    base_key = list(raw_msg[ids[0]].keys())[1]
    
    tmp = []
    for i in ids :
        msg = pyzmail.PyzMessage.factory(raw_msg[i][base_key])
        if msg.text_part != None :
            a = msg.text_part.get_payload().decode(msg.text_part.charset)
            clean_a = cleasing(a)
            tmp.append([clean_a, msg.get_addresses('from')])
        else :
            a = msg.html_part.get_payload().decode(msg.html_part.charset)
            clean_a = BeautifulSoup(str(a), "lxml").text
            clean_a = cleasing(clean_a)
            tmp.append([clean_a, msg.get_addresses('from')])
            
    tmp = pd.DataFrame(tmp, columns = ['내용', '보낸 사람'])
    tmp = tmp.to_json(orient='records', force_ascii=False)
    return tmp
