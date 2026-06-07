"""
API REST simples com Flask
"""

from flask import Flask, request, jsonify
from src.models import User, Post

app = Flask(__name__)


# ============= ROTAS DE HEALTH CHECK =============

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica se a API está ativa"""
    return jsonify({'status': 'ok', 'message': 'API está funcionando'}), 200


@app.route('/info', methods=['GET'])
def info():
    """Retorna informações da API"""
    return jsonify({
        'name': 'User Posts API',
        'version': '1.0.0',
        'description': 'API simples para gerenciar usuários e posts'
    }), 200


# ============= ROTAS DE USUÁRIOS =============

@app.route('/users', methods=['GET'])
def list_users():
    """Lista todos os usuários"""
    users = User.list_all()
    return jsonify([user.to_dict() for user in users]), 200


@app.route('/users', methods=['POST'])
def create_user():
    """Cria um novo usuário"""
    try:
        data = request.get_json()
        user = User.create(
            name=data.get('name'),
            email=data.get('email')
        )
        return jsonify(user.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtém um usuário específico"""
    user = User.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(user.to_dict()), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deleta um usuário"""
    if User.delete(user_id):
        return jsonify({'message': 'Usuário deletado'}), 200
    return jsonify({'error': 'Usuário não encontrado'}), 404


# ============= ROTAS DE POSTS =============

@app.route('/posts', methods=['GET'])
def list_posts():
    """Lista todos os posts"""
    posts = Post.list_all()
    return jsonify([post.to_dict() for post in posts]), 200


@app.route('/posts', methods=['POST'])
def create_post():
    """Cria um novo post"""
    try:
        data = request.get_json()
        post = Post.create(
            user_id=data.get('user_id'),
            title=data.get('title'),
            content=data.get('content')
        )
        return jsonify(post.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Obtém um post específico"""
    post = Post.get(post_id)
    if not post:
        return jsonify({'error': 'Post não encontrado'}), 404
    return jsonify(post.to_dict()), 200


@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Deleta um post"""
    if Post.delete(post_id):
        return jsonify({'message': 'Post deletado'}), 200
    return jsonify({'error': 'Post não encontrado'}), 404


@app.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    """Obtém todos os posts de um usuário"""
    user = User.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    posts = Post.list_by_user(user_id)
    return jsonify([post.to_dict() for post in posts]), 200


# ============= TRATAMENTO DE ERROS =============

@app.errorhandler(404)
def not_found(error):
    """Tratamento de rota não encontrada"""
    return jsonify({'error': 'Recurso não encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro interno"""
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
