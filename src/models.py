class User:
    _id_counter = 1
    _users_db = {}

    def __init__(self, name: str, email: str):
        self.id = User._id_counter
        self.name = name
        self.email = email
        User._id_counter += 1

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}

    @staticmethod
    def create(name: str, email: str):
        if not name or not email:
            raise ValueError("Nome e email são obrigatórios")
        if "@" not in email:
            raise ValueError("Email inválido")
        user = User(name, email)
        User._users_db[user.id] = user
        return user

    @staticmethod
    def get(user_id: int):
        return User._users_db.get(user_id)

    @staticmethod
    def list_all():
        return list(User._users_db.values())

    @staticmethod
    def delete(user_id: int):
        if user_id in User._users_db:
            del User._users_db[user_id]
            return True
        return False

    @staticmethod
    def clear():
        User._users_db.clear()
        User._id_counter = 1


class Post:
    _id_counter = 1
    _posts_db = {}

    def __init__(self, user_id: int, title: str, content: str):
        self.id = Post._id_counter
        self.user_id = user_id
        self.title = title
        self.content = content
        Post._id_counter += 1

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
        }

    @staticmethod
    def create(user_id: int, title: str, content: str):
        if not User.get(user_id):
            raise ValueError(f"Usuário {user_id} não encontrado")
        if not title or not content:
            raise ValueError("Título e conteúdo são obrigatórios")
        post = Post(user_id, title, content)
        Post._posts_db[post.id] = post
        return post

    @staticmethod
    def get(post_id: int):
        return Post._posts_db.get(post_id)

    @staticmethod
    def list_by_user(user_id: int):
        return [p for p in Post._posts_db.values() if p.user_id == user_id]

    @staticmethod
    def list_all():
        return list(Post._posts_db.values())

    @staticmethod
    def delete(post_id: int):
        if post_id in Post._posts_db:
            del Post._posts_db[post_id]
            return True
        return False

    @staticmethod
    def clear():
        Post._posts_db.clear()
        Post._id_counter = 1
