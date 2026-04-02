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

<<<<<<< database
def Loop(file, inverted_index, cursor, connection):
    page = readFile(file)
    InvertedIndex(page, inverted_index)
    DataBase(inverted_index, cursor, connection)
=======
def createDatabase():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public."InvertedIndex"(
            "Word" text COLLATE pg_catalog."default" NOT NULL,
            "Links" integer[] NOT NULL,
            CONSTRAINT "InvertedIndex_pkey" PRIMARY KEY ("Word")
        )
        TABLESPACE pg_default;
        ALTER TABLE IF EXISTS public."InvertedIndex"
            OWNER to postgres;"""
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public."Links"(
            "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
            "Link" text COLLATE pg_catalog."default"
        )   
        TABLESPACE pg_default;
        ALTER TABLE IF EXISTS public."Links"
        OWNER to postgres;"""
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public."LinkWeight"(
            "ID" integer,
            "linkID" integer,
            "In-count" integer,
            "Out-count" integer,
            "Weight Ratio" real
        )
        TABLESPACE pg_default;
        ALTER TABLE IF EXISTS public."LinkWeight"
            OWNER to postgres;"""
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public."Linking"(
            "ID" integer,
            "LinkID (source)" integer,
            "LinkID (destination)" integer
        )
        TABLESPACE pg_default;
        ALTER TABLE IF EXISTS public."Linking"
            OWNER to postgres;"""
    )
    connection.commit()

def resetDatabase():
    cursor.execute('TRUNCATE TABLE "InvertedIndex", "Links" RESTART IDENTITY CASCADE;')
    connection.commit()
>>>>>>> local


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

<<<<<<< database
file = ['Calamity Crabulon.txt', "Minecraft.txt"]
=======
##Main Program
def main():
    import crawler as c
    createDatabase()
    resetDatabase()
    dictionary = c.crawler(2, "https://minecraft.wiki/")
    links_into_database(dictionary)
    words_into_database(dictionary)
>>>>>>> local

for file in file:
    Loop(file, inverted_index, cursor, connection)

connection.close()
cursor.close()