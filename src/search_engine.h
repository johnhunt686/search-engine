#ifndef SEARCH_ENGINE_H
#define SEARCH_ENGINE_H

#include <string>
#include <vector>

// Processes the query and fills the results vector with terms.
// Returns 0 on success or non-zero on error.
int search(std::string* query, std::vector<SearchResult>& results , int count){}

std::string stem(std::string word);

#endif // SEARCH_ENGINE_H
