#include "search_engine.h"
#include <string>
#include <vector>
#include <iostream>
#include <pqxx/pqxx>
#include <algorithm>
#include <cctype>
#include <sstream>


int main(int argc, char* argv[])
{
    if (argc == 0){
        return -1;
    }
    
    //first argument is always the query
    std::string query;
    int count;
    std::string demo;

    for (int i=1;i<argc;i++){
        std::string str(argv[i]);

        size_t pos = str.find('='); 

        if (pos == std::string::npos) {
            std::cerr << "Invalid format\n";
            return 1;
        }

        std::string key = str.substr(0, pos);
        std::string value = str.substr(pos + 1);

        if(key == "query"){
            query = value;
        } else if(key == "count"){
            try{
                count = std::stoi(value);
                if (count < 1){
                    count = 1;
                }
            }
            catch(const std::exception& e){
                std::cerr << e.what() << '\n';
            }
            
            
        } else if(key == "demo"){
            demo = value;
        } else {
            return -1;
        }
    }
    std::vector<SearchResult> result;
    search(&query, result, count);

    auto escape_json = [](const std::string& s){
        std::string out;
        for (char c : s) {
            switch (c) {
                case '"': out += "\\\""; break;
                case '\\': out += "\\\\"; break;
                case '\b': out += "\\b"; break;
                case '\f': out += "\\f"; break;
                case '\n': out += "\\n"; break;
                case '\r': out += "\\r"; break;
                case '\t': out += "\\t"; break;
                default: out += c; break;
            }
        }
        return out;
    };

    //testing exception
    if (demo == "1"){

        std::cout << "{ \"results\": {";
        for (int i = 0; i < count; ++i) {
            std::cout << "\"result" << i << "\": {";
            std::cout << "\"title\": \"Placeholder Title " << (i+1) << "\",";
            std::cout << "\"link\": \"https://example.com/item" << (i+1) << "\",";
            std::cout << "\"description\": \"Placeholder description for item " << (i+1) << "\"";
            std::cout << "}";
            if (i + 1 < count) std::cout << ",";
        }
        std::cout << "} }";
        return 0;
    }

    std::cout << "{ \"results\": {";
    for (int i = 0; i < result.size(); ++i) {
        std::cout << "\"result" << i << "\": {";
        std::cout << "\"title\": \"" << escape_json(result[i].title) << "\",";
        std::cout << "\"link\": \"" << escape_json(result[i].link) << "\",";
        std::cout << "\"description\": \"" << escape_json(result[i].description) << "\"";
        std::cout << "}";
        if (i +1 < result.size()) std::cout << ",";
    }
    std::cout << "} }";
    return 0;
}

