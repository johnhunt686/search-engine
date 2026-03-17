#include <string>
#include <vector>
#include <iostream>


int main(int argc, char* argv[])
{
    if (argc == 0){
        return -1;
    }
    
    //first argument is always the query
    std::string query;
    std::string setting1;
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
            setting1 = value;
        } else if(key == "setting2"){
            setting2 = value;
        } else if(key == "setting3"){
            setting3 = value;
        } else {
            return -1;
        }
    }

    std::cout << "{ \"query\": \"" << query 
            << "\", \"setting1\": \"" << setting1
            << "\", \"setting2\": \"" << setting2
            << "\", \"setting3\": \"" << setting3
            << "\", \"results\": [\"example result\"] }";

    return 0;
}

