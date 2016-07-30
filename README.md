# IITG WEB CRAWLER

### Installations:

Python 2.7 packages needed:
    
- Scrapy

    ```sh
    $ pip install scrapy
    ```
    
- Whoosh

    ```sh
    $ pip install whoosh
    ```

- Django

    ```sh
    $ pip install django
    ```
    
### Deploy Crawler:

- Crawl and Index:

    ```sh
    $ scrapy crawl 4spider 
    ```

- Crawl, index and show scrapped data in **scrapped.json** file:

    ```sh
    $ scrapy crawl 4spider -o scrapped.json
    ```
    ***INFO:*** Delete the scrapped.json file present in directory.

### Use Search Engine:

1. Go to gui subdirectory in spiderman directory.

2. Deploy the virtual Server on 127.0.0.1:8000

    ```sh
    $ python manage.py runserver
    ```
    ***INFO:*** Remember to switch off the server using Ctrl+D.


    


