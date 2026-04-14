import psycopg2
import os
import nltk
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords

##Globals
all_links = []
lancaster_stemmer = LancasterStemmer()
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

if __name__ == "__main__":
    ##Database Stuff
    connection = psycopg2.connect(host="localhost", dbname="SearchEngine", user="postgres", password="1234", port=41204)
    cursor = connection.cursor()

def deleteTables():
    cursor.execute("""
        DROP TABLE IF EXISTS "InvertedIndex", "Links", "Linking", "LinkWeight" CASCADE;"""
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
        connection.commit()

    except Exception as e:
        print(f"Error creating tables: {e}")
        connection.rollback()

##Resets the database
def resetDatabase():
    cursor.execute('TRUNCATE TABLE "InvertedIndex", "Links", "Linking" RESTART IDENTITY CASCADE;')
    connection.commit()

##Puts the relationships between links into the database
def linking_into_database(dictionary):
    link_to_id = links_to_ids()
    
    data = []
    for page, (links, pageContent, pageTitle) in dictionary.items():
        page_id = link_to_id[page]
        link_ids = [link_to_id[link] for link in links if link in link_to_id]
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
    link_to_id = links_to_ids()

    data = []
    for word, pages in inverted_index.items():
        for link, frequency in pages.items():
            if link in link_to_id:
                link_id = link_to_id[link]
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
    ##Dictionary Format: linkOutputs[page] = (links, pageContent)
    ##Finds links already in the database
    cursor.execute('SELECT "Link" FROM "Links";')
    existing_links = set(row[0] for row in cursor.fetchall())
    
    ##Sets all_links to everything not in database already
    all_links = set()
    for page in dictionary:
        all_links.update(dictionary[page][0])
        all_links.add(page)
    data = [(link,) for link in all_links if link not in existing_links]
    
    cursor.executemany("""
            INSERT INTO "Links" ("Link") 
            VALUES (%s)
            ON CONFLICT DO NOTHING;""",
            data
        )

    connection.commit()

def links_to_ids():
    cursor.execute("""
                   SELECT "ID", "Link"
                   FROM "Links";"""
                   )
    return {Link: ID for ID, Link in cursor.fetchall()}

##Stems a list of words
def documentStemmer(list):
    return [lancaster_stemmer.stem(word) for word in list]

##Trims a list of words. Calls  the removeStopWords() and removeDuplicates() functions.
def trimList(list):
    return removeStopWords(list)

##Removes stopwords from a list
def removeStopWords(list):
    return [word for word in list if word not in stop_words]

##Removes duplicates from a list
##def removeDuplicates(list):
    return sorted(set(list), key=lambda x:list.index(x))

def rank_links(query, dictionary, inverted_index, linking_table, alpha=0.5, title_weight=8):
    query_words = documentStemmer(query.lower().split())
    link_to_id = links_to_ids()

    base_scores = {}

    # Body score
    for word in query_words:
        if word in inverted_index:
            for page_id, frequency in inverted_index[word].items():
                base_scores[page_id] = base_scores.get(page_id, 0) + frequency

    # Title bonus
    for page, (links, pageContent, pageTitle) in dictionary.items():
        if page not in link_to_id:
            continue

        page_id = link_to_id[page]

        if pageTitle:
            title_words = documentStemmer(pageTitle.lower().split())

            for word in query_words:
                count_in_title = title_words.count(word)
                if count_in_title > 0:
                    base_scores[page_id] = base_scores.get(page_id, 0) + title_weight * count_in_title

    final_scores = {}
    all_pages = set(base_scores.keys()) | set(linking_table.keys())

    for page_id in all_pages:
        own_score = base_scores.get(page_id, 0)

        destinations = linking_table.get(page_id, [])
        link_score = 0

        if destinations:
            for dest in destinations:
                link_score += base_scores.get(dest, 0)
            link_score /= len(destinations)

        final_scores[page_id] = own_score + alpha * link_score

    return sorted(final_scores.items(), key=lambda x: x[1], reverse=True)


##Main Program
def main():
    from crawler import crawler
    deleteTables()
    createDatabase()
    resetDatabase()
    dictionary = crawler(5, "https://minecraft.wiki/")
    links_into_database(dictionary)
    words_into_database(dictionary)
    linking_into_database(dictionary)

    print(rank_links("Minecraft", dictionary, getInvertedIndex(), getLinking()))

    connection.close()
    cursor.close()
    return

if __name__ == "__main__":
    main()