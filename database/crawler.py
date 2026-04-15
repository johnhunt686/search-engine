from bs4 import BeautifulSoup
from selenium import webdriver
from collections import deque


visitedPages = set()
sitesToVisit = deque()
linkOutputs = {}

def scrapper(page, masterUrl):
    from InvertedIndex import trimList
    driver = webdriver.Chrome()
    driver.get(page)
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')
    links = []

    for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if '#' not in href and '=' not in href and '.' not in href and ':' not in href and '%' not in href:
                    links.append(masterUrl + href)
                    if masterUrl + href not in sitesToVisit and masterUrl + href not in visitedPages:
                        sitesToVisit.append(masterUrl + href) 
    

    pageContent = soup.get_text()
    pageContent = splitStrings(pageContent)
    pageContent = trimList(pageContent)
    pageTitle = soup.title.string

    print(soup.title.name)

    linkOutputs[page] = (links, pageContent, pageTitle)
    visitedPages.add(page)

    driver.quit()


def splitStrings(string):
    words = []
    for line in string.splitlines():
        line = line.replace("(", "").replace(")", "")
        words_in_line = line.lower().split()
        words.extend(words_in_line)
    return words

def crawler(numIterations, startingURL):
    if "https://" in startingURL:
       masterUrl = startingURL.split('/', 3)[0] + '//' + startingURL.split('/', 3)[2]
    else:
        masterUrl = "https://" + startingURL.split('/')[0]
        startingURL = "https://" + startingURL
    currentIteration = 0
    sitesToVisit.append(startingURL)
    while(currentIteration < numIterations):
        while True:
            if not sitesToVisit:
                break
            page = sitesToVisit.popleft()
            if(page not in visitedPages):
                break
        scrapper(page, masterUrl)
        currentIteration = currentIteration + 1
    
    return linkOutputs

def getDictionary():
    return  linkOutputs

