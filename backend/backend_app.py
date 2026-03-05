from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]
SORT_OPTIONS = ['title', 'content']
DIRECTION_OPTION = ['asc', 'desc']


def validate_blog_post(data) -> tuple[bool, str]:
    """
    Validates the structure of a blog post dictionary.

    Checks if the mandatory keys 'title' and 'content' are present and
    ensures no unexpected extra fields are included in the data.

    Args:
        data (dict): The dictionary to be validated, typically from a JSON request.

    Returns:
        tuple: A pair containing:
            - bool: True if the structure is valid, False otherwise.
            - str: "Done!" on success, or a specific error message explaining
                   the validation failure.
    """
    required_keys = {'title', 'content'}
    if not required_keys.issubset(data.keys()):
        missing = required_keys - data.keys()
        return False, f"Missing keys: {', '.join(missing)}"
    if len(data) > len(required_keys):
        return False, "Too many fields in JSON!"
    return True, "Done!"


def fetch_post_by_id(post_id) -> tuple[bool, dict]:
    """
    Searches for a blog post by its unique ID in the global list.

    Args:
        post_id (int): The ID of the post to retrieve.

    Returns:
        tuple: A pair containing:
            - bool: True if the post was found, False otherwise.
            - dict: The post data on success, or an error dictionary
                   {'error': message} if the post does not exist.
    """
    for post in POSTS:
        if post['id'] == post_id:
            return True, post
    return False, {'error': f"No post with ID: '{post_id}'"}


def get_new_id() -> int:
    """
    Generates a new unique identifier for a blog post.

    Finds the highest existing ID in the POSTS list and increments it by 1.
    If the list is empty, it starts the ID sequence at 1.

    Returns:
        int: The next available unique ID.
    """
    if not POSTS:
        return 1
    return max(post['id'] for post in POSTS) + 1


def search_post_by_title_or_content(title: str, content: str) -> list[dict]:
    """
    Filters blog posts by title, content, or both.

    The search is case-insensitive and performs a partial match. If a post
    matches either the title or the content criteria, it is included in the
    result list.

    Args:
        title (str): The search string for the title.
        content (str): The search string for the post content.

    Returns:
        list[dict]: A list of matching post dictionaries. Empty list if no match.
    """
    result = []
    for post in POSTS:
        if ((title.lower() in post['title'].lower() and title) or
                (content.lower() in post['content'].lower() and content)):
            result.append(post)
    return result


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """
    Handles retrieval and creation of blog posts via the API.

    GET:
        Returns a JSON list of all posts. Supports optional sorting via
        query parameters.
        Params:
            - sort (str): The field to sort by (e.g., 'title', 'content').
            - direction (str): 'asc' (default) or 'desc'.
        Returns: 200 OK with list of posts, or 400 Bad Request on invalid params.

    POST:
        Creates a new blog post. Validates the incoming JSON data and
        assigns a new unique ID.
        Payload: JSON object with 'title' and 'content'.
        Returns: 201 Created with the new post, or 400 Bad Request on validation failure.
    """
    if request.method == 'GET':
        sort_key = request.args.get('sort')
        direction = request.args.get('direction', 'asc').lower()

        if not sort_key:
            return jsonify(POSTS)

        if sort_key not in SORT_OPTIONS:
            return jsonify(f"Invalid 'sort' parameter. Options: {SORT_OPTIONS}"), 400
        if direction not in DIRECTION_OPTION:
            return jsonify(f"Invalid 'direction' parameter. Options: {DIRECTION_OPTION}"), 400

        is_reverse = (direction == 'desc')
        sorted_posts = sorted(
            POSTS,
            key=lambda x: str(x.get(sort_key, '')).lower(),
            reverse=is_reverse)
        return jsonify(sorted_posts)

    # method = POST
    new_post = request.get_json()
    is_executed, msg = validate_blog_post(new_post)
    if not is_executed:
        return jsonify({'error': f"Invalid blog post: {msg}"}), 400

    new_post['id'] = get_new_id()

    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE', 'PUT'])
def delete_post(post_id):
    """
    Manages individual blog posts by their ID.

    Common:
        First, attempts to retrieve the post by the given ID.
        Returns 404 if the post does not exist.

    DELETE:
        Removes the specified post from the global list.
        Returns: 200 OK with a success message.

    PUT:
        Updates an existing post with new JSON data.
        Validates the payload before applying changes.
        Returns: 200 OK with the updated post, or 400 Bad Request if validation fails.
    """
    is_executed, post = fetch_post_by_id(post_id)
    if not is_executed:
        return jsonify(post), 404

    if request.method == 'DELETE':
        POSTS.remove(post)
        return jsonify({'message': f"Post with ID: '{post_id}' has been deleted successfully"}), 200

    # method PUT
    new_data = request.get_json()
    is_valid, msg = validate_blog_post(new_data)
    if not is_valid:
        return jsonify({'error': msg}), 400

    post.update(new_data)
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    """
    Search for blog posts based on title and/or content.

    Query Parameters:
        - title (str): Partial string to match against post titles.
        - content (str): Partial string to match against post content.

    Returns:
        - 200 OK: A JSON list of posts that match at least one of the criteria.
                  Returns an empty list if no matches are found.
    """
    title = request.args.get('title', '')
    content = request.args.get('content', '')
    result = search_post_by_title_or_content(title, content)
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
