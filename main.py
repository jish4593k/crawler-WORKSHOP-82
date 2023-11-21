import requests
from bs4 import BeautifulSoup
import re  # Import the regular expression module


class CraigslistScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_html(self, url):
        # Make a GET request to the provided URL and return the HTML content
        response = requests.get(url)
        return response.text

    def extract_house_data(self, house):
        # Extract relevant information for each house listing
        info = {}
        info['href'] = 'https://sfbay.craigslist.org' + house.find('a')['href']
        info['description'] = house.find('span', {'id': 'titletextonly'}).get_text(strip=True)
        info['price'] = house.find('span', class_='price').get_text(strip=True)
        house_info = house.find('span', class_='housing').get_text(strip=True, separator=' ')
        try:
            info['bedroom'] = re.search(r'(\d+)br', house_info).group(1)
            price_int = int(info['price'][1:])
            bedroom_int = int(info['bedroom'])
            average_price = price_int * 1.0 / bedroom_int
            info['averagePrice'] = price_int if average_price < 1000 else average_price
        except AttributeError:
            info['bedroom'] = ""
            info['averagePrice'] = ""
        try:
            info['size'] = re.search(r'(\d+ft)', house_info).group(1)
        except AttributeError:
            info['size'] = ""
        info['location'] = house.find('small').get_text(strip=True)
        return info

    def scrape_page(self, page_url):
        # Scrape information from a single page of house listings
        html = self.get_html(page_url)
        soup = BeautifulSoup(html, 'html.parser')
        houses = soup.find_all('p', class_='row')
        return [self.extract_house_data(house) for house in houses]

    def save_info_to_file(self, house_info, filename):
        # Save housing information to a text file
        with open(filename, 'a') as f:
            for each in house_info:
                f.write(f'description: {each["description"]}\n')
                f.write(f'location: {each["location"]}\n')
                f.write(f'href: {each["href"]}\n')
                f.write(f'size: {each["size"]}\n')
                f.write(f'bedroom: {each["bedroom"]}\n')
                f.write(f'price: {each["price"]}\n')
                f.write(f'averagePrice: {each["averagePrice"]}\n')
                f.write('-----------------------------------------------------------\n')

    def save_average_price_to_file(self, house_info, filename):
        # Save average prices to a text file
        with open(filename, 'a') as f:
            for each in house_info:
                if each['averagePrice'] != "":
                    print(each['averagePrice'])
                    f.write(str(each['averagePrice']) + '\n')


if __name__ == '__main__':
    base_url = "https://sfbay.craigslist.org"
    query = "uc+berkeley"
    start_urls = [f"{base_url}/search/apa?query={query}&s={start}" for start in range(0, 300, 100)]

    # Initialize the scraper
    scraper = CraigslistScraper(base_url)
    house_info = []

    # Loop through each page URL and scrape information
    for url in start_urls:
        print(f"Processing {url}")
        page_info = scraper.scrape_page(url)
        house_info.extend(page_info)

    # Save scraped information to text files
    scraper.save_info_to_file(house_info, 'house_info.txt')
    scraper.save_average_price_to_file(house_info, 'average_price.txt')
