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



    


