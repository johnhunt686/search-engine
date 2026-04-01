import psycopg2
import os
import nltk
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords

##Database Stuff
connection = psycopg2.connect(host="localhost", dbname="SearchEngine", user="postgres", password="1234", port=41204)
cursor = connection.cursor()

##Globals
all_links = []
lancaster_stemmer = LancasterStemmer()
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def resetDatabase():
    cursor.execute('TRUNCATE TABLE "InvertedIndex", "Links" RESTART IDENTITY CASCADE;')
    connection.commit()

##Puts the inverted index into the database. (Columns: Word, ID[])
def words_into_database(dictionary):
    ##Makes a map for linhks and their ID
    inverted_index = InvertedIndex(dictionary)
    cursor.execute("""
                   SELECT "ID", "Link"
                   FROM "Links";"""
                   )
    link_to_id = {Link: ID for ID, Link in cursor.fetchall()}
    
    ##Data is a list of words and their IDs
    data = []
    for word, links in inverted_index.items():
        link_ids = [link_to_id[link] for link in links if link in link_to_id]
        data.append((word, link_ids))

    ##Queries data into the database
    cursor.executemany("""
            INSERT INTO "InvertedIndex" ("Word", "Links") 
            VALUES (%s, %s)
            ON CONFLICT ("Word") DO UPDATE
            SET "Links" = EXCLUDED."Links";""",
            data
        )
    connection.commit()

##Makes an InvertedIndex of words and links
def InvertedIndex(dictionary):
    ##InvertedIndex Form -> {Words, [Link1, link2]}
    inverted_index = {}
    for page in dictionary:
        for word in dictionary[page][1]:
            if word not in inverted_index:
                inverted_index[word] = []
            if page not in inverted_index[word]:
                inverted_index[word].append(page)
    return inverted_index

##Put all links into a table and set ID
def links_into_database(dictionary):
    ##Dictionary Format: linkOutputs[page] = (links, pageContent)
    ##Finds links already in the database
    cursor.execute('SELECT "Link" FROM "Links";')
    existing_links = set(row[0] for row in cursor.fetchall())
    
    ##Sets all_links to everything not in database already
    all_links = set()
    for page in dictionary:
        all_links.update(dictionary[page][0])
        all_links.add(page)
    all_links = [(link,) for link in all_links if link not in existing_links]

    data = [(link,) for link in all_links]
    cursor.executemany("""
            INSERT INTO "Links" ("Link") 
            VALUES (%s)
            ON CONFLICT DO NOTHING;""",
            data
        )

    connection.commit()

##Stems a list of words
def documentStemmer(list):
    return [lancaster_stemmer.stem(word) for word in list]

##Trims a list of words. Calls  the removeStopWords() and removeDuplicates() functions.
def trimList(list):
    return removeDuplicates(removeStopWords(list))

##Removes stopwords from a list
def removeStopWords(list):
    return [word for word in list if word not in stop_words]

##Removes duplicates from a list
def removeDuplicates(list):
    return sorted(set(list), key=lambda x:list.index(x))

##Main Program
def main():
    import crawler as c
    resetDatabase()
    dictionary = c.crawler(2, "https://minecraft.wiki/")
    links_into_database(dictionary)
    words_into_database(dictionary)

    connection.close()
    cursor.close()
    return

main()