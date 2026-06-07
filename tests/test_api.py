import pytest

from src.app import app
from src.models import Post, User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_db():
    User.clear()
    Post.clear()
    yield
    User.clear()
    Post.clear()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_info(client):
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json["name"] == "User Posts API"


def test_create_user_success(client):
    response = client.post(
        "/users",
        json={"name": "João Silva", "email": "joao@example.com"},
    )
    assert response.status_code == 201
    assert response.json["email"] == "joao@example.com"


def test_create_user_invalid_email(client):
    response = client.post(
        "/users",
        json={"name": "João Silva", "email": "email_invalido"},
    )
    assert response.status_code == 400


def test_create_user_missing_fields(client):
    response = client.post("/users", json={"name": "João Silva"})
    assert response.status_code == 400


def test_list_users_empty(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json == []


def test_list_users_with_data(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    client.post("/users", json={"name": "Maria", "email": "maria@example.com"})
    response = client.get("/users")
    assert len(response.json) == 2


def test_get_user_by_id(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json["id"] == 1


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404


def test_delete_user(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    assert client.delete("/users/1").status_code == 200
    assert client.get("/users/1").status_code == 404


def test_delete_user_not_found(client):
    assert client.delete("/users/999").status_code == 404


def test_create_post_success(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    response = client.post(
        "/posts",
        json={
            "user_id": 1,
            "title": "Meu primeiro post",
            "content": "Conteúdo interessante",
        },
    )
    assert response.status_code == 201


def test_create_post_user_not_found(client):
    response = client.post(
        "/posts",
        json={"user_id": 999, "title": "Post", "content": "Conteúdo"},
    )
    assert response.status_code == 400


def test_list_posts_empty(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json == []


def test_list_posts_with_data(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    payload = {"user_id": 1, "title": "Post", "content": "Conteúdo"}
    client.post("/posts", json={**payload, "title": "Post 1"})
    client.post("/posts", json={**payload, "title": "Post 2"})
    response = client.get("/posts")
    assert len(response.json) == 2


def test_get_post_by_id(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    client.post(
        "/posts",
        json={"user_id": 1, "title": "Post 1", "content": "Conteúdo 1"},
    )
    response = client.get("/posts/1")
    assert response.status_code == 200
    assert response.json["title"] == "Post 1"


def test_get_post_not_found(client):
    assert client.get("/posts/999").status_code == 404


def test_delete_post(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    client.post(
        "/posts",
        json={"user_id": 1, "title": "Post 1", "content": "Conteúdo 1"},
    )
    assert client.delete("/posts/1").status_code == 200
    assert client.get("/posts/1").status_code == 404


def test_get_user_posts(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    client.post("/users", json={"name": "Maria", "email": "maria@example.com"})
    post = {"user_id": 1, "content": "Conteúdo"}
    client.post("/posts", json={**post, "title": "Post de João 1"})
    client.post("/posts", json={**post, "title": "Post de João 2"})
    client.post(
        "/posts",
        json={"user_id": 2, "title": "Post de Maria", "content": "Conteúdo"},
    )
    response = client.get("/users/1/posts")
    assert len(response.json) == 2


def test_get_user_posts_user_not_found(client):
    assert client.get("/users/999/posts").status_code == 404


def test_post_missing_fields(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    response = client.post("/posts", json={"user_id": 1, "title": "Post"})
    assert response.status_code == 400


def test_multiple_users_creation(client):
    for i in range(10):
        response = client.post(
            "/users",
            json={"name": f"Usuário {i}", "email": f"user{i}@example.com"},
        )
        assert response.status_code == 201
    assert len(client.get("/users").json) == 10


def test_multiple_posts_creation(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    for i in range(15):
        response = client.post(
            "/posts",
            json={
                "user_id": 1,
                "title": f"Post {i}",
                "content": f"Conteúdo do post {i}",
            },
        )
        assert response.status_code == 201
    assert len(client.get("/posts").json) == 15


def test_api_consistency(client):
    client.post("/users", json={"name": "João", "email": "joao@example.com"})
    for i in range(5):
        client.post(
            "/posts",
            json={
                "user_id": 1,
                "title": f"Post {i}",
                "content": f"Conteúdo {i}",
            },
        )
    assert client.get("/users/1").status_code == 200
    posts = client.get("/users/1/posts").json
    assert len(posts) == 5
