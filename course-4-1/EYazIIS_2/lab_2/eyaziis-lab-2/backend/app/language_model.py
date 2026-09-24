import math
import pickle
import time
from collections import Counter
from pathlib import Path

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder

from .config import (
    LANGUAGE_SHARE_THRESHOLD,
    MIN_LEXEME_LEN,
    MIN_OCCURRENCES,
    TOP_WORDS_COUNT,
    N_GRAM_MIN,
    N_GRAM_MAX,
    MIN_NGRAM_DF,
    MLP_HIDDEN_LAYERS,
    MLP_MAX_ITER,
    MLP_RANDOM_STATE,
    UNSEEN_PROB,
)
from .text_processing import CYRILLIC_RE, LATIN_RE, lexemes, reset_preprocess_cache


def _ranked(profile: dict[str, float]) -> list[str]:
    return [item for item, _ in sorted(profile.items(), key=lambda pair: (-pair[1], pair[0]))]


def _finite(value):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return None
    return value


def _softmax(log_scores: dict[str, float]) -> dict[str, float]:
    if not log_scores:
        return {}
    top = max(log_scores.values())
    exps = {key: math.exp(value - top) for key, value in log_scores.items()}
    total = sum(exps.values()) or 1.0
    return {key: value / total for key, value in exps.items()}


def _confidence(log_scores: dict[str, float], token_count: int) -> dict[str, float]:
    count = token_count or 1
    return _softmax({lang: score / count for lang, score in log_scores.items()})


def _script_shares(feature_names: list[str], present: set[str]) -> dict[str, float]:
    russian = 0
    german = 0
    for name in feature_names:
        if name not in present:
            continue
        gram = name.split(":", 1)[-1]
        cyrillic = CYRILLIC_RE.search(gram) is not None
        latin = LATIN_RE.search(gram) is not None
        if cyrillic and not latin:
            russian += 1
        elif latin and not cyrillic:
            german += 1
    total = russian + german
    if total == 0:
        return {}
    return {"русский": russian / total, "немецкий": german / total}


def _empty_result(method: str, details: dict | None = None) -> dict:
    return {
        "language": "unknown",
        "languages": [],
        "shares": {},
        "confidence": 0.0,
        "score": 0.0,
        "oop": None,
        "matched": 0,
        "distances": details or {},
        "method": method,
    }


def _pack_result(method: str, shares: dict[str, float], details: dict | None = None, evidence: bool = True) -> dict:
    if not evidence or not shares:
        return _empty_result(method, details)
    detected = [
        lang
        for lang, share in sorted(shares.items(), key=lambda item: (-item[1], item[0]))
        if share >= LANGUAGE_SHARE_THRESHOLD
    ]
    if not detected:
        return _empty_result(method, details)
    best = detected[0]
    best_details = (details or {}).get(best, {})
    return {
        "language": ", ".join(detected),
        "languages": detected,
        "shares": {lang: round(float(share), 4) for lang, share in shares.items()},
        "confidence": float(shares.get(best, 0.0)),
        "score": best_details.get("log_prob", 0.0),
        "oop": best_details.get("oop"),
        "matched": best_details.get("matched", 0),
        "distances": details or {},
        "method": method,
    }


def summarize_recognition(results: dict) -> dict:
    for key in ("neural_network", "frequent_words", "short_words"):
        payload = results.get(key) or {}
        if payload.get("languages") or payload.get("language") not in {None, "", "unknown", "не обучена"}:
            return payload
    return _empty_result("unknown")


def out_of_place_distance(profile_a: list[str], profile_b: list[str]) -> float:
    if not profile_a or not profile_b:
        return float("inf")
    pos_a = {gram: index for index, gram in enumerate(profile_a)}
    pos_b = {gram: index for index, gram in enumerate(profile_b)}
    penalty = max(len(profile_a), len(profile_b))
    total = 0
    for gram in set(pos_a) | set(pos_b):
        total += abs(pos_a.get(gram, penalty) - pos_b.get(gram, penalty))
    return float(total)


