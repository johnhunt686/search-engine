import psycopg2
import os
import nltk
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords

##Database Stuff
connection = psycopg2.connect(host="localhost", dbname="SearchEngine", user="postgres", password="1234", port=41204)
cursor = connection.cursor()


inverted_index = {}
lancaster_stemmer = LancasterStemmer()
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def Loop(file, inverted_index, cursor, connection):
    page = readFile(file)
    InvertedIndex(page, inverted_index)
    DataBase(inverted_index, cursor, connection)


def DataBase(inverted_index, cursor, connection):
    for word, page_ids in inverted_index.items():
        cursor.execute("""
            INSERT INTO "InvertedIndex" ("Word", "Links")
            VALUES (%s, %s)
            ON CONFLICT ("Word")
            DO UPDATE SET "Links" = (
                SELECT ARRAY(
                    SELECT DISTINCT unnest("InvertedIndex"."Links" || EXCLUDED."Links")
                )
            );
        """, (word, page_ids))
    
    connection.commit()

def InvertedIndex(page, inverted_index):
    pageID = page["id"]
    words = page["words"]

    for word in words:
        if word not in inverted_index:
            inverted_index[word] = []
        if pageID not in inverted_index[word]:
            inverted_index[word].append(pageID)

def readFile(filename):
    words = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.replace("(", "").replace(")", "")
            words_in_line = line.lower().split()
            words.extend(words_in_line)
    
    words.pop(0)
    pageID = words.pop(0)
    page_words = trimList(words)
    page_words = documentStemmer(page_words)
    page = {
        "id": pageID,
        "words": page_words
    }
    return page

def documentStemmer(list):
    return [lancaster_stemmer.stem(word) for word in list]

def trimList(list):
    return removeDuplicates(removeStopWords(list))

def removeStopWords(list):
    return [word for word in list if word not in stop_words]

def removeDuplicates(list):
    return sorted(set(list), key=lambda x:list.index(x))

file = ['Calamity Crabulon.txt', "Minecraft.txt"]

for file in file:
    Loop(file, inverted_index, cursor, connection)

connection.close()
cursor.close()