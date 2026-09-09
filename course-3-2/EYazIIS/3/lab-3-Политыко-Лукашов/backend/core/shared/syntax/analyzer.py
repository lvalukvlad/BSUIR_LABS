from typing import Any
import pymorphy3
from razdel import sentenize, tokenize

from core.shared.syntax.spacy_dependency import build_flat_dependency_spacy


class DependencyNode:
    def __init__(
        self, token_data: dict[str, Any], head_id: int | None = None, relation: str = ""
    ):
        self.id = id(self)
        self.token_data = token_data
        self.head_id = head_id
        self.relation = relation
        self.children: list[DependencyNode] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "token_text": self.token_data.get("token", ""),
            "lemma": self.token_data.get("lemma", ""),
            "pos": self.token_data.get("pos", ""),
            "pos_name": self.token_data.get("pos_name", ""),
            "head_id": self.head_id,
            "relation": self.relation,
            "children": [c.to_dict() for c in self.children],
        }


class ConstituencyNode:
    def __init__(self, label: str, label_ru: str):
        self.id = id(self)
        self.label = label
        self.label_ru = label_ru
        self.children: list[ConstituencyNode | str] = []

    def add_child(self, child: "ConstituencyNode | str"):
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "label_ru": self.label_ru,
            "children": [
                c.to_dict() if isinstance(c, ConstituencyNode) else c
                for c in self.children
            ],
        }


