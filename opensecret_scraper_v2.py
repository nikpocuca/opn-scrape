import openpyxl 
import pandas as pd 
from bs4 import BeautifulSoup
import logging 
import time
from urllib.request import Request, urlopen
import string
import urllib.request
import requests
import math
import copy

PAUSE_TIME = 5
INPUT_FILE, INPUT_SHEET = 'orig-input.xlsx', 'input'
OUTPUT_FILE, OUTPUT_SHEET = 'output.xlsx', 'output'
INPUT_HEADERS = ['NAME','DIRECTOR_DETAIL_ID','FIRST_NAME','LAST_NAME']
OUTPUT_HEADERS = ['CONTRIBUTOR_LNAME','CONTRIBUTOR_FNAME','OCCUPATION','DATE','YEAR','AMOUNT','RECIPIENT','PARTY']
URL_TEMPLATE = 'https://www.opensecrets.org/donor-lookup/results?name=FIRST_NAME+LAST_NAME&cycle=&state=&zip=&employ=COMPANY&cand='

'''
TODO: handle multiple pages
logic: 
    -get number of results
    -calculate number of pages required
    -create url per pages
    -get data from URL, add to df



'''
def get_num_pages(target_link):
    # I am able to get the soup
    response = requests.get(target_link)
    soup = BeautifulSoup(response.text,'lxml')
    donor_look = soup.findAll("div",{"class":"DonorLookupSplash--results u-richtext u-mt4"})[0]
    page_range = donor_look.findAll("strong")[0]
    current_index = page_range.contents[0].split(' ')[-1]
    current_page = donor_look.findAll("span",{"style":"font-size:14px;"})
    page_final = current_page[0].contents[0].strip('.')
    return int(current_index),int(page_final)
'''
# 1 hour worked on so far. 
def StartScrape():
    print("Starting Scrape")
    print("Accessing URL...")
    pageNum = 1
    Condition = True
    while Condition:
        results = ScrapeCurrentInfo(pageNum)
        current_index = results[0]
        page_final = results[1]
        if(int(page_final.replace(",","")) > 500):
            print("Max Page limit, can't scrape \n\n\n\n\n")
            Condition = False
        print("Current page is " + current_index)
        print("Final page is " + page_final)
        if(current_index != page_final):
            input("Next")
            pageNum += 1
        if(current_index == page_final):
            Condition = False
'''
def get_data(soup,input_data):
    data_list = []
    data = {INPUT_HEADERS[0]:input_data[0],INPUT_HEADERS[1]:input_data[1],INPUT_HEADERS[2]:input_data[2],INPUT_HEADERS[3]:input_data[3]}
    table = soup.find('table',attrs={'class','u-mt2'})
    rows = table.tbody.find_all('tr')
    for r in rows:
        columns = r.find_all('td')
        if len(columns) == 1: continue
        data[OUTPUT_HEADERS[0]] = columns[1].text.strip().split('\n')[0].split(',')[0].strip()
        data[OUTPUT_HEADERS[1]] = columns[1].text.strip().split('\n')[0].split(',')[1].strip()
        data[OUTPUT_HEADERS[2]] = columns[2].text.strip()
        data[OUTPUT_HEADERS[3]] = columns[3].text.strip()
        data[OUTPUT_HEADERS[4]] = columns[3].text.strip().split('-')[-1].strip()
        data[OUTPUT_HEADERS[5]] = columns[4].text.strip()
        data[OUTPUT_HEADERS[6]] = columns[5].text.strip().split('(')[0].strip()
        data[OUTPUT_HEADERS[7]] = columns[5].text.strip().split('(')[1].strip()[:-1]
        data_list.append(copy.deepcopy(data)) 
    return data_list

def get_urls(file):
    wb = openpyxl.load_workbook(INPUT_FILE) #load in input Excel Workbook
    ws = wb[INPUT_SHEET] #get input Excel Sheet
    rows = list(ws.iter_rows()) #get rows in sheet
    input_data = rows[1:] #don't use header row
    input_data_values = []
    
    for row in input_data: #convert cell object to text values
        new_row = [x.value for x in row]
        input_data_values.append(new_row)
        
    urls = []
    for row in input_data_values:
        #clean input text values (remove punctuation, make lowercase)
        company = clean(row[0]) 
        first_name = clean(row[2])
        last_name = clean(row[3])
        
        #replace values in URL
        url = URL_TEMPLATE.replace('COMPANY',company).replace('FIRST_NAME',first_name).replace('LAST_NAME',last_name)
        #print(url)
        try:
            curr_index, final_index = get_num_pages(url)
            print("The search for "+first_name+" "+last_name+" at "+company+" yeilded "+str(final_index)+" results.")
            if final_index > curr_index: #if results are over multiple pages
                num_pages = ceil(final_index/50)
                if num_pages > 10: num_pages = 10
                for p in range(num_pages): #create per page
                    page_url = url+'&page='+str(p+1)
                    #print('Appending URL '+page_url)
                    urls.append(page_url)
            else: #if there's only 1 page
                #print('Appending URL '+url)
                urls.append(url)
        except:
            continue
    wb.close()
    return urls, input_data_values

def get_html(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) #fake using browser
    web_page = urlopen(req).read() #read HTML
    soup = BeautifulSoup(web_page,'html.parser')
    return soup

def clean(s):
    if not s is None:
        s = s.translate(str.maketrans('', '', string.punctuation)).lower() #remove punctuation from string and convert to lower case
        s = '+'.join([x for x in s.split() if not (x=='inc' or x=='corp')]) #remove 'inc' from string
    else:
        s = ''
    return s
    
def run(file):
    df = pd.DataFrame() #create empty pandas DataFrame
    urls,input_data = get_urls(file) #generate URL per row of input file
    for i in range(len(urls)): #loop through URLs
        #print(urls[i])
        try:
            soup = get_html(urls[i]) #get HTML of site
            data = get_data(soup,input_data[i]) #get table data of site in form of dictionary
        except: #if error in site URL
            continue 
        for d in data:
            df = df.append(d,ignore_index=True) #append data to dataframe
        df = df.drop_duplicates() #drop duplicates
        time.sleep(PAUSE_TIME) #don't overload web server
    return df

if __name__ == '__main__':
    df = run(INPUT_FILE)
    df.to_excel(OUTPUT_FILE, index=False) #convert dataframe to Excel file