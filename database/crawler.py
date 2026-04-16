from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collections import deque

driver = None
visitedPages = set()
sitesToVisit = deque()
pages_crawled = 0

def scrapper(page, masterUrl, driver):
    from InvertedIndex import trimList
    linkOutputs = {}

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
    return linkOutputs

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

def createDriver():
    global driver
    
    options = Options()
    options.headless = True
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)

def crawler(numIterations, startingURL):
    global driver
    global pages_crawled
    
    if driver is None:
        createDriver()

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
        linkOutputs = scrapper(page, masterUrl, driver)
        currentIteration = currentIteration + 1
        pages_crawled += 1

        if pages_crawled % 50 == 0:
            closeDriver()
            createDriver()

    return linkOutputs

