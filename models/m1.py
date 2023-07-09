from models.api import get_forward_links, get_backward_links
from collections import deque
import time


def bidirectional_search(start_article, end_article):
    start_time = time.time()
    start_queue = deque([(start_article, [start_article])])
    end_queue = deque([(end_article, [end_article])])
    start_visited = {start_article: [start_article]}
    end_visited = {end_article: [end_article]}
    counter = 2 # Include starting and ending article

    while start_queue and end_queue:
        start_article, start_path = start_queue.popleft()
        start_links = get_forward_links(start_article)

        for link in start_links:
            new_path = start_path + [link]

            if link not in start_visited or len(new_path) < len(start_visited[link]):
                counter += 1
                start_queue.append((link, new_path))
                start_visited[link] = new_path

                if link in end_visited:
                    end_path = end_visited[link]
                    end_time = time.time()
                    print(end_time - start_time)
                    return (start_path + end_path, len(start_path + end_path), counter)

        end_article, end_path = end_queue.popleft()
        end_links = get_backward_links(end_article)

        for link in end_links:
            new_path = [link] + end_path

            if link not in end_visited or len(new_path) < len(end_visited[link]):
                counter += 1
                end_queue.append((link, new_path))
                end_visited[link] = new_path

                if link in start_visited:
                    start_path = start_visited[link]
                    end_time = time.time()
                    print(end_time - start_time)
                    return (start_path + end_path, len(start_path + end_path), counter)

    return None


start_article = "United States Post Office and Federal Courthouse-Colorado Springs Main"
end_article = "1974 attack on the Japanese Embassy in Kuwait"
result = bidirectional_search(start_article, end_article)
print(result)