class SyntaxAnalyzer:
    POS_MAP = {
        "NOUN": "существительное",
        "ADJF": "прилагательное",
        "ADJS": "краткое прилагательное",
        "COMP": "сравнительная степень",
        "VERB": "глагол",
        "INFN": "инфинитив",
        "PRTF": "причастие",
        "PRTS": "краткое причастие",
        "GRND": "деепричастие",
        "NUMR": "числительное",
        "NPRO": "местоимение",
        "PRED": "предикатив",
        "PREP": "предлог",
        "CONJ": "союз",
        "PRCL": "частица",
        "INTJ": "междометие",
        "ADVB": "наречие",
        "PUNCT": "пунктуация",
    }

    CASE_MAP = {
        "nomn": "именительный",
        "gent": "родительный",
        "datv": "дательный",
        "accs": "винительный",
        "ablt": "творительный",
        "loct": "предложный",
        "voct": "звательный",
        "gen1": "родительный 1",
        "gen2": "родительный 2",
        "acc2": "винительный 2",
        "loc1": "предложный 1",
        "loc2": "предложный 2",
    }

    NUMBER_MAP = {"sing": "единственное", "plur": "множественное"}

    GENDER_MAP = {
        "masc": "мужской",
        "femn": "женский",
        "neut": "средний",
        "ms-f": "общий",
    }

    RELATION_TYPES = {
        "nominal_subject": "подлежащее",
        "predicate": "сказуемое",
        "direct_object": "прямое дополнение",
        "indirect_object": "косвенное дополнение",
        "attribute": "определение",
        "adverbial_modifier": "обстоятельство",
        "prepositional_phrase": "предложная группа",
        "conjunction": "союз",
        "particle": "частица",
        "preposition": "предлог",
        "root": "корень",
        "punctuation": "пунктуация",
    }

    CONSTITUENCY_LABELS = {
        "S": ("S", "Предложение"),
        "NP": ("NP", "Именная группа"),
        "VP": ("VP", "Глагольная группа"),
        "AP": ("AP", "Адъективная группа"),
        "PP": ("PP", "Предложная группа"),
        "AdjP": ("AdjP", "Адъективная группа"),
        "NumP": ("NumP", "Числительная группа"),
        "AdvP": ("AdvP", "Адвербиальная группа"),
        "InfP": ("InfP", "Инфинитивная группа"),
        "Punct": ("Punct", "Пунктуация"),
    }

    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()

    def _get_pos_name(self, pos: str) -> str:
        return self.POS_MAP.get(pos, pos)

    def _get_case_name(self, case: str) -> str:
        return self.CASE_MAP.get(case, case)

    def _get_number_name(self, number: str) -> str:
        return self.NUMBER_MAP.get(number, number)

    def _get_gender_name(self, gender: str) -> str:
        return self.GENDER_MAP.get(gender, gender)

    def _determine_syntax_role(
        self,
        pos: str,
        case: str | None,
        animacy: str | None,
        word_index: int,
        sentence_words: list,
        is_punct: bool = False,
    ) -> str:
        if is_punct or pos == "PREP" or pos == "CONJ" or pos == "PRCL" or pos == "INTJ":
            return ""

        if (
            pos == "VERB"
            or pos == "INFN"
            or pos == "PRTF"
            or pos == "PRTS"
            or pos == "GRND"
        ):
            return "сказуемое"

        if pos == "ADJF" or pos == "ADJS" or pos == "PRTF" or pos == "PRTS":
            return "определение"

        if pos == "ADVB":
            return "обстоятельство"

        if pos == "NUMR":
            return "определение"

        if pos == "NPRO":
            if case == "nomn":
                return "подлежащее"
            return "дополнение"

        if pos == "NOUN":
            if case == "nomn":
                return "подлежащее"
            elif case in ("gent", "datv", "accs", "ablt", "loct"):
                return "дополнение"
            return "дополнение"

        return ""

    def analyze_token(
        self, token_text: str, word_index: int, sentence_words: list
    ) -> dict[str, Any]:
        parsed = self.morph.parse(token_text)

        if not parsed:
            return {
                "token": token_text,
                "pos": "",
                "pos_name": "",
                "lemma": token_text.lower(),
                "case": "",
                "number": "",
                "gender": "",
                "tense": "",
                "person": "",
                "animacy": "",
                "grammemes": {},
                "syntax_role": "",
                "syntax_role_name": "",
            }

        p = parsed[0]

        is_punctuation = not token_text.isalnum() and not token_text.isalpha()
        pos = p.tag.POS or ""
        case = p.tag.case or ""
        number = p.tag.number or ""
        gender = p.tag.gender or ""
        tense = p.tag.tense or ""
        person = p.tag.person or ""
        animacy = p.tag.animacy or ""

        grammemes = {}
        if case:
            grammemes["падеж"] = self._get_case_name(case)
        if number:
            grammemes["число"] = self._get_number_name(number)
        if gender:
            grammemes["род"] = self._get_gender_name(gender)
        if tense:
            grammemes["время"] = tense
        if person:
            grammemes["лицо"] = person
        if animacy:
            grammemes["одушевлённость"] = animacy

        syntax_role = self._determine_syntax_role(
            pos, case, animacy, word_index, sentence_words, is_punctuation
        )

        syntax_role_map = {
            "подлежащее": "подлежащее",
            "сказуемое": "сказуемое",
            "дополнение": "дополнение",
            "определение": "определение",
            "обстоятельство": "обстоятельство",
        }

        return {
            "token": token_text,
            "pos": "PUNCT" if is_punctuation else pos,
            "pos_name": "пунктуация" if is_punctuation else self._get_pos_name(pos),
            "lemma": token_text if is_punctuation else p.normal_form,
            "case": case,
            "case_name": self._get_case_name(case) if case else "",
            "number": number,
            "number_name": self._get_number_name(number) if number else "",
            "gender": gender,
            "gender_name": self._get_gender_name(gender) if gender else "",
            "tense": tense,
            "person": person,
            "animacy": animacy,
            "grammemes": grammemes,
            "syntax_role": syntax_role,
            "syntax_role_name": syntax_role_map.get(syntax_role, ""),
        }

    def analyze_sentence(
        self, sentence_text: str, sentence_index: int
    ) -> dict[str, Any]:
        tokens = list(tokenize(sentence_text))

        sentence_words = []
        for i, token in enumerate(tokens):
            token_analysis = self.analyze_token(token.text, i + 1, [])
            token_analysis["position"] = i + 1
            token_analysis["char_start"] = token.start
            token_analysis["char_end"] = token.stop
            sentence_words.append(token_analysis)

        for i, word in enumerate(sentence_words):
            word["sentence_position"] = i + 1

        return {
            "sentence_index": sentence_index + 1,
            "sentence": sentence_text,
            "tokens": sentence_words,
            "token_count": len(tokens),
            "dependency_tree": self.build_dependency_tree(sentence_words),
            "constituency_tree": self.build_constituency_tree(sentence_words),
        }

    def analyze_text(self, text: str) -> list[dict[str, Any]]:
        sentences = list(sentenize(text))

        results = []
        for i, sent in enumerate(sentences):
            sentence_analysis = self.analyze_sentence(sent.text, i)
            results.append(sentence_analysis)

        return results

    def build_constituency_tree(self, tokens: list[dict]):
        tree_builder = ConstituencyTreeBuilder(self)
        sentence_data = {"tokens": tokens}
        return tree_builder.build_tree(sentence_data)

    def build_dependency_tree(self, tokens: list[dict]):
        tree_builder = DependencyTreeBuilder(self)
        sentence_data = {"tokens": tokens}
        return tree_builder.build_tree(sentence_data)

    def get_statistics(self, analysis: list[dict[str, Any]]) -> dict[str, Any]:
        pos_stats: dict[str, int] = {}
        syntax_role_stats: dict[str, int] = {}
        total_tokens = 0

        for sentence in analysis:
            for token in sentence.get("tokens", []):
                total_tokens += 1

                pos = token.get("pos_name", "")
                if pos:
                    pos_stats[pos] = pos_stats.get(pos, 0) + 1

                role = token.get("syntax_role_name", "")
                if role:
                    syntax_role_stats[role] = syntax_role_stats.get(role, 0) + 1

        return {
            "total_sentences": len(analysis),
            "total_tokens": total_tokens,
            "pos_distribution": pos_stats,
            "syntax_role_distribution": syntax_role_stats,
        }

    def detect_relations(self, tokens: list) -> list[dict[str, Any]]:
        relations = []

        tokens_by_role = {
            "подлежащее": [],
            "сказуемое": [],
            "дополнение": [],
            "определение": [],
            "обстоятельство": [],
        }

        for token in tokens:
            role = getattr(token, "syntax_role", "") or ""
            if role in tokens_by_role:
                tokens_by_role[role].append(token)

        for subject in tokens_by_role["подлежащее"]:
            for predicate in tokens_by_role["сказуемое"]:
                if subject.position < predicate.position:
                    relations.append(
                        {
                            "from_token_id": subject.id,
                            "to_token_id": predicate.id,
                            "relation_type": "subject-predicate",
                            "relation_name": "подлежащее-сказуемое",
                            "description": f'"{subject.token_text}" → "{predicate.token_text}"',
                        }
                    )

        for predicate in tokens_by_role["сказуемое"]:
            for obj in tokens_by_role["дополнение"]:
                if predicate.position < obj.position:
                    relations.append(
                        {
                            "from_token_id": predicate.id,
                            "to_token_id": obj.id,
                            "relation_type": "predicate-object",
                            "relation_name": "сказуемое-дополнение",
                            "description": f'"{predicate.token_text}" → "{obj.token_text}"',
                        }
                    )

        for attribute in tokens_by_role["определение"]:
            for noun in tokens_by_role["подлежащее"] + tokens_by_role["дополнение"]:
                if (
                    attribute.position < noun.position
                    and attribute.position + 1 == noun.position
                ):
                    relations.append(
                        {
                            "from_token_id": attribute.id,
                            "to_token_id": noun.id,
                            "relation_type": "attribute-noun",
                            "relation_name": "определение-существительное",
                            "description": f'"{attribute.token_text}" → "{noun.token_text}"',
                        }
                    )

        for adverbial in tokens_by_role["обстоятельство"]:
            for predicate in tokens_by_role["сказуемое"]:
                relations.append(
                    {
                        "from_token_id": adverbial.id,
                        "to_token_id": predicate.id,
                        "relation_type": "adverbial-predicate",
                        "relation_name": "обстоятельство-сказуемое",
                        "description": f'"{adverbial.token_text}" → "{predicate.token_text}"',
                    }
                )

        return relations

