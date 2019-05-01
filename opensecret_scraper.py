import openpyxl
import pandas as pd
from bs4 import BeautifulSoup
import logging
import time
from urllib.request import Request, urlopen
import string


# Import Python Libraries
import urllib.request
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pdb



page_num = 1
PAUSE_TIME = 5
INPUT_FILE, INPUT_SHEET = 'input.xlsx', 'input'
OUTPUT_FILE, OUTPUT_SHEET = 'output.xlsx', 'output'
INPUT_HEADERS = ['NAME','DIRECTOR_DETAIL_ID','FIRST_NAME','LAST_NAME']
OUTPUT_HEADERS = ['CONTRIBUTOR_LNAME','CONTRIBUTOR_FNAME','OCCUPATION','YEAR','AMOUNT','RECIPIENT','PARTY']
URL_TEMPLATE = 'https://www.opensecrets.org/donor-lookup/results?name=FIRST_NAME+LAST_NAME&page=PAGE_NUM&cycle=&state=&zip=&employ=COMPANY&cand='
'''
TODO: handle multiple pages
logic: 
    -get number of results
    -calculate number of pages required
    -create url per pages
    -get data from URL, add to df
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
        data[OUTPUT_HEADERS[3]] = columns[3].text.strip().split('-')[-1].strip()
        data[OUTPUT_HEADERS[4]] = columns[4].text.strip()
        data[OUTPUT_HEADERS[5]] = columns[5].text.strip().split('(')[0].strip()
        data[OUTPUT_HEADERS[6]] = columns[5].text.strip().split('(')[1].strip()[:-1]
        data_list.append(data)
    return data_list

def get_urls(file):
    wb = openpyxl.load_workbook(INPUT_FILE)
    ws = wb[INPUT_SHEET]
    rows = list(ws.iter_rows())
    input_data = rows[1:] 
    input_data_values = []
    for row in input_data:
        new_row = [x.value for x in row]
        input_data_values.append(new_row)
    urls = []
    for row in input_data_values:
        company = clean(row[0])
        first_name = clean(row[2])
        last_name = clean(row[3])
        url = URL_TEMPLATE.replace('COMPANY',company).replace('FIRST_NAME',first_name).replace('LAST_NAME',last_name).replace('PAGE_NUM', str(page_num))
        urls.append(url)
    wb.close()
    return urls, input_data_values

def get_html(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    web_page = urlopen(req).read()
    soup = BeautifulSoup(web_page,'html.parser')
    return soup

def clean(s):
    s = s.translate(str.maketrans('', '', string.punctuation)).lower()
    s = '+'.join([x for x in s.split() if not x == 'inc'])
    return s
    
def run(file):

    df = pd.DataFrame()
    urls,input_data = get_urls(file)
    
    # Go through Each Row and Define a URL
    for i in range(len(urls)):
        print(urls[i])

        # Go Through Pages
        Condition = True
        while Condition:
            
            # Perform a request to check page index and compare with max index
            
            current_data = input_data[i]

            employ_name = clean(current_data[0])
            donor_name = clean(current_data[2]) + '+' + clean(current_data[3])

            print(employ_name)
            print(donor_name)
            
            input("Next\n\n")
            
            pdb.set_trace()
            
            current_index, page_final = ScrapeCurrentInfo(page_num,employ_name,donor_name)
                
            if(int(page_final.replace(",","")) > 500):
                print("Max Page limit, can't scrape \n\n\n\n\n")
                Condition = False
                break

            # Perform a request and get the actual data
            soup = get_html(urls[i])
            
            try:
                data = get_data(soup,input_data[i])
            except:
                continue
            for d in data:
                df = df.append(d,ignore_index=True)
            df = df.drop_duplicates()
            time.sleep(PAUSE_TIME)


            if(current_index == page_final):
                break

            # increment page number by 1
            if(current_index != page_final):
                page_num += 1
        

    return df



def ScrapeCurrentInfo(page_num_input,employ_name,donor_name):


    target_link = "https://www.opensecrets.org/donor-lookup/results?name="+ \
        donor_name+"&cycle=&state=&zip=&employ="+ employ_name +"&cand=" \
            + "&page=" + str(page_num_input)

    # I am able to get the soup
    response = requests.get(target_link)
    soup = BeautifulSoup(response.text)


    donor_look = soup.findAll("div",{"class":"DonorLookupSplash--results u-richtext u-mt4"})[0]

    page_range = donor_look.find("strong")
    current_index = page_range.contents[0].split(' ')[-1]

    print(current_index)

    current_page = donor_look.findAll("span",{"style":"font-size:14px;"})
    page_final = current_page[0].contents[0].strip('.')


    print(current_index)
    print(page_final)

    return current_index,page_final




if __name__ == '__main__':
    df = run(INPUT_FILE)
    df.to_excel(OUTPUT_FILE, index=False)
