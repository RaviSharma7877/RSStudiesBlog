# app.py

from flask import Flask, jsonify, g, request, render_template, send_from_directory
import os
from flask_pymongo import MongoClient
from bson import ObjectId, json_util
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb+srv://root:rootravi7877@cluster0.vwzslkb.mongodb.net/NovaNotions?retryWrites=true&w=majority')

ALLOWED_KEYS = ['title', 'desc', 'time', 'img', 'summary', 'KeyElements', 'Tips', 'Conclusion', 'Strategies']

def get_db():
    if 'db' not in g:
        g.db = MongoClient(app.config['MONGO_URI'])
    return g.db

class BlogPostManager:
    def __init__(self):
        self.db = MongoClient(app.config['MONGO_URI']).NovaNotions.BlogPosts

    def validate_keys(self, data):
        for key in data.keys():
            if key not in ALLOWED_KEYS:
                return False, f'Invalid key: {key}'
        return True, None

    def add_post(self, new_data):
        is_valid, error = self.validate_keys(new_data)
        if not is_valid:
            return False, error

        try:
            result = self.db.insert_one(new_data)
            return True, str(result.inserted_id)
        except Exception as e:
            return False, str(e)

    def get_all_posts(self):
        return list(self.db.find())

    def get_post_by_id(self, post_id):
        return self.db.find_one({'_id': ObjectId(post_id)})

    def update_post(self, post_id, updated_data):
        is_valid, error = self.validate_keys(updated_data)
        if not is_valid:
            return False, error

        try:
            result = self.db.update_one({'_id': ObjectId(post_id)}, {'$set': updated_data})
            if result.modified_count > 0:
                return True, 'Post updated successfully'
            else:
                return False, 'No post found for the given ID'
        except Exception as e:
            return False, str(e)

    def delete_post(self, post_id):
        try:
            result = self.db.delete_one({'_id': ObjectId(post_id)})
            if result.deleted_count > 0:
                return True, 'Post deleted successfully'
            else:
                return False, 'No post found for the given ID'
        except Exception as e:
            return False, str(e)

bp_manager = BlogPostManager()

@app.route('/', methods=['GET'])
def index():
     posts = bp_manager.get_all_posts()
     return json_util.dumps(posts)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/add_data', methods=['POST'])
def add_data():
    try:
        new_data = request.json
        success, message = bp_manager.add_post(new_data)

        if success:
            return jsonify({'message': 'Data added successfully', 'inserted_id': message})
        else:
            return jsonify({'Error': message}), 400

    except Exception as e:
        return jsonify({'Error': str(e)}), 500

@app.route('/blog/posts/<string:post_id>', methods=['GET'])
def get_post(post_id):
    post = bp_manager.get_post_by_id(post_id)

    if post:
        return json_util.dumps(post)
    else:
        return jsonify({'message': 'No post found for the given ID'}), 404

@app.route('/update_data/<string:post_id>', methods=['PUT'])
def update_data(post_id):
    try:
        updated_data = request.json
        success, message = bp_manager.update_post(post_id, updated_data)

        if success:
            return jsonify({'message': message})
        else:
            return jsonify({'Error': message}), 404

    except Exception as e:
        return jsonify({'Error': str(e)}), 500

@app.route('/delete_data/<string:post_id>', methods=['DELETE'])
def delete_data(post_id):
    success, message = bp_manager.delete_post(post_id)

    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'Error': message}), 404

@app.teardown_appcontext
def teardown_db(exception=None):
    pass

if __name__ == '__main__':
    app.run(debug=True)
