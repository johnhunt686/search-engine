Install BeautifulSoup4:
py -m pip install beautifulsoup4

Install Selenium:
pip install -U selenium

Installing NLTK Package

Terminal
- pip install nltk
- python -m nltk.downloader popular

Website for help: https://www.nltk.org/install.html


Installing Database Stuff (This is a Local Database right now. Will make online later probably)

Do in order or it might not work

Install PostgreSQL
- https://www.postgresql.org/download/
- Run the .exe
- Make database password: 1234 and port: 41204
- It should download and run Stack Builder
- In Stack Builder install:
	Database Drivers: psqlODBC (64 bit) v13.02.0000-1
	Database Server: v18.3-2 (Should already be installed)

Install pgAdmin4 (This should automatically come with PostgreSQL so you shouldn't have to do this)
- https://www.pgadmin.org/download/ (Choose Windows unless you are John)
- Open this probably. You can test connection to your database.

Terminal
- pip install psycopg2

You might have to change your python interpreter in vscode to make it actually work.
- In the vscode terminal type (pip show nltk) and (pip show psycopg2)
- This will show you what python version they are installed on.
- In the bottom right of VSCode there is a version number. Make sure the same as above.
- If not click on it and change it to the right one.
