from models.api import get_forward_links, get_backward_links
from collections import deque
import time
import random

from pyvis.network import Network


def visualize_graph(start_article, end_article, path, connection_point):
    net = Network(notebook=True)
    net.force_atlas_2based()
    connection_index = path.index(connection_point)

    # Add main path nodes first
    for i in range(len(path)):
        node = path[i]
        color = 'green' if node == connection_point else 'blue' if i <= connection_index else 'red'
        net.add_node(node, color=color, title=node)

    # Add main path edges second
    for i in range(len(path) - 1):
        source = path[i]
        target = path[i + 1]
        edge_color = 'blue' if i < connection_index else 'red'
        net.add_edge(source, target, color=edge_color)

    # Add alternative paths
    for i in range(len(path)):
        if path[i] == connection_point:
            continue
        elif i < connection_index:  # Forward links
            links = get_forward_links(path[i])
        else:  # Backward links
            links = get_backward_links(path[i])

        # Randomly select up to 50 links
        links_to_add = random.sample(list(links), min(50, len(links)))
        for link in links_to_add:
            net.add_node(link, title=link)
            # Use a different color for alternative paths
            net.add_edge(path[i], link, color='grey')

    net.show("graph.html")


def bidirectional_search(start_article, end_article):
    start_time = time.time()
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
                    end_time = time.time()
                    print(end_time - start_time)
                    print(link)
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
                    end_time = time.time()
                    print(end_time - start_time)
                    print(link)
                    return (start_path + end_path, len(start_path + end_path), counter, "start_visited", link)

    return None


start_article = "Rostki, Pisz County"
end_article = "Ryne Duren"
result = bidirectional_search(start_article, end_article)
print(result)


if result is not None:
    path, length, counter, direction, connection_point = result
    visualize_graph(start_article, end_article, path, connection_point)
else:
    print("No path found between the articles.")
