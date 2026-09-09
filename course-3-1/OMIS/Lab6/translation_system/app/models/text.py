class Text:
    def __init__(self, text_id, content, source_language, context=None):
        self.text_id = text_id
        self.content = content
        self.source_language = source_language
        self.context = context or {}

    def __repr__(self):
        return f"<Text id={self.text_id} lang={self.source_language}>"