def extract_ngrams(text: str, n_min: int = N_GRAM_MIN, n_max: int = N_GRAM_MAX) -> Counter:
    source = f" {text.lower()} "
    counts: Counter = Counter()
    for n in range(n_min, n_max + 1):
        for index in range(len(source) - n + 1):
            gram = source[index:index + n]
            if any(char.isalpha() for char in gram):
                counts[gram] += 1
    return counts


def ngram_profile(texts: list[str], limit: int = 300) -> dict[str, float]:
    counts: Counter = Counter()
    for text in texts:
        counts.update(extract_ngrams(text))
    return {gram: float(freq) for gram, freq in counts.most_common(limit)}


class ShortWordsRecognizer:
    def build_profile(self, texts: list[str]) -> dict[str, float]:
        counts: Counter = Counter()
        for text in texts:
            for lemma in lexemes(text):
                if len(lemma) <= MIN_LEXEME_LEN:
                    counts[lemma] += 1
        kept = {word: freq for word, freq in counts.items() if freq > MIN_OCCURRENCES}
        if not kept:
            kept = dict(counts)
        total = sum(kept.values()) or 1
        return {word: freq / total for word, freq in kept.items()}

    def document_profile(self, text: str) -> dict[str, float]:
        counts = Counter(lemma for lemma in lexemes(text) if len(lemma) <= MIN_LEXEME_LEN)
        total = sum(counts.values()) or 1
        return {word: freq / total for word, freq in counts.items()}

    def recognize(self, text: str, profiles: dict[str, dict[str, float]]) -> dict:
        doc_lexemes = [lemma for lemma in lexemes(text) if len(lemma) <= MIN_LEXEME_LEN]
        if not doc_lexemes:
            return _empty_result("short_words")
        doc_ranked = _ranked(self.document_profile(text))
        log_scores: dict[str, float] = {}
        details: dict[str, dict] = {}
        for lang, profile in profiles.items():
            log_prob = sum(math.log(profile.get(lemma, UNSEEN_PROB)) for lemma in doc_lexemes)
            oop = out_of_place_distance(_ranked(profile), doc_ranked)
            log_scores[lang] = log_prob
            details[lang] = {
                "log_prob": log_prob,
                "oop": _finite(oop),
                "matched": sum(1 for lemma in doc_lexemes if lemma in profile),
            }
        evidence = any(item["matched"] > 0 for item in details.values())
        return _pack_result("short_words", _confidence(log_scores, len(doc_lexemes)), details, evidence)


class FrequentWordsRecognizer:
    def build_profile(self, texts: list[str]) -> dict[str, float]:
        counts: Counter = Counter()
        for text in texts:
            counts.update(lexemes(text))
        top = counts.most_common(TOP_WORDS_COUNT)
        total = sum(freq for _, freq in top) or 1
        return {word: freq / total for word, freq in top}

    def document_profile(self, text: str) -> dict[str, float]:
        counts = Counter(lexemes(text))
        top = counts.most_common(TOP_WORDS_COUNT)
        total = sum(freq for _, freq in top) or 1
        return {word: freq / total for word, freq in top}

    def recognize(self, text: str, profiles: dict[str, dict[str, float]]) -> dict:
        vocab = set().union(*profiles.values()) if profiles else set()
        doc_all = lexemes(text)
        compared = [lemma for lemma in doc_all if lemma in vocab]
        if not compared:
            return _empty_result("frequent_words")
        doc_ranked = _ranked(self.document_profile(text))
        log_scores: dict[str, float] = {}
        details: dict[str, dict] = {}
        for lang, profile in profiles.items():
            log_prob = sum(math.log(profile.get(lemma, UNSEEN_PROB)) for lemma in compared)
            oop = out_of_place_distance(_ranked(profile), doc_ranked)
            log_scores[lang] = log_prob
            details[lang] = {
                "log_prob": log_prob,
                "oop": _finite(oop),
                "matched": sum(1 for lemma in compared if lemma in profile),
            }
        evidence = any(item["matched"] > 0 for item in details.values())
        return _pack_result("frequent_words", _confidence(log_scores, len(compared)), details, evidence)


