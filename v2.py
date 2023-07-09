import time
import random
import requests
from collections import deque
from pyvis.network import Network

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


def visualize_graph(start_article, end_article, path, connection_point, adj_nodes):
    if not adj_nodes:
        adj_nodes = 10  # or some default value
    else:
        adj_nodes = int(adj_nodes)

    net = Network(notebook=True, directed=True)
    net.force_atlas_2based()
    connection_index = path.index(connection_point)

    # Add main path nodes first
    for i in range(len(path)):
        node = path[i]
        color = 'green' if node == connection_point else 'blue' if i <= connection_index else 'red'
        net.add_node(node, color=color, title=node)

    added_edges = set()  # To track the edges we've already added.

    # Add main path edges second
    for i in range(len(path) - 1):
        source = path[i]
        target = path[i + 1]
        edge_color = 'blue' if i < connection_index else 'red'
        net.add_edge(source, target, color=edge_color)
        added_edges.add((source, target))

    # Add alternative paths
    for i in range(len(path)):
        if path[i] == connection_point:
            continue
        elif i < connection_index:  # Forward links
            links = get_forward_links(path[i])
        else:  # Backward links
            links = get_backward_links(path[i])

        # Randomly select up to 50 links
        links_to_add = random.sample(list(links), min(adj_nodes, len(links)))
        for link in links_to_add:
            net.add_node(link, title=link)
            # Use a different color for alternative paths
            # Reverse the direction for the nodes that use get_backward_links
            if i < connection_index:
                # Only add the edge if it's not already added.
                if (path[i], link) not in added_edges:
                    net.add_edge(path[i], link, color='grey')
                    added_edges.add((path[i], link))
            else:
                # Only add the edge if it's not already added.
                if (link, path[i]) not in added_edges:
                    net.add_edge(link, path[i], color='grey')
                    added_edges.add((link, path[i]))

    net.show("graph.html")
    with open("graph.html", "r") as f:
        html_content = f.read()

    return html_content



def bidirectional_search(start_article, end_article):

    if not (get_forward_links(start_article) and get_backward_links(end_article)):
        print("error")
        return None
    
    start_queue = deque([(start_article, [start_article])])
    end_queue = deque([(end_article, [end_article])])
    start_visited = {start_article}
    end_visited = {end_article}
    start_paths = {start_article: [start_article]}
    end_paths = {end_article: [end_article]}
    counter = 2  # Include starting and ending article

    while start_queue and end_queue:
        start_article, start_path = start_queue.popleft()
        start_links = get_forward_links(start_article)

        for link in start_links:
            if link not in start_visited:
                new_path = start_path + [link]
                counter += 1
                start_queue.append((link, new_path))
                start_visited.add(link)
                start_paths[link] = new_path

                if link in end_visited:
                    end_path = end_paths[link]
                    return (start_path + end_path, len(start_path + end_path), counter, "end_visited", link)

        end_article, end_path = end_queue.popleft()
        end_links = get_backward_links(end_article)

        for link in end_links:
            if link not in end_visited:
                new_path = [link] + end_path
                counter += 1
                end_queue.append((link, new_path))
                end_visited.add(link)
                end_paths[link] = new_path

                if link in start_visited:
                    start_path = start_paths[link]
                    return (start_path + end_path, len(start_path + end_path), counter, "start_visited", link)

    return None