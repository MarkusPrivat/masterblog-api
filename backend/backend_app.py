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
    if not len(data) == 2:
        return False, "Incorrect number of data in .JSON!"
    if 'title' not in data:
        return False, "'title' not in .JSON!"
    if 'content' not in data:
        return False, "'content' not in .JSON!"
    return True, "Done!"


def fetch_post_by_id(id) -> tuple[bool, dict]:
    for post in POSTS:
        if post['id'] == id:
            return True, post
    return False, {'error': f"No post with ID: '{id}'"}


def get_new_id() -> int:
    return max(post['id'] for post in POSTS) + 1


def search_post_by_title_or_content(title: str, content: str) -> list[dict]:
    result = [{}]
    for post in POSTS:
        if title.lower() in post['title'].lower() and title:
            result.append(post)
            continue
        if content.lower() in post['content'].lower() and content:
            result.append(post)
    return result


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
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


@app.route('/api/posts/<int:id>', methods=['DELETE', 'PUT'])
def delete_post(id):
    is_executed, post = fetch_post_by_id(id)
    if not is_executed:
        return jsonify(post), 404

    if request.method == 'DELETE':
        POSTS.remove(post)
        return jsonify({'message': f"Post with ID: '{id}' has been deleted successfully"}), 200

    # method PUT
    for post_to_edit in POSTS:
        if post_to_edit['id'] == id:
            new_post = request.get_json()
            is_executed, msg = validate_blog_post(new_post)
            if not is_executed:
                return jsonify({'error': f"Invalid blog post: {msg}"}), 400
            post_to_edit.update(new_post)
            return jsonify(post_to_edit), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title = request.args.get('title', '')
    content = request.args.get('content', '')
    result = search_post_by_title_or_content(title, content)
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