class DependencyTreeBuilder:
    RELATION_RU = {
        "nsubj": "подлежащее",
        "nsubj:pass": "подлежащее (страдат.)",
        "root": "корень",
        "obl": "обстоятельство",
        "obl:agent": "обстоятельство (агент)",
        "obj": "дополнение",
        "iobj": "косвенное дополнение",
        "ccomp": "дополнение (придаточное)",
        "xcomp": "дополнение (открытое)",
        "amod": "определение",
        "nmod": "определение (именное)",
        "appos": "приложение",
        "conj": "однородное",
        "cc": "союз",
        "punct": "пунктуация",
        "case": "предлог",
        "det": "определитель",
        "advmod": "обстоятельство (наречие)",
        "aux": "вспомогат. глагол",
        "aux:pass": "вспомогат. глагол (страдат.)",
        "mark": "маркер",
        "advcl": "обстоятельство (придаточное)",
        "acl": "определение (придаточное)",
        "compound": "сложное слово",
        "flat": "неразложимое",
        "fixed": "устойчивое",
        "dep": "зависимое слово",
        "parataxis": "паратаксис",
        "discourse": "дискурсивный элемент",
        "vocative": "звательное",
        "expl": "эксплетив",
        "list": "перечисление",
        "orphan": "сирота (эллипсис)",
        "goeswith": "слитное написание",
        "reparandum": "исправление",
        "dislocated": "вынесенный элемент",
    }

    def __init__(self, syntax_analyzer: SyntaxAnalyzer):
        self.analyzer = syntax_analyzer

    def build_tree(self, sentence_data: dict[str, Any]) -> dict[str, Any]:
        tokens = sentence_data.get("tokens", [])

        if not tokens:
            return {"tree": None, "flat_representation": []}

        sentence_text = (
            sentence_data.get("sentence")
            or sentence_data.get("sentence_text")
            or ""
        )
        spacy_try = build_flat_dependency_spacy(
            sentence_text,
            tokens,
            self.RELATION_RU,
            self._token_text,
            self._safe_pos,
        )
        if spacy_try is not None:
            flat_repr, root_index = spacy_try
            tree = self._build_tree_structure(flat_repr, root_index)
            return {
                "tree": tree,
                "flat_representation": flat_repr,
                "root_token": self._token_text(tokens[root_index]) if tokens else None,
                "root_index": root_index,
            }

        root_index = self._pick_root(tokens)
        flat_repr: list[dict[str, Any]] = []

        for i, token in enumerate(tokens):
            head_index, relation = self._assign_head_and_relation(i, tokens, root_index)
            relation_ru = self.RELATION_RU.get(
                relation, token.get("syntax_role_name", "") or relation
            )
            flat_repr.append(
                {
                    "id": i + 1,
                    "token": self._token_text(token),
                    "lemma": token.get("lemma", ""),
                    "pos": self._safe_pos(token),
                    "pos_name": token.get("pos_name", ""),
                    "head": 0 if head_index is None else head_index + 1,
                    "relation": relation,
                    "relation_ru": relation_ru,
                    "syntax_role": token.get("syntax_role", ""),
                    "syntax_role_name": token.get("syntax_role_name", ""),
                    "case": token.get("case", ""),
                    "case_name": token.get("case_name", ""),
                    "number": token.get("number", ""),
                    "number_name": token.get("number_name", ""),
                    "gender": token.get("gender", ""),
                    "gender_name": token.get("gender_name", ""),
                }
            )

        tree = self._build_tree_structure(flat_repr, root_index)

        return {
            "tree": tree,
            "flat_representation": flat_repr,
            "root_token": self._token_text(tokens[root_index]) if tokens else None,
            "root_index": root_index,
        }

    def _safe_pos(self, token: dict[str, Any]) -> str:
        return str(token.get("pos", "") or "")

    def _token_text(self, token: dict[str, Any]) -> str:
        return str(token.get("token", token.get("token_text", "")) or "")

    def _pick_root(self, tokens: list[dict[str, Any]]) -> int:
        for i, token in enumerate(tokens):
            if token.get("syntax_role", "") == "сказуемое":
                return i

        for i, token in enumerate(tokens):
            if self._safe_pos(token) in ("VERB", "INFN"):
                return i

        for i, token in enumerate(tokens):
            if self._safe_pos(token) != "PUNCT":
                return i

        return 0

    def _assign_head_and_relation(
        self, token_index: int, tokens: list[dict[str, Any]], root_index: int
    ) -> tuple[int | None, str]:
        if token_index == root_index:
            return None, "root"

        token = tokens[token_index]
        pos = self._safe_pos(token)
        role = token.get("syntax_role", "")

        if pos == "PUNCT":
            head = self._nearest_index(
                token_index,
                tokens,
                predicate=lambda t: self._safe_pos(t) != "PUNCT",
                prefer_left=True,
            )
            return (head if head is not None else root_index, "punct")

        if pos == "PREP":
            noun_head = self._nearest_index(
                token_index,
                tokens,
                predicate=lambda t: self._safe_pos(t) in ("NOUN", "NPRO"),
                prefer_left=False,
            )
            return (noun_head if noun_head is not None else root_index, "case")

        if role == "подлежащее":
            return root_index, "nsubj"

        if role == "дополнение":
            verb_head = self._nearest_index(
                token_index,
                tokens,
                predicate=lambda t: self._safe_pos(t) in ("VERB", "INFN"),
                prefer_left=True,
            )
            return (verb_head if verb_head is not None else root_index, "obj")

        if role == "определение":
            noun_head = self._nearest_index(
                token_index,
                tokens,
                predicate=lambda t: self._safe_pos(t) in ("NOUN", "NPRO")
                or t.get("syntax_role", "") in ("подлежащее", "дополнение"),
                prefer_left=False,
            )
            relation = "amod" if pos in ("ADJF", "ADJS", "PRTF", "PRTS") else "nmod"
            return (noun_head if noun_head is not None else root_index, relation)

        if role == "обстоятельство":
            verb_head = self._nearest_index(
                token_index,
                tokens,
                predicate=lambda t: self._safe_pos(t) in ("VERB", "INFN"),
                prefer_left=True,
            )
            relation = "advmod" if pos == "ADVB" else "obl"
            return (verb_head if verb_head is not None else root_index, relation)

        if pos == "CONJ":
            conj_head = self._nearest_index(
                token_index,
                tokens,
                predicate=lambda t: self._safe_pos(t) not in ("PUNCT", "CONJ"),
                prefer_left=True,
            )
            return (conj_head if conj_head is not None else root_index, "cc")

        if pos in ("VERB", "INFN") and token_index != root_index:
            return root_index, "xcomp"

        fallback_head = self._nearest_index(
            token_index,
            tokens,
            predicate=lambda t: self._safe_pos(t) != "PUNCT",
            prefer_left=True,
        )
        return (fallback_head if fallback_head is not None else root_index, "dep")

    def _nearest_index(
        self,
        start: int,
        tokens: list[dict[str, Any]],
        predicate,
        prefer_left: bool,
    ) -> int | None:
        left_range = range(start - 1, -1, -1)
        right_range = range(start + 1, len(tokens))
        ranges = [left_range, right_range] if prefer_left else [right_range, left_range]

        for seq in ranges:
            for idx in seq:
                if predicate(tokens[idx]):
                    return idx
        return None

    def _build_tree_structure(self, nodes: list[dict[str, Any]], root_index: int) -> dict:
        if not nodes or root_index >= len(nodes):
            return {}

        by_id: dict[int, dict[str, Any]] = {}
        for node in nodes:
            by_id[node["id"]] = {
                "id": node["id"],
                "token": node["token"],
                "pos": node["pos"],
                "relation": node["relation"],
                "relation_ru": node["relation_ru"],
                "children": [],
            }

        for node in nodes:
            head = node["head"]
            if head > 0 and head in by_id and head != node["id"]:
                by_id[head]["children"].append(by_id[node["id"]])

        def sort_children(subtree: dict[str, Any]) -> None:
            subtree["children"].sort(key=lambda n: n["id"])
            for child in subtree["children"]:
                sort_children(child)

        root = by_id[nodes[root_index]["id"]]
        sort_children(root)
        return root


