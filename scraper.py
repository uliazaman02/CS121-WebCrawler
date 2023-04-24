import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests


def scraper(url, resp, word_count, word_frequency, stops):
    links = extract_next_links(url, resp, word_count, word_frequency, stops)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp, word_count, word_frequency, stops):
    print(f'---------URL: {url}---------')
    links = []

    # checks if page has 200 status code (OK) and there is content, so we can crawl the page
    if resp.status == 200 and resp.raw_response != None:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        # get the text on the webpage
        text = soup.get_text()
        # get list of text
        text = text.strip().split()
        # count total (non-stop) words
        count = 0
        
        # print("THIS IS TEXT")
        # print(text)
        for word in text:
            if word not in stops:
                word_frequency[word] += 1
                # count word for word_count dict/finding longest page
                count += 1
                
        print()
        print(f'{url}~~~~~~~~~~~~~~~~~~~~~~ word count: {len(text)}')
        print()
        
        # add page stats to word_count dict
        word_count[count] = url

        # uses beatiful soup to extract the urls and put them in a list
        for link in soup.findAll('a'):
            links.append(link.get('href'))

    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.  
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        #split the netloc to only get the domain
        valid_domains = parsed.netloc.split('.', 1)

        # checks if the url is from one of the four domains
        if len(valid_domains) >= 2:
            if valid_domains[1] not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
                return False

        # detect large files
        res = requests.head(url)

        # TRAP DETECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # check if webpage content is too similar
        fingerprintA = 0 # prev page?
        fingerprintB = 0 # this page
        similarityAB = 0 # algo here (he hasn't published the slides yet lol)
        # TODO: decide threshold
        threshold = 1
        if similarityAB >= threshold:
            return False
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        # checks for invalid file types in the url
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|jpeg|jpg|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|ps|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
