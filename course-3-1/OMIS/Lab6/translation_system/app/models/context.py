class Context:
    def __init__(self, style=None, cultural_notes=None, translation_type='adaptive'):
        self.style = style
        self.cultural_notes = cultural_notes or []
        self.translation_type = translation_type