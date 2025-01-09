from langchain.document_loaders import WebBaseLoader
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# scrap websites, if website doesn't have blockers
class WebsiteScraper:
   def __init__(self, base_url):
       self.base_url = base_url
       self.found_urls = set()
       self.docs = []

   def get_links(self, url):
       response = requests.get(url)
       soup = BeautifulSoup(response.text, 'html.parser')
       return [urljoin(self.base_url, link.get('href'))
               for link in soup.find_all('a')
               if link.get('href') and self.base_url in urljoin(self.base_url, link.get('href'))]

   def crawl(self):
       urls = set([self.base_url])
       while urls:
           url = urls.pop()
           if url not in self.found_urls:
               self.found_urls.add(url)
               new_urls = self.get_links(url)
               urls.update(set(new_urls) - self.found_urls)
       return self

   def load(self):
       loader = WebBaseLoader(list(self.found_urls))
       self.docs = loader.load()
       return self.docs

   @property
   def urls(self):
       return list(self.found_urls)

# Usage
scraper = WebsiteScraper("https://docs.dolosdiary.com")
docs = scraper.crawl().load()