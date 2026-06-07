"""
Modelos de dados da aplicação
"""


class User:
    """Modelo de usuário"""
    
    _id_counter = 1
    _users_db = {}  # Simulando um banco de dados em memória
    
    def __init__(self, name: str, email: str):
        """
        Inicializa um usuário
        
        Args:
            name: Nome do usuário
            email: Email do usuário
        """
        self.id = User._id_counter
        self.name = name
        self.email = email
        User._id_counter += 1
    
    def to_dict(self):
        """Converte usuário para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
    
    @staticmethod
    def create(name: str, email: str):
        """Cria um novo usuário"""
        if not name or not email:
            raise ValueError("Nome e email são obrigatórios")
        
        if '@' not in email:
            raise ValueError("Email inválido")
        
        user = User(name, email)
        User._users_db[user.id] = user
        return user
    
    @staticmethod
    def get(user_id: int):
        """Obtém um usuário por ID"""
        return User._users_db.get(user_id)
    
    @staticmethod
    def list_all():
        """Lista todos os usuários"""
        return list(User._users_db.values())
    
    @staticmethod
    def delete(user_id: int):
        """Deleta um usuário"""
        if user_id in User._users_db:
            del User._users_db[user_id]
            return True
        return False
    
    @staticmethod
    def clear():
        """Limpa o banco de dados (para testes)"""
        User._users_db.clear()
        User._id_counter = 1


class Post:
    """Modelo de post/mensagem"""
    
    _id_counter = 1
    _posts_db = {}
    
    def __init__(self, user_id: int, title: str, content: str):
        """
        Inicializa um post
        
        Args:
            user_id: ID do usuário que criou o post
            title: Título do post
            content: Conteúdo do post
        """
        self.id = Post._id_counter
        self.user_id = user_id
        self.title = title
        self.content = content
        Post._id_counter += 1
    
    def to_dict(self):
        """Converte post para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content
        }
    
    @staticmethod
    def create(user_id: int, title: str, content: str):
        """Cria um novo post"""
        user = User.get(user_id)
        if not user:
            raise ValueError(f"Usuário {user_id} não encontrado")
        
        if not title or not content:
            raise ValueError("Título e conteúdo são obrigatórios")
        
        post = Post(user_id, title, content)
        Post._posts_db[post.id] = post
        return post
    
    @staticmethod
    def get(post_id: int):
        """Obtém um post por ID"""
        return Post._posts_db.get(post_id)
    
    @staticmethod
    def list_by_user(user_id: int):
        """Lista todos os posts de um usuário"""
        return [p for p in Post._posts_db.values() if p.user_id == user_id]
    
    @staticmethod
    def list_all():
        """Lista todos os posts"""
        return list(Post._posts_db.values())
    
    @staticmethod
    def delete(post_id: int):
        """Deleta um post"""
        if post_id in Post._posts_db:
            del Post._posts_db[post_id]
            return True
        return False
    
    @staticmethod
    def clear():
        """Limpa o banco de dados (para testes)"""
        Post._posts_db.clear()
        Post._id_counter = 1
