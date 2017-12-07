# -*- coding: utf-8 -*-
"""
Created on Fri Dec 01 10:48:26 2017

@author: hweilun
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys, re

"""
# use peter-thompson/Topic-modelling-using-LDA Pre-processing functions
def re_clean_list():
    # define a list of regular expression clean up to use
    re_list = []
    re_list.append(re.compile('>'))
    re_list.append(re.compile('(Message-ID(.*?\n)*X-FileName.*?\n)|'
                     '(To:(.*?\n)*?Subject.*?\n)|'
                     '(< (Message-ID(.*?\n)*.*?X-FileName.*?\n))'))
    re_list.append(re.compile('(.+)@(.+)')) # Remove emails
    re_list.append(re.compile('\s(-----)(.*?)(-----)\s', re.DOTALL))
    re_list.append(re.compile('''\s(\*\*\*\*\*)(.*?)(\*\*\*\*\*)\s''', re.DOTALL))
    re_list.append(re.compile('\s(_____)(.*?)(_____)\s', re.DOTALL))
    re_list.append(re.compile('\n( )*-.*'))
    re_list.append(re.compile('\n( )*\d.*'))
    re_list.append(re.compile('(\n( )*[\w]+($|( )*\n))|(\n( )*(\w)+(\s)+(\w)+(( )*\n)|$)|(\n( )*(\w)+(\s)+(\w)+(\s)+(\w)+(( )*\n)|$)'))
    re_list.append(re.compile('.*orwarded.*'))
    re_list.append(re.compile('From.*|Sent.*|cc.*|Subject.*|Embedded.*|http.*|\w+\.\w+|.*\d\d/\d\d/\d\d\d\d.*'))
    re_list.append(re.compile(' [\d:;,.]+ '))
    return re_list

def remove_clutter(text,re_list):
    # takes in the regular expression to remove clutter
    for i in range(len(re_list)):
        text = re.sub(re_list[i], ' ', text)
    return text
"""

# ============================
# regular expression patterns
# ============================
# pattern to extract data into structure
date_pattern = re.compile('(?<=Date:).*',re.IGNORECASE)
msgId_pattern = re.compile('(?<=: <)(.*?)(?=@)',re.IGNORECASE)
from_pattern = re.compile(r"(?<=From: )[\"']*(.*?)(?:\"|\'|\n|\<|\[|\\)",re.IGNORECASE) #note: still have to clean up names
sent_pattern = re.compile('(?<=Sent: ).*',re.IGNORECASE)
to_pattern = re.compile(r"(?<=To: )[\"']*(.*?)(?:\"|\'|\n|\<|\[|\\)",re.IGNORECASE)
subj_pattern = re.compile('(?<=Subject: )[Fw: | Fwd]*(.*)',re.IGNORECASE)
content_pattern = re.compile(r"[\t|\n]*(.*)[\n]") # only can use with clear patterns below

# patterns to clean up data
# clear_content_pattern = re.compile('(?:.*:)(.*)')
clear_header_pattern = re.compile('(?:from:.*|mime-.*|sent.*|to:.*|'
                                      'subject:.*|received:.*|date:.*|'
                                      'folder:.*|filename:.*|cc:.*|Message-ID:.*|'
                                      'X-.*|status:.*|content-.*|'
                                      'boundary[-|=].*|http.*)',re.IGNORECASE)
clear_star_pattern = re.compile('(?<=\*)[\n].*[\n](?=\*)')
clear_symbol_pattern = re.compile('[\*|\-|\=|\_]{2,}')

# ============================
# own pre-processing functions
# ============================
def uniq_set(list_item):
    return list(set(list_item))

def clean_names(list_item):
    list_item = [i.strip() for i in list_item]
    # list_item = [re.findall(parse_name_pattern,i)[0].strip() for i in list_item]
    return uniq_set(list_item)

def parse_data(content):
    # this function takes in the data and parses it and stores into
    # a json object for retrival
    c_data = {} # stores the content data
    extract_date = re.findall(date_pattern,content)
    extract_sent = re.findall(sent_pattern,content)
    extract_date.extend(extract_sent)
    # store some of the key informaion
    c_data['isValid'] = True # set data to valid
    c_data['date'] = uniq_set(extract_date)
    c_data['msgId'] = re.findall(msgId_pattern,content)
    c_data['from'] = clean_names(re.findall(from_pattern,content))
    c_data['to'] = clean_names(re.findall(to_pattern,content))
    c_data['subj'] = uniq_set(re.findall(subj_pattern,content))
    # extract contents from the email
    remove_idx = content.find('\n_____') # remove everything after this
    content = content[0:remove_idx]
    remove_idx = content.find('\n*******')
    content = content[0:remove_idx]
    content = re.sub(clear_header_pattern,'',content)
    # content = re.sub(clear_star_pattern,'',content)
    content = re.sub(clear_symbol_pattern,'',content)
    content = re.findall(content_pattern,content)
    c_data['content'] = [' '.join(content)]
    if c_data['content'][0] == '': # if there is no content
        c_data['isValid'] = False # set the validity to false
    # return the data
    return c_data

# ==================
# Program goes here!
# ==================
# change this directory to point to where the Enron data is
root_dir = 'C:\Users\hweilun\Desktop\Python\Enron'
file_content = []

# structure to store the original contents
org_content = {}

# re_list = re_clean_list()
for sub_dir, dirs, files in os.walk(root_dir):
    for file in files:
        # obtain the file name to load
        # only want to open files with NO extension!
        if file.find('.') == -1:
            file_path = os.path.join(sub_dir, file)
            f=open(file_path,'r')
            content = f.read()
            # content = remove_clutter(content,re_list)
            # content = f.readlines()
            # print content
            extract_data = parse_data(content)
            print extract_data['msgId']
            print extract_data['from']
            print extract_data['to']
            print extract_data['content']
            
             # store the original content
            if len(extract_data['msgId'])>0:
                org_content[extract_data['msgId'][0]] = {}
                org_content[extract_data['msgId'][0]]['data'] = content
            
            f.close()
            print '++++++++++++++++++++++++++++++++++++++++++'
