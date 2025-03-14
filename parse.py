import html
import os
import time
from bs4 import BeautifulSoup
import json

def parse_sets_data(doc):
    sets_table = doc.select('#ContentPlaceHolder1_EvalsContentPlaceHolder_pnlSETs')
    if len(sets_table) == 0:
        return []
    sets_table = sets_table[0]
    table_rows = sets_table.find_all('tr')[1:]
    #print(table_rows)
    inst_data = []
    attributes = ["source", "instructor", "course", "term", "submitted", "enrolled", "avg grade recieved", "avg hours worked", "student learning", "course structure", "class environment"]
    for i in range(len(table_rows)):
        table_cols = table_rows[i].find_all('td')
        #print(table_cols)
        enrol_sub = [text for text in table_cols[3].stripped_strings]
        enrolled = str(round(int(enrol_sub[0])*float(enrol_sub[1][1:enrol_sub[1].index('%')])/100)) if enrol_sub[0].isdigit() else "N/A"
        data = ["sets", table_cols[0].get_text(), table_cols[1].find('span').get_text(), table_cols[2].get_text(), enrolled, enrol_sub[0], table_cols[4].get_text(), table_cols[5].get_text(), table_cols[6].find('div').get_text(), table_cols[7].find('div').get_text(), table_cols[8].find('div').get_text()]
        for d in range(len(data)):
            start = 0
            while start < len(data[d]) and not data[d][start].isalnum(): 
                start += 1
            if start < len(data[d]):
                data[d] = data[d][start:]
            else:
                data[d] = ''
            end = len(data[d])-1
            while end >= 0 and not data[d][end].isalnum() and not data[d][end] == ')':
                end -= 1
            data[d] = data[d][:end+1]
        inst_data.append({key:val for key, val in zip(attributes, data)})
    return inst_data

def parse_capes_data(doc):
    capes_table = doc.select('#ContentPlaceHolder1_EvalsContentPlaceHolder_pnlCAPEs')
    if len(capes_table) == 0:
        return []
    capes_table = capes_table[0]
    table_rows = capes_table.find_all('tr')[1:]
    inst_data = []
    attributes = ["source", "instructor", "course", "term", "submitted", "enrolled", "avg grade recieved", "avg hours worked"]
    for i in range(len(table_rows)):
        table_cols = table_rows[i].find_all('td')
        #print(table_cols)
        data = ["capes", table_cols[0].get_text(), table_cols[1].find('span').get_text(), table_cols[2].get_text(), table_cols[3].find('span').get_text(), table_cols[4].get_text(), table_cols[5].find('span').get_text(), table_cols[6].get_text()]
        for d in range(len(data)):
            start = 0
            while start < len(data[d]) and not data[d][start].isalnum(): 
                start += 1
            if start < len(data[d]):
                data[d] = data[d][start:]
            else:
                data[d] = ''
            end = len(data[d])-1
            while end >= 0 and not data[d][end].isalnum() and not data[d][end] == ')':
                end -= 1
            data[d] = data[d][:end+1]
        inst_data.append({key:val for key, val in zip(attributes, data)})
    return inst_data