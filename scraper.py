import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


<<<<<<< HEAD
def scraper(url, resp):
    #print("hello")
    #count = 0
    links = extract_next_links(url, resp)
    #for link in links:
        #print(is_valid(link))
        #print(url)
        #if (is_valid(link)):
            #count = count + 1
        #print(link)
        #print(is_valid(link))
    #print("Number of valid links: ", count)
=======
def scraper(url, resp, word_count):
    links = extract_next_links(url, resp, word_count)
>>>>>>> b29254594c8ffd23a0da7652453655396a1c4a27
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp, word_count):
    #html_page = urllib.urlopen(resp.url)
<<<<<<< HEAD
    print("URL----------------------------")
    print(url)
    links = []
    if resp.raw_response != None:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
=======
    print(f'---------URL: {url}---------')
    #soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    links = []

    if resp.raw_response != None:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        text = soup.get_text()
        text = text.strip().split()
        print()
        print(f'{url}~~~~~~~~~~~~~~~~~~~~~~ word count: {len(text)}')
        print()
        word_count[len(text)] = url
        # word_count += len(text)
>>>>>>> b29254594c8ffd23a0da7652453655396a1c4a27
        for link in soup.findAll('a'):
            links.append(link.get('href'))

    #for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
        #links.append(link.get('href'))

    print(f'links: {links}')
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    #print(resp.raw_response.content)
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.  
    parsed = urlparse(url) 
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        valid_domains = parsed.netloc.split('.', 1)
        if len(valid_domains) >= 2:
            if valid_domains[1] not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
                return False

        #return not re.match(
            #r".*\.(stat.uci.edu|ics.uci.edu|cs.uci.edu|informatics.uci.edu)$", parsed.netloc)
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
