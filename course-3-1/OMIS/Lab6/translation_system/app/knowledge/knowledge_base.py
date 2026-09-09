import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'

class KnowledgeGraphService:
    def __init__(self):
        self.graph_file = DATA_DIR / 'knowledge_graph.json'
        self.graph = self._load_graph()

    def _load_graph(self):
        if self.graph_file.exists():
            with open(self.graph_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            initial_graph = {
                "люблю": {
                    "respect": {"weight": 0.3, "contexts": [{"style": "formal"}]},
                    "like": {"weight": 0.7, "contexts": [{"style": "casual"}]},
                    "adore": {"weight": 0.2, "contexts": [{"style": "poetic"}]}
                },
                "ты": {
                    "you": {"weight": 0.8, "contexts": [{"style": "casual"}]},
                    "you (formal)": {"weight": 0.9, "contexts": [{"style": "formal"}]}
                },
                "мир": {
                    "world": {"weight": 0.9, "contexts": [{"domain": "world"}]},
                    "peace": {"weight": 0.8, "contexts": [{"domain": "peace"}]}
                }
            }
            self._save_graph(initial_graph)
            return initial_graph

    def _save_graph(self, graph):
        DATA_DIR.mkdir(exist_ok=True)
        with open(self.graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

    def get_best_translation(self, word, context):
        translations = self.graph.get(word.lower(), {})
        best = None
        best_weight = 0

        for trans, data in translations.items():
            for rule in data["contexts"]:
                match = True
                for k, v in rule.items():
                    if context.get(k) != v:
                        match = False
                        break
                if match and data["weight"] > best_weight:
                    best = trans
                    best_weight = data["weight"]

        return best or word

    def update_weight(self, word, new_translation, context, delta=0.1):
        word_lower = word.lower()
        if word_lower not in self.graph:
            self.graph[word_lower] = {}

        if new_translation not in self.graph[word_lower]:
            self.graph[word_lower][new_translation] = {"weight": 0.1, "contexts": []}

        context_exists = False
        for ctx in self.graph[word_lower][new_translation]["contexts"]:
            if ctx == context:
                context_exists = True
                break
        if not context_exists:
            self.graph[word_lower][new_translation]["contexts"].append(context)
        self.graph[word_lower][new_translation]["weight"] = min(1.0, self.graph[word_lower][new_translation]["weight"] + delta)
        self._save_graph(self.graph)