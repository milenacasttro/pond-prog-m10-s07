"""
Testes da API REST
"""

import pytest
from src.app import app
from src.models import User, Post


@pytest.fixture
def client():
    """Cria um cliente de teste"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clean_db():
    """Limpa o banco de dados antes de cada teste"""
    User.clear()
    Post.clear()
    yield
    User.clear()
    Post.clear()


# ============= TESTES DE HEALTH CHECK =============

def test_health_check(client):
    """Testa se o health check retorna status ok"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'


def test_info(client):
    """Testa se a rota /info retorna informações"""
    response = client.get('/info')
    assert response.status_code == 200
    assert 'name' in response.json
    assert response.json['version'] == '1.0.0'


# ============= TESTES DE USUÁRIOS =============

def test_create_user_success(client):
    """Testa criação bem-sucedida de usuário"""
    response = client.post('/users', json={
        'name': 'João Silva',
        'email': 'joao@example.com'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'João Silva'
    assert response.json['email'] == 'joao@example.com'


def test_create_user_invalid_email(client):
    """Testa criação de usuário com email inválido"""
    response = client.post('/users', json={
        'name': 'João Silva',
        'email': 'email_invalido'
    })
    assert response.status_code == 400
    assert 'error' in response.json


def test_create_user_missing_fields(client):
    """Testa criação de usuário sem campos obrigatórios"""
    response = client.post('/users', json={
        'name': 'João Silva'
    })
    assert response.status_code == 400


def test_list_users_empty(client):
    """Testa listagem de usuários vazio"""
    response = client.get('/users')
    assert response.status_code == 200
    assert response.json == []


def test_list_users_with_data(client):
    """Testa listagem de usuários com dados"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    client.post('/users', json={'name': 'Maria', 'email': 'maria@example.com'})
    
    response = client.get('/users')
    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_user_by_id(client):
    """Testa obtenção de usuário por ID"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    
    response = client.get('/users/1')
    assert response.status_code == 200
    assert response.json['id'] == 1
    assert response.json['name'] == 'João'


def test_get_user_not_found(client):
    """Testa busca de usuário inexistente"""
    response = client.get('/users/999')
    assert response.status_code == 404
    assert 'error' in response.json


def test_delete_user(client):
    """Testa deleção de usuário"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    
    response = client.delete('/users/1')
    assert response.status_code == 200
    
    response = client.get('/users/1')
    assert response.status_code == 404


def test_delete_user_not_found(client):
    """Testa deleção de usuário inexistente"""
    response = client.delete('/users/999')
    assert response.status_code == 404


# ============= TESTES DE POSTS =============

def test_create_post_success(client):
    """Testa criação bem-sucedida de post"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    
    response = client.post('/posts', json={
        'user_id': 1,
        'title': 'Meu primeiro post',
        'content': 'Conteúdo interessante'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Meu primeiro post'


def test_create_post_user_not_found(client):
    """Testa criação de post para usuário inexistente"""
    response = client.post('/posts', json={
        'user_id': 999,
        'title': 'Post',
        'content': 'Conteúdo'
    })
    assert response.status_code == 400


def test_list_posts_empty(client):
    """Testa listagem de posts vazio"""
    response = client.get('/posts')
    assert response.status_code == 200
    assert response.json == []


def test_list_posts_with_data(client):
    """Testa listagem de posts com dados"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    client.post('/posts', json={'user_id': 1, 'title': 'Post 1', 'content': 'Conteúdo 1'})
    client.post('/posts', json={'user_id': 1, 'title': 'Post 2', 'content': 'Conteúdo 2'})
    
    response = client.get('/posts')
    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_post_by_id(client):
    """Testa obtenção de post por ID"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    client.post('/posts', json={'user_id': 1, 'title': 'Post 1', 'content': 'Conteúdo 1'})
    
    response = client.get('/posts/1')
    assert response.status_code == 200
    assert response.json['title'] == 'Post 1'


def test_get_post_not_found(client):
    """Testa busca de post inexistente"""
    response = client.get('/posts/999')
    assert response.status_code == 404


def test_delete_post(client):
    """Testa deleção de post"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    client.post('/posts', json={'user_id': 1, 'title': 'Post 1', 'content': 'Conteúdo 1'})
    
    response = client.delete('/posts/1')
    assert response.status_code == 200
    
    response = client.get('/posts/1')
    assert response.status_code == 404


def test_get_user_posts(client):
    """Testa obtenção de posts de um usuário"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    client.post('/users', json={'name': 'Maria', 'email': 'maria@example.com'})
    
    client.post('/posts', json={'user_id': 1, 'title': 'Post de João 1', 'content': 'Conteúdo'})
    client.post('/posts', json={'user_id': 1, 'title': 'Post de João 2', 'content': 'Conteúdo'})
    client.post('/posts', json={'user_id': 2, 'title': 'Post de Maria', 'content': 'Conteúdo'})
    
    response = client.get('/users/1/posts')
    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_user_posts_user_not_found(client):
    """Testa obtenção de posts de usuário inexistente"""
    response = client.get('/users/999/posts')
    assert response.status_code == 404


def test_post_missing_fields(client):
    """Testa criação de post sem campos obrigatórios"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    
    response = client.post('/posts', json={
        'user_id': 1,
        'title': 'Post'
    })
    assert response.status_code == 400


# ============= TESTES ADICIONAIS PARA VARIAR QUANTIDADE =============

def test_multiple_users_creation(client):
    """Testa criação de múltiplos usuários"""
    for i in range(10):
        response = client.post('/users', json={
            'name': f'Usuário {i}',
            'email': f'user{i}@example.com'
        })
        assert response.status_code == 201
    
    response = client.get('/users')
    assert len(response.json) == 10


def test_multiple_posts_creation(client):
    """Testa criação de múltiplos posts"""
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    
    for i in range(15):
        response = client.post('/posts', json={
            'user_id': 1,
            'title': f'Post {i}',
            'content': f'Conteúdo do post {i}'
        })
        assert response.status_code == 201
    
    response = client.get('/posts')
    assert len(response.json) == 15


def test_api_consistency(client):
    """Testa consistência da API"""
    # Cria usuário
    client.post('/users', json={'name': 'João', 'email': 'joao@example.com'})
    
    # Cria posts
    for i in range(5):
        client.post('/posts', json={
            'user_id': 1,
            'title': f'Post {i}',
            'content': f'Conteúdo {i}'
        })
    
    # Verifica consistência
    user_response = client.get('/users/1')
    posts_response = client.get('/users/1/posts')
    
    assert user_response.status_code == 200
    assert posts_response.status_code == 200
    assert len(posts_response.json) == 5
