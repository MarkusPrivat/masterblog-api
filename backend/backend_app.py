from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def validate_blog_post(data) -> tuple[bool, str]:
    if not len(data) == 2:
        return False, "Incorrect number of data in .JSON!"
    if 'title' not in data:
        return False, "'title' not in .JSON!"
    if 'content' not in data:
        return False, "'content' not in .JSON!"
    return True, "Done!"


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'GET':
        return jsonify(POSTS)

    # method = POST
    new_post = request.get_json()
    is_executed, msg = validate_blog_post(new_post)
    if not is_executed:
        return jsonify({'error': f"Invalid blog post: {msg}"}), 400

    new_id = max(post['id'] for post in POSTS) + 1
    new_post['id'] = new_id

    POSTS.append(new_post)
    return jsonify(new_post), 201



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
