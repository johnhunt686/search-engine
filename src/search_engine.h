#ifndef SEARCH_ENGINE_H
#define SEARCH_ENGINE_H
#pragma once

#include <string>
#include <vector>
#include <iostream>
#include <pqxx/pqxx>
#include <algorithm>
#include <cctype>
#include <sstream>
#include <libstemmer.h>

struct SearchResult {
    std::string link;
    std::string title;
    std::string description;
};

int search(std::string* query, std::vector<SearchResult>& results , int count);

std::string stem(std::string word);

#endif // SEARCH_ENGINE_H