int search(std::string* query, std::vector<SearchResult>& results, int count) {
    std::vector<std::string> stopWords = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"};
    //seperate query into an array of words
    std::vector<std::string> terms;
    std::stringstream ss(*query);
    std::string word;
    while (ss >> word) {
        // Remove punctuation
        word.erase(std::remove_if(word.begin(), word.end(), ::ispunct), word.end());
        // lowercase
        std::transform(word.begin(), word.end(), word.begin(),
                   [](unsigned char c){ return std::tolower(c); });

        if (!word.empty() && std::find(stopWords.begin(), stopWords.end(), word) == stopWords.end()) {
            terms.push_back(word);
        }
    }

    // Stem the terms
    for (auto& term : terms) {
        //term = stem(term);
        //disable stem for now
        term = term;
    }


    try {
        pqxx::connection C("dbname=SearchEngine user=postgres password=1234 hostaddr=127.0.0.1 port=5432");
        if (C.is_open()) {
            //std::cout << "Opened database successfully: " << C.dbname() << std::endl;
        } else {
            std::cerr << "Can't open database" << std::endl;
            return 1;
        }

        pqxx::work W(C);
        std::stringstream sqlStream;

        // --- Build word list ---
        std::stringstream wordList;
        for (size_t i = 0; i < terms.size(); ++i) {
            if (i > 0) wordList << ", ";
            wordList << "'" << terms[i] << "'";
        }

        // --- Main SQL ---
        sqlStream << R"(
        WITH query_words AS (
            SELECT UNNEST(ARRAY[
        )" << wordList.str() << R"(
            ]) AS word
        ),

        total_docs AS (
            SELECT COUNT(DISTINCT "LinkID") AS N
            FROM public."InvertedIndex"
        ),

        doc_freq AS (
            SELECT 
                ii."Word",
                COUNT(DISTINCT ii."LinkID") AS df
            FROM public."InvertedIndex" ii
            JOIN query_words qw
                ON ii."Word" = qw.word
            GROUP BY ii."Word"
        ),

        bm25_scores AS (
            SELECT
                ii."LinkID",
                ii."Word",
                ii."Frequency",
                df.df,
                td.N,

                LN(td.N::real / df.df) *
                (ii."Frequency"::real / (ii."Frequency" + 1.2)) AS bm25_term

            FROM public."InvertedIndex" ii
            JOIN query_words qw
                ON ii."Word" = qw.word
            JOIN doc_freq df
                ON ii."Word" = df."Word"
            CROSS JOIN total_docs td
        ),

        aggregated AS (
            SELECT
                "LinkID",
                SUM(bm25_term) AS text_score
            FROM bm25_scores
            GROUP BY "LinkID"
        ),

        -- NEW: compute per-word matches in title/description
        field_matches AS (
            SELECT
                a."LinkID",
                qw.word,

                CASE 
                    WHEN sli."Title" ILIKE '%' || qw.word || '%' THEN 1 
                    ELSE 0 
                END AS title_match,

                CASE 
                    WHEN sli."Description" ILIKE '%' || qw.word || '%' THEN 1 
                    ELSE 0 
                END AS desc_match

            FROM aggregated a
            JOIN public."SearchedLinkInfo" sli
                ON a."LinkID" = sli."LinkID"
            CROSS JOIN query_words qw
        ),

        -- NEW: aggregate matches per document
        field_scores AS (
            SELECT
                "LinkID",
                SUM(title_match) AS title_matches,
                SUM(desc_match) AS desc_matches
            FROM field_matches
            GROUP BY "LinkID"
        )

        SELECT
            l."Link",
            sli."Title",
            sli."Description",
            a.text_score,
            COALESCE(lw."Weight Score", 0) AS weight_score,

            -- FINAL SCORE WITH CAPS
            (
                a.text_score
                + LEAST(3.0 * COALESCE(fs.title_matches, 0), 8.0)
                + LEAST(0.7 * COALESCE(fs.desc_matches, 0), 3.0)
            )
            * (1 + 0.3 * COALESCE(lw."Weight Score", 0)) AS final_score

        FROM aggregated a

        LEFT JOIN field_scores fs
            ON a."LinkID" = fs."LinkID"

        LEFT JOIN public."Links" l
            ON a."LinkID" = l."ID"
        LEFT JOIN public."LinkWeight" lw
            ON a."LinkID" = lw."ID"
        LEFT JOIN public."SearchedLinkInfo" sli
            ON a."LinkID" = sli."LinkID"

        ORDER BY final_score DESC
        LIMIT )" << count << ";";

        // --- Execute ---
        std::string sql = sqlStream.str();
        pqxx::result R = W.exec(sql);

        for (auto row : R) {
            SearchResult r;

            // Column 0: Link (guaranteed NOT NULL due to WHERE clause)
            r.link = row[0].c_str();

            // Column 1: title
            if (row[1].is_null() || std::string(row[1].c_str()).empty()) {
                r.title = r.link; // fallback
            } else {
                r.title = row[1].c_str();
            }

            // Column 2: description
            if (row[2].is_null()) {
                r.description = "";
            } else {
                r.description = row[2].c_str();
            }

            results.push_back(r);
        }

        W.commit();
    } catch (const std::exception &e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }

   
    return 0;
}


std::string stem(std::string word) {
    size_t len = word.size();
    if (len < 3) return word;

    // Remove plural 's'
    if (word.back() == 's') {
        if (len > 1 && word[len-2] != 's' && word[len-2] != 'u' && word[len-2] != 'i') {
            word.pop_back();
            len--;
        }
    }

    // Remove 'ed' or 'ing'
    if (len > 2) {
        std::string suffix = word.substr(len-2);
        if (suffix == "ed" || suffix == "ing") {
            bool has_vowel = false;
            for (size_t i = 0; i < len-2; ++i) {
                char c = word[i];
                if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
                    has_vowel = true;
                    break;
                }
            }
            if (has_vowel) {
                word = word.substr(0, len-2);
                len -= 2;
            }
        }
    }

    // Remove 'er' or 'est'
    if (len > 2) {
        std::string suffix = word.substr(len-2);
        if (suffix == "er" || suffix == "est") {
            word = word.substr(0, len-2);
        }
    }

    return word;
}
