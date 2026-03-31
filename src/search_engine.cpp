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
    std::string results;
    std::string setting2;
    std::string setting3;

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
        } else if(key == "setting1"){
            results = value;
        } else if(key == "setting2"){
            setting2 = value;
        } else if(key == "setting3"){
            setting3 = value;
        } else {
            return -1;
        }
    }
    std::vector<std::string> tmpResult;
    search(&query, tmpResult);

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

    std::cout << "{ \"results\": [";
    for (size_t i = 0; i < tmpResult.size(); ++i) {
        std::cout << "\"" << escape_json(tmpResult[i]) << "\"";
        if (i + 1 < tmpResult.size()) std::cout << ",";
    }
    std::cout << "] }";

    return 0;
}

int search(std::string* query, std::vector<std::string>& results){
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

    //query synonym engine

    //query common language removal

    //term simplification

    //query initial query TOP <results>
    /*
    select *
    from index
    left join links on (index.linkID = links.linkID)
    left join linkWeights on (links.linkID = linkWeights.linkID)
    WHERE <result> IN Index.term
    ORDER BY linkWeights.linkWeight DESC;
    */
    
    //TESTING DO NOT LEAVE
    results = terms;

   
    return 0;
}
