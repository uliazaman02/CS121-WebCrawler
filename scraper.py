import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from difflib import SequenceMatcher

prev_page_text = ''
prev_url = ''


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
        text_list = text.strip().split()
        # count total (non-stop) words
        count = 0
        
        # TRAP DETECTION ~~~~~~~~~~~~~~~~~~~~~~~~~~~

        global prev_page_text
        global prev_url
        # if this isn't the first page being checked
        if len(prev_page_text) > 0:
            # check if webpage content is too similar to that of previous webpage
            sm = SequenceMatcher(a=text, b=prev_page_text)
            similarityAB = sm.ratio()
        
            threshold = 0.9
            # if the pages are more than 90% similar
            if similarityAB >= threshold:
                # TODO: something else here????? or does just leaving the function work?
                print(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DUPLICATE DETECTED!!!!!')
                print()
                print(f'prev: {prev_url}')
                print(f'current: {url}')
                print()
                return []
            
        # this is the new prev_page_text
        prev_page_text = text
        # this is the new prev_url
        prev_url = url
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # detect and avoid large files
        '''
        p = re.compile(r'^(\d+) bytes$')
        el = soup.findAll()
        # print(f'el: {el}')
        file_size = len(el)
        print(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~file size: {file_size}')
        # threshold of what is too large to bother crawling:
        too_large = 15000000
        if file_size > too_large:
            print(f'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~TOO LARGE: {url}')
            return
        '''
        
        # turn words into lowercase and add them to the word_frequency dictionary to count if not a stopword
        for word in text_list:
            word = word.lower()
            # only consider words that are alphabetical and is not a stopword
            alphabetical_regex = re.compile("[a-zA-Z]+")
            valid_words = re.findall(alphabetical_regex, word)
            for word in valid_words:
                if word not in stops:
                    word_frequency[word] += 1
                    # count word for word_count dict/finding longest page
                    count += 1
                
        print()
        print(f'{url}~~~~~~~~~~~~~~~~~~~~~~ word count: {len(text_list)}')
        print()

        # add page stats to word_count dict
        word_count[count] = url

        # uses beatiful soup to extract the urls and put them in a list
        for link in soup.findAll('a'):
            links.append(link.get('href'))
        
        # status code 3xx means redirect, find new URL and add to links to explore
        if 300 <= resp.status < 400:
            new_link = resp.raw_response.headers.get("Location")
            print("new redirected link:")
            print(new_link)
            if new_link != None:
                links.append(new_link)

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
