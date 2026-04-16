import psycopg2
import os
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords

##Globals
link_to_id_cache = {}
links_to_search = 100
all_links = []
stemmer = SnowballStemmer("english")
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

if __name__ == "__main__":
    ##Database Stuff
    connection = psycopg2.connect(host="localhost", dbname="SearchEngine", user="postgres", password="1234", port=41204)
    cursor = connection.cursor()

def deleteTables():
    cursor.execute("""
        DROP TABLE IF EXISTS "InvertedIndex", "Links", "Linking", "SearchedLinkInfo" CASCADE;"""
    )
    connection.commit()

##Creates the database
def createDatabase():
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "InvertedIndex" (
                "Word" text NOT NULL,
                "LinkID" integer NOT NULL,
                "Frequency" integer NOT NULL,
                PRIMARY KEY ("Word", "LinkID")
            )
            TABLESPACE pg_default;
            ALTER TABLE IF EXISTS public."InvertedIndex"
                OWNER to postgres;"""             
        )
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_inverted_word ON public."InvertedIndex"("Word");""")
        cursor.execute("""CREATE INDEX IF NOT EXISTS idx_inverted_linkid ON public."InvertedIndex"("Word");""")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public."Links"(
                "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
                "Link" text COLLATE pg_catalog."default" UNIQUE
            )   
            TABLESPACE pg_default;
            ALTER TABLE IF EXISTS public."Links"
            OWNER to postgres;"""
        )
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public."Linking"
            (
                "ID" integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
                "LinkID (source)" integer NOT NULL,
                "LinkID (destination)" integer[] NOT NULL,
                CONSTRAINT "Linking_pkey" PRIMARY KEY ("ID"),
                CONSTRAINT unique_source UNIQUE ("LinkID (source)")
            )
            TABLESPACE pg_default;
            ALTER TABLE IF EXISTS public."Linking"
            OWNER to postgres;"""
        )
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public."SearchedLinkInfo"
            (
                "LinkID" integer NOT NULL PRIMARY KEY,
                "Title" text COLLATE pg_catalog."default",
                "Description" text COLLATE pg_catalog."default"
            )
            TABLESPACE pg_default;
            ALTER TABLE IF EXISTS public."SearchedLinkInfo"
            OWNER to postgres;"""
        )
        cursor.execute("""
            CREATE OR REPLACE VIEW public."LinkWeight" AS
                WITH edges AS (
                    SELECT
                        l."LinkID (source)" AS source,
                        unnest(l."LinkID (destination)") AS destination
                    FROM public."Linking" l
                ),

                out_counts AS (
                    SELECT
                        source AS id,
                        COUNT(*) AS "Out-count"
                    FROM edges
                    GROUP BY source
                ),

                in_counts AS (
                    SELECT
                        destination AS id,
                        COUNT(*) AS "In-count"
                    FROM edges
                    GROUP BY destination
                )

                SELECT
                    COALESCE(o.id, i.id) AS "ID",
                    COALESCE(o."Out-count", 0) AS "Out-count",
                    COALESCE(i."In-count", 0) AS "In-count",

                    LN(1 + COALESCE(i."In-count", 0)) 
                    - LN(1 + COALESCE(o."Out-count", 0)) 
                    AS "Weight Score"

                FROM out_counts o
                FULL OUTER JOIN in_counts i
                ON o.id = i.id;"""
        )
        connection.commit()


    except Exception as e:
        print(f"Error creating tables: {e}")
        connection.rollback()

##Resets the database
def resetDatabase():
    cursor.execute('TRUNCATE TABLE "InvertedIndex", "Links", "Linking", "SearchedLinkInfo" RESTART IDENTITY CASCADE;')
    connection.commit()

def linkInfo_into_database(dictionary):
    global link_to_id_cache

    data = []
    for page, (links, pageContent, pageTitle, firstParagraph) in dictionary.items():
        if page not in link_to_id_cache:
            continue

        link_id = link_to_id_cache[page]

        description = dictionary[page][3]

        title = pageTitle if pageTitle else None
        data.append((link_id, title, description))
    
    cursor.executemany("""
        INSERT INTO "SearchedLinkInfo" ("LinkID", "Title", "Description")
        VALUES (%s, %s, %s)
        ON CONFLICT ("LinkID") DO UPDATE
        SET "Title" = EXCLUDED."Title",
            "Description" = EXCLUDED."Description";
    """, data)
    connection.commit()

##Puts the relationships between links into the database
def linking_into_database(dictionary):
    global link_to_id_cache
    
    data = []
    for page, (links, pageContent, pageTitle, firstParagraph) in dictionary.items():
        page_id = link_to_id_cache[page]
        link_ids = [link_to_id_cache[link] for link in links if link in link_to_id_cache]
        data.append((page_id, link_ids))

    ##Queries data into the database
    cursor.executemany("""
            INSERT INTO "Linking" ("LinkID (source)", "LinkID (destination)") 
            VALUES (%s, %s)
            ON CONFLICT ("LinkID (source)") DO NOTHING;""",
            data
        )
    connection.commit()

##Puts the inverted index into the database. (Columns: Word, ID[])
def words_into_database(dictionary):
    inverted_index = createInvertedIndex(dictionary)
    global link_to_id_cache

    data = []
    for word, pages in inverted_index.items():
        for link, frequency in pages.items():
            if link in link_to_id_cache:
                link_id = link_to_id_cache[link]
                data.append((word, link_id, frequency))

    cursor.executemany("""
        INSERT INTO "InvertedIndex" ("Word", "LinkID", "Frequency")
        VALUES (%s, %s, %s)
        ON CONFLICT ("Word", "LinkID") DO UPDATE
        SET "Frequency" = EXCLUDED."Frequency";
    """, data)

    connection.commit()

##Makes an InvertedIndex of words and links
def createInvertedIndex(dictionary):
    inverted_index = {}

    for page in dictionary:
        words = dictionary[page][1] 
        words = documentStemmer(words)

        for word in words:
            if word not in inverted_index:
                inverted_index[word] = {}

            if page not in inverted_index[word]:
                inverted_index[word][page] = 0

            inverted_index[word][page] += 1

    return inverted_index

def getInvertedIndex():
    cursor.execute('SELECT "Word", "LinkID", "Frequency" FROM "InvertedIndex"')
    rows = cursor.fetchall()

    inverted_index = {}
    for word, link_id, frequency in rows:
        word = word.lower()
        if word not in inverted_index:
            inverted_index[word] = {}
        inverted_index[word][link_id] = frequency
    return inverted_index

def getLinking():
    cursor.execute('SELECT "LinkID (source)", "LinkID (destination)" FROM "Linking"')
    rows = cursor.fetchall()

    linking_table = {}
    for source, destinations in rows:
        linking_table[source] = destinations
    return linking_table

##Put all links into a table and set ID
def links_into_database(dictionary):
    global link_to_id_cache

    all_links = set()
    for page, (links, pageContent, pageTitle, firstParagraph) in dictionary.items():
        all_links.add(page)
        all_links.update(links)

    data = [(link,) for link in all_links]

    cursor.executemany("""
        INSERT INTO "Links" ("Link")
        VALUES (%s)
        ON CONFLICT ("Link") DO NOTHING;
    """, data)

    cursor.execute("""
        SELECT "ID", "Link"
        FROM "Links"
        WHERE "Link" = ANY(%s);
    """, (list(all_links),))

    link_map = {link: link_id for link_id, link in cursor.fetchall()}

    link_to_id_cache.update(link_map)

##Stems a list of words
def documentStemmer(list):
    return [stemmer.stem(word) for word in list]

##Trims a list of words. Calls  the removeStopWords() and removeDuplicates() functions.
def trimList(list):
    return removeStopWords(list)

##Removes stopwords from a list
def removeStopWords(list):
    return [word for word in list if word not in stop_words]

##Main Program
def main():
    from crawler import crawler, closeDriver
    dictionary = {}
    createDatabase()
    for i in range(links_to_search):
        new_page = crawler(1, "https://minecraft.wiki/")
        dictionary.update(new_page)
        links_into_database(new_page)
        words_into_database(new_page)
        linking_into_database(new_page)
        linkInfo_into_database(new_page)

    closeDriver()
    connection.close()
    cursor.close()
    return

if __name__ == "__main__":
    main()