class ConstituencyTreeBuilder:
    def __init__(self, syntax_analyzer: SyntaxAnalyzer):
        self.analyzer = syntax_analyzer

    def build_tree(self, sentence_data: dict[str, Any]) -> dict[str, Any]:
        tokens = sentence_data.get("tokens", [])

        if not tokens:
            return {"tree": None}

        root = self._build_sentence_tree(tokens)
        return {"tree": root.to_dict(), "linearized": self._linearize_tree(root)}

    def _safe_pos(self, token: dict[str, Any]) -> str:
        return str(token.get("pos", "") or "")

    def _safe_role(self, token: dict[str, Any]) -> str:
        return str(token.get("syntax_role", "") or "")

    def _token_text(self, token: dict[str, Any]) -> str:
        return str(token.get("token", token.get("token_text", "")) or "")

    def _is_boundary(self, token: dict[str, Any]) -> bool:
        return self._safe_pos(token) in ("PUNCT", "CONJ")

    def _is_nounish(self, token: dict[str, Any]) -> bool:
        pos = self._safe_pos(token)
        role = self._safe_role(token)
        return pos in ("NOUN", "NPRO") or role in ("подлежащее", "дополнение")

    def _is_modifier(self, token: dict[str, Any]) -> bool:
        pos = self._safe_pos(token)
        role = self._safe_role(token)
        return pos in ("ADJF", "ADJS", "PRTF", "PRTS", "NUMR") or role == "определение"

    def _is_verbish(self, token: dict[str, Any]) -> bool:
        return self._safe_pos(token) in ("VERB", "INFN", "GRND")

    def _build_token_node(self, label: str, label_ru: str, token: dict[str, Any]) -> ConstituencyNode:
        node = ConstituencyNode(label, label_ru)
        node.add_child(self._token_text(token))
        return node

    def _build_sentence_tree(self, tokens: list[dict[str, Any]]) -> ConstituencyNode:
        sentence = ConstituencyNode("S", "Предложение")
        i = 0

        while i < len(tokens):
            token = tokens[i]
            pos = self._safe_pos(token)
            role = self._safe_role(token)

            if pos == "PUNCT":
                punct = ConstituencyNode("Punct", "Пунктуация")
                while i < len(tokens) and self._safe_pos(tokens[i]) == "PUNCT":
                    punct.add_child(self._token_text(tokens[i]))
                    i += 1
                sentence.add_child(punct)
                continue

            if pos == "PREP":
                pp_node, i = self._build_pp(tokens, i)
                sentence.add_child(pp_node)
                continue

            if self._is_verbish(token) or role == "сказуемое":
                vp_node, i = self._build_vp(tokens, i)
                sentence.add_child(vp_node)
                continue

            if self._is_nounish(token) or self._is_modifier(token):
                np_node, i = self._build_np(tokens, i)
                sentence.add_child(np_node)
                continue

            if pos == "ADVB":
                sentence.add_child(self._build_token_node("AdvP", "Наречная группа", token))
            elif pos == "CONJ":
                sentence.add_child(self._build_token_node("Conj", "Союз", token))
            else:
                sentence.add_child(self._build_token_node("X", "Прочее", token))
            i += 1

        return sentence

    def _build_np(
        self, tokens: list[dict[str, Any]], start: int
    ) -> tuple[ConstituencyNode, int]:
        node = ConstituencyNode("NP", "Именная группа")
        i = start
        has_noun = False

        while i < len(tokens):
            token = tokens[i]
            if self._is_boundary(token) or self._safe_pos(token) == "PREP":
                break

            if self._is_modifier(token):
                node.add_child(self._build_token_node("Adj", "Определение", token))
                i += 1
                continue

            if self._is_nounish(token):
                node.add_child(self._build_token_node("N", "Имя", token))
                has_noun = True
                i += 1
                continue

            if self._safe_pos(token) == "ADVB" and not has_noun:
                node.add_child(self._build_token_node("AdvP", "Наречная группа", token))
                i += 1
                continue

            break

        if not node.children:
            node.add_child(self._token_text(tokens[start]))
            return node, start + 1

        return node, i

    def _build_vp(
        self, tokens: list[dict[str, Any]], start: int
    ) -> tuple[ConstituencyNode, int]:
        node = ConstituencyNode("VP", "Глагольная группа")
        i = start
        has_verb = False

        while i < len(tokens):
            token = tokens[i]
            pos = self._safe_pos(token)
            role = self._safe_role(token)

            if self._is_boundary(token):
                break

            if pos == "PREP":
                pp_node, i = self._build_pp(tokens, i)
                node.add_child(pp_node)
                continue

            if self._is_verbish(token) or role == "сказуемое":
                node.add_child(self._build_token_node("V", "Глагол", token))
                has_verb = True
                i += 1
                continue

            if pos == "ADVB" or role == "обстоятельство":
                node.add_child(self._build_token_node("AdvP", "Наречная группа", token))
                i += 1
                continue

            if self._is_nounish(token) or role in ("дополнение", "подлежащее"):
                np_node, i = self._build_np(tokens, i)
                node.add_child(np_node)
                continue

            if has_verb:
                break
            i += 1

        if not node.children:
            node.add_child(self._token_text(tokens[start]))
            return node, start + 1

        return node, i

    def _build_pp(
        self, tokens: list[dict[str, Any]], start: int
    ) -> tuple[ConstituencyNode, int]:
        node = ConstituencyNode("PP", "Предложная группа")
        node.add_child(self._build_token_node("Prep", "Предлог", tokens[start]))
        i = start + 1

        if i < len(tokens) and not self._is_boundary(tokens[i]):
            np_node, i = self._build_np(tokens, i)
            node.add_child(np_node)

        return node, i

    def _linearize_tree(self, node: ConstituencyNode) -> str:
        if isinstance(node, str):
            return node

        if not node.children:
            return node.label

        children_str = []
        for child in node.children:
            children_str.append(self._linearize_tree(child))

        return f"({node.label} {' '.join(children_str)})"
