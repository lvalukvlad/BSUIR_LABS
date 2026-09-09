class Translation:
    def __init__(self, trans_id, text_id, draft, final_version=None, target_language='en', quality_score=0.0):
        self.trans_id = trans_id
        self.text_id = text_id
        self.draft = draft
        self.final_version = final_version
        self.target_language = target_language
        self.quality_score = quality_score

    def approve(self, final_text):
        self.final_version = final_text
        self.quality_score = min(1.0, self.quality_score + 0.2)