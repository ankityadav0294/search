# IITG WEB CRAWLER

### Installations:

Python 2.7 packages needed:
    
- Scrapy

    ```sh
    $ pip install --proxy="http://username:password@202.141.80.22:3128" scrapy
    ```
    
- Whoosh

    ```sh
    $ pip install --proxy="http://username:password@202.141.80.22:3128" whoosh
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



    


