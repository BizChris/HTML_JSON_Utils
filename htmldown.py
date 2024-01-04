import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import time

def download_html(url, depth, filepath):
    start_time = time.time()  # Set the start time when the function is called
    urls = [url]
    domain = urlparse(url).netloc
    downloaded_urls = set()  # Set to store already downloaded URLs

    with ThreadPoolExecutor() as executor:
        for i in range(depth):
            new_urls = []
            futures = []

            for url in urls:
                futures.append(executor.submit(download_and_parse, url, domain, filepath, new_urls, downloaded_urls))

            # Wait for all tasks to complete
            for future in futures:
                future.result()

            # Update the list of URLs with the newly found URLs
            urls = new_urls

    print(f"Processed {len(downloaded_urls)} files in {time.time() - start_time} seconds")
import json

# Create a dictionary to store skipped URLs
skipped_urls = {}

def download_and_parse(url, domain, filepath, new_urls, downloaded_urls):
    # Parse the URL and remove the query parameters
    parsed_url = urlparse(url)
    url_without_query = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

    try:
        if url_without_query in downloaded_urls:
            return  # Skip if URL has already been downloaded

        response = requests.get(url)
        if response.status_code == 404:
            print(f"Skipping URL: {url} due to 404 error")
            skipped_urls[url] = "404 error"
            return
        response.raise_for_status()
        html_content = response.text

        # Save the HTML content to a local file
        filename = os.path.join(filepath, f'{url_without_query.replace("http://", "").replace("https://", "").replace("/", "_")}.html')
        with open(filename, 'w') as file:
            file.write(html_content)

        # Add the downloaded URL to the set of downloaded URLs
        downloaded_urls.add(url_without_query)

        # Parse the HTML content
        content_type = response.headers['Content-Type'].lower()
        if 'html' in content_type:
            soup = BeautifulSoup(html_content, 'html.parser')
        elif 'xml' in content_type:
            soup = BeautifulSoup(html_content, 'lxml')
        else:
            print(f"Skipping URL: {url} due to unknown content type: {content_type}")
            skipped_urls[url] = f"Unknown content type: {content_type}"
            return

        # Find all the URLs in the HTML file and add them to the new_urls list
        for link in soup.find_all('a'):
            new_url = link.get('href')
            if new_url:
                # Resolve relative URLs
                new_url = urljoin(url, new_url)
                if new_url.startswith(('http://', 'https://')):
                    if new_url.startswith(f"https://{domain}") or new_url.startswith(f"http://{domain}"):
                        new_urls.append(new_url)

        # Add a 1 second delay to avoid websites blocking requests
        time.sleep(2)

    except requests.exceptions.SSLError:
        print(f"Skipping URL: {url} due to SSL certificate failure")
        skipped_urls[url] = "SSL certificate failure"

# Write the skipped URLs to a JSON file
with open('skipped_urls.json', 'w') as file:
    json.dump(skipped_urls, file)

# Usage:
# download_html('https://developer.harness.io/docs/', 5, '/Users/christopherdickson/Downloads/harness')