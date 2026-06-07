from flask import Flask, jsonify, request

from src.models import Post, User

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/info", methods=["GET"])
def info():
    return jsonify({
        "name": "User Posts API",
        "version": "1.0.0",
    }), 200


@app.route("/users", methods=["GET"])
def list_users():
    users = User.list_all()
    return jsonify([user.to_dict() for user in users]), 200


@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user = User.create(name=data.get("name"), email=data.get("email"))
        return jsonify(user.to_dict()), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.get(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(user.to_dict()), 200


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if User.delete(user_id):
        return jsonify({"message": "Usuário deletado"}), 200
    return jsonify({"error": "Usuário não encontrado"}), 404


@app.route("/posts", methods=["GET"])
def list_posts():
    posts = Post.list_all()
    return jsonify([post.to_dict() for post in posts]), 200


@app.route("/posts", methods=["POST"])
def create_post():
    try:
        data = request.get_json()
        post = Post.create(
            user_id=data.get("user_id"),
            title=data.get("title"),
            content=data.get("content"),
        )
        return jsonify(post.to_dict()), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.get(post_id)
    if not post:
        return jsonify({"error": "Post não encontrado"}), 404
    return jsonify(post.to_dict()), 200


@app.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    if Post.delete(post_id):
        return jsonify({"message": "Post deletado"}), 200
    return jsonify({"error": "Post não encontrado"}), 404


@app.route("/users/<int:user_id>/posts", methods=["GET"])
def get_user_posts(user_id):
    if not User.get(user_id):
        return jsonify({"error": "Usuário não encontrado"}), 404
    posts = Post.list_by_user(user_id)
    return jsonify([post.to_dict() for post in posts]), 200


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Recurso não encontrado"}), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Erro interno do servidor"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
