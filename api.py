import requests
import time

session = requests.Session()
URL = "https://en.wikipedia.org/w/api.php"
EXCLUDE_PREFIXES = (
    "Wikipedia:", "Template:", "Category:", "Category talk:", "File:", "File talk:", "Draft talk:", "Help:", "Special:", "Portal:", "Talk:", "Module:", "Template talk:", "User:", "User talk:", "Draft:", "Wikipedia talk:"
)


def get_forward_links(page_name):

    params = {
        "action": "query",
        "format": "json",
        "titles": page_name,
        "prop": "links",
        "pllimit": "max"  # Get as many links as allowed per request
    }

    links = set()

    while True:
        # Respect rate limits
        time.sleep(1)

        response = session.get(url=URL, params=params)
        data = response.json()

        # Extract links from response
        pages = data["query"]["pages"]
        for page in pages.values():
            if "links" in page:
                for l in page["links"]:
                    title = l["title"]
                    if not title.startswith(EXCLUDE_PREFIXES):
                        links.add(title)

        if "continue" in data:
            # Update the 'continue' parameter for the next request
            params.update(data["continue"])
        else:
            break

    return links


def get_backward_links(page_name):

    params = {
        "action": "query",
        "format": "json",
        "titles": page_name,
        "prop": "linkshere",
        "lhlimit": "max"  # Get as many links as allowed per request
    }

    links = set()
    
    while True:
        # Respect rate limits
        time.sleep(1)

        response = session.get(url=URL, params=params)
        data = response.json()

        # Extract links from response
        pages = data["query"]["pages"]
        for page in pages.values():
            if "linkshere" in page:
                for l in page["linkshere"]:
                    title = l["title"]
                    if not title.startswith(EXCLUDE_PREFIXES):
                        links.add(title)

        if "continue" in data:
            # Update the 'continue' parameter for the next request
            params.update(data["continue"])
        else:
            break

    return links
