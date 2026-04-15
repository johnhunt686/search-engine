from bs4 import BeautifulSoup
from selenium import webdriver
from collections import deque

driver = None
visitedPages = set()
sitesToVisit = deque()
linkOutputs = {}

def scrapper(page, masterUrl, driver):
    from InvertedIndex import trimList
    
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

    firstParagraph = ""
    paragraph = soup.find_all("p")
    for p in paragraph:
        firstParagraph = p.get_text(separator = " ", strip = True)
        if firstParagraph and len(firstParagraph) > 200:
            break

    linkOutputs[page] = (links, pageContent, pageTitle, firstParagraph)
    visitedPages.add(page)

def splitStrings(string):
    words = []
    for line in string.splitlines():
        line = line.replace("(", "").replace(")", "")
        words_in_line = line.lower().split()
        words.extend(words_in_line)
    return words

def closeDriver():
    global driver
    if driver is not None:
        driver.quit()
        driver = None

def crawler(numIterations, startingURL):
    global driver
    
    if driver is None:
        driver = webdriver.Chrome()

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
        scrapper(page, masterUrl, driver)
        currentIteration = currentIteration + 1
    
    return linkOutputs

def getDictionary():
    return  linkOutputs
