import math
from collections import defaultdict

class SemanticVectorService:
    SEMANTIC_VECTORS = {
        "люблю": [0.1, 0.9, 0.3],
        "уважаю": [0.8, 0.4, 0.3],
        "ненавижу": [0.9, 0.1, 0.2],
        "терпеть не могу": [0.8, 0.2, 0.1],
        "работа": [0.5, 0.2, 0.8],
        "труд": [0.6, 0.1, 0.7],
    }
    
    ANTONYMS = {
        "люблю": ["ненавижу", "терпеть не могу"],
        "ненавижу": ["люблю"],
        "терпеть не могу": ["люблю"],
    }

    @classmethod
    def get_vector(cls, word):
        return cls.SEMANTIC_VECTORS.get(word.lower(), [0.0] * 3)

    @classmethod
    def cosine_similarity(cls, vec1, vec2):
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @classmethod
    def find_similar_words(cls, word, threshold=0.7):
        target_vec = cls.get_vector(word)
        similar = []
        word_lower = word.lower()
        antonyms = cls.ANTONYMS.get(word_lower, [])
        
        for w, vec in cls.SEMANTIC_VECTORS.items():
            if w != word and w.lower() not in antonyms:
                sim = cls.cosine_similarity(target_vec, vec)
                if sim >= threshold:
                    similar.append((w, sim))
        return sorted(similar, key=lambda x: x[1], reverse=True)