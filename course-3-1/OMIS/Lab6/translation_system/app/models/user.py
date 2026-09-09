class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Translator(User):
    def __init__(self, user_size, username):
        super().__init__(user_size, username, 'translator')


class Editor(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'editor')


class Admin(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'admin')


class Expert(User):
    """Роль эксперта для консультаций по переводу"""
    def __init__(self, user_id, username, specialization=None):
        super().__init__(user_id, username, 'expert')
        self.specialization = specialization  # 'literary', 'technical', 'medical', etc.
    
    def provide_consultation(self, translation_id, advice, rating=None):
        """Предоставляет консультацию по переводу"""
        return {
            'expert_id': self.user_id,
            'translation_id': translation_id,
            'advice': advice,
            'rating': rating,
            'specialization': self.specialization
        }