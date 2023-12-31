from api import bidirectional_search, visualize_graph
from flask import Flask, render_template, request
import os  # Import the os module

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    result = None  # Initialize the result variable
    error = False  # Initialize the error variable
    graph_data = ''  # Initialize the graph_data variable

    if request.method == 'POST':
        start_article = request.form['start_article']
        end_article = request.form['end_article']
        adj_nodes = request.form['adj_nodes']

        result = bidirectional_search(start_article, end_article)

        if result is not None:
            path, length, counter, direction, connection_point = result
            graph_data = visualize_graph(
                start_article, end_article, path, connection_point, adj_nodes)
            error = False
        else:
            error = True  # Set the error to True when no result is found

    return render_template('index.html', result=result, graph_data=graph_data, error=error)


if __name__ == '__main__':
    # Get the PORT environment variable (provided by Render) and fall back to 5000 if it doesn't exist.
    port = int(os.environ.get("PORT", 5000))
    # Run the app with the specified host and port
    app.run(host='0.0.0.0', port=port)
