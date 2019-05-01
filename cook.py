# Import Python Libraries
import urllib.request
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


# name, and employ request in api,
# more efficient way of doing this later.
donor_name = "Mohammed"
employ_name = ""


def ScrapeCurrentInfo(pageNum):
    
    print(pageNum)
    target_link = "https://www.opensecrets.org/donor-lookup/results?name="+ \
        donor_name+"&cycle=&state=&zip=&employ="+ employ_name +"&cand=" \
            + "&page=" + str(pageNum)

    # I am able to get the soup
    response = requests.get(target_link)
    soup = BeautifulSoup(response.text)

    donor_look = soup.findAll("div",{"class":"DonorLookupSplash--results u-richtext u-mt4"})[0]
    page_range = donor_look.findAll("strong")[0]
    current_index = page_range.contents[0].split(' ')[-1]

    current_page = donor_look.findAll("span",{"style":"font-size:14px;"})
    page_final = current_page[0].contents[0].strip('.')

    return ([current_index,page_final])


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





StartScrape()




