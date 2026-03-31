from bs4 import BeautifulSoup
from selenium import webdriver
from collections import deque


visitedPages = set()
sitesToVisit = deque()

def scrapper(page, masterUrl):
    
    #headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    #              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    #}
    # webPage = requests.get(page, headers=headers)
    # soup = BeautifulSoup(webPage.text, 'html.parser')
    driver = webdriver.Chrome()
    driver.get(page)
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')


    with open("links.txt", "w", encoding="utf-8") as out:
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if '#' not in href and '=' not in href and '.' not in href and ':' not in href:
                    out.write(masterUrl + href + "\n")
                    if masterUrl + href not in sitesToVisit and masterUrl + href not in visitedPages:
                        sitesToVisit.append(masterUrl + href) 
    #print(soup.get_text())
    with open("output.txt", "w", encoding="utf-8") as out:
        out.write("Url: " + page + "\n")
        out.write(soup.get_text())
    #print(sitesToVisit)
    visitedPages.add(page)
    driver.quit()


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
            page = sitesToVisit.popleft()
            if(page not in visitedPages):
                break
        scrapper(page, masterUrl)
        currentIteration = currentIteration + 1


        



crawler(20, "https://minecraft.wiki/")