class NeuralNetworkRecognizer:
    def __init__(self):
        self.clf: MLPClassifier | None = None
        self.label_encoder: LabelEncoder | None = None
        self.feature_names: list[str] = []
        self._trained = False

    def _feature_set(self, text: str) -> set[str]:
        return {f"n{len(gram)}:{gram}" for gram in extract_ngrams(text)}

    def train(self, texts: list[str], labels: list[str]) -> None:
        document_features = [self._feature_set(text) for text in texts]
        document_frequency: Counter = Counter()
        for features in document_features:
            document_frequency.update(features)
        self.feature_names = sorted(
            name for name, freq in document_frequency.items() if freq >= MIN_NGRAM_DF
        )
        if not self.feature_names:
            self.feature_names = sorted(document_frequency)
        matrix = [[1 if name in features else 0 for name in self.feature_names] for features in document_features]

        self.label_encoder = LabelEncoder()
        encoded = self.label_encoder.fit_transform(labels)
        self.clf = MLPClassifier(
            hidden_layer_sizes=MLP_HIDDEN_LAYERS,
            activation="relu",
            solver="adam",
            max_iter=MLP_MAX_ITER,
            random_state=MLP_RANDOM_STATE,
            early_stopping=False,
        )
        self.clf.fit(matrix, encoded)
        self._trained = True

    def recognize(self, text: str) -> dict:
        if not self._trained or self.clf is None or self.label_encoder is None:
            return _empty_result("neural_network")
        features = self._feature_set(text)
        row = [[1 if name in features else 0 for name in self.feature_names]]
        predicted = self.clf.predict(row)[0]
        language = str(self.label_encoder.inverse_transform([predicted])[0])
        probabilities = self.clf.predict_proba(row)[0]
        by_label = {
            str(self.label_encoder.inverse_transform([index])[0]): float(prob)
            for index, prob in enumerate(probabilities)
        }
        shares = _script_shares(self.feature_names, features) or by_label
        packed = _pack_result("neural_network", shares, evidence=bool(shares))
        packed["probabilities"] = by_label
        if not packed["languages"] and language:
            packed["language"] = language
            packed["languages"] = [language]
            packed["confidence"] = float(max(probabilities))
        return packed

    def save(self, path: str | Path) -> None:
        if not self._trained or self.clf is None:
            return
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as handle:
            pickle.dump(
                {
                    "clf": self.clf,
                    "label_encoder": self.label_encoder,
                    "feature_names": self.feature_names,
                },
                handle,
            )

    def load(self, path: str | Path) -> bool:
        target = Path(path)
        if not target.exists():
            return False
        with target.open("rb") as handle:
            payload = pickle.load(handle)
        self.clf = payload["clf"]
        self.label_encoder = payload["label_encoder"]
        self.feature_names = payload["feature_names"]
        self._trained = True
        return True


def build_all_profiles(training_texts: dict[str, list[str]]) -> dict[str, dict]:
    short = ShortWordsRecognizer()
    frequent = FrequentWordsRecognizer()
    profiles: dict[str, dict] = {}
    for language, texts in training_texts.items():
        profiles[language] = {
            "short_words": short.build_profile(texts),
            "frequent_words": frequent.build_profile(texts),
            "ngrams": ngram_profile(texts),
        }
    return profiles


def recognize_language(text: str, profiles: dict[str, dict], nn_recognizer: NeuralNetworkRecognizer) -> dict:
    short = ShortWordsRecognizer()
    frequent = FrequentWordsRecognizer()

    reset_preprocess_cache()
    started = time.perf_counter()
    short_result = short.recognize(text, {lang: profiles[lang]["short_words"] for lang in profiles})
    short_result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)

    reset_preprocess_cache()
    started = time.perf_counter()
    frequent_result = frequent.recognize(
        text, {lang: profiles[lang]["frequent_words"] for lang in profiles}
    )
    frequent_result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)

    started = time.perf_counter()
    neural_result = nn_recognizer.recognize(text)
    neural_result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)

    ngram_doc = _ranked(ngram_profile([text]))
    ngram_distances = {
        lang: _finite(out_of_place_distance(_ranked(profiles[lang].get("ngrams", {})), ngram_doc))
        for lang in profiles
    }

    return {
        "short_words": short_result,
        "frequent_words": frequent_result,
        "neural_network": neural_result,
        "ngram_oop": ngram_distances,
    }
