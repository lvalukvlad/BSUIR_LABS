import math
import re
from collections import Counter

from .config import KEYWORD_LIMIT, PHRASE_MIN_COUNT, SUMMARY_SENTENCES
from .text_processing import tokenize

SENT_RE = re.compile(r"(?<=[.!?])\s+")


def split_paragraphs(text):
    out = []
    pos = 0
    for chunk in re.split(r"\n\s*\n", text):
        i = text.find(chunk, pos)
        if i < 0:
            i = pos
        s = chunk.strip()
        if s:
            pad = len(chunk) - len(chunk.lstrip())
            out.append((i + pad, s))
        pos = i + len(chunk)
    return out


def split_sentences(paragraph, base):
    out = []
    pos = 0
    for part in SENT_RE.split(paragraph):
        i = paragraph.find(part, pos)
        if i < 0:
            i = pos
        s = part.strip()
        if s:
            pad = len(part) - len(part.lstrip())
            out.append((base + i + pad, s))
        pos = i + len(part)
    return out


def parse_document(text, lang):
    sents = []
    for p_start, p in split_paragraphs(text):
        plen = max(len(p), 1)
        for start, sent in split_sentences(p, p_start):
            toks = tokenize(sent, lang)
            sents.append({
                "text": sent,
                "start": start,
                "para_start": p_start,
                "para_len": plen,
                "tokens": toks,
                "tf": Counter(toks),
            })
    tf = Counter()
    for s in sents:
        tf.update(s["tf"])
    return {
        "char_len": max(len(text), 1),
        "sentences": sents,
        "tf": tf,
        "vocabulary": set(tf),
    }


def idf(n, df):
    if df <= 0 or n <= 0:
        return 0.0
    return math.log(n / df)


def term_w(t, tf, tfmax, n, df):
    return 0.5 * (1.0 + tf[t] / tfmax) * idf(n, df.get(t, 1))


def summarize(text, lang, title, domain, n, df):
    doc = parse_document(text, lang)
    tf = doc["tf"]
    tfmax = max(tf.values()) if tf else 1
    L = doc["char_len"]
    sents = doc["sentences"]

    scored = []
    for i, s in enumerate(sents):
        sc = 0.0
        for t, c in s["tf"].items():
            sc += c * term_w(t, tf, tfmax, n, df)
        posd = max(1.0 - s["start"] / L, 0.0)
        posp = max(1.0 - (s["start"] - s["para_start"]) / s["para_len"], 0.0)
        w = posd * posp * sc
        scored.append({
            "index": i,
            "text": s["text"],
            "tokens": s["tokens"],
            "posd": round(posd, 4),
            "posp": round(posp, 4),
            "score": round(sc, 4),
            "weight": round(w, 4),
        })

    ranked = sorted(scored, key=lambda x: x["weight"], reverse=True)
    picked = []
    for x in ranked:
        if x["weight"] > 0:
            picked.append(x["index"])
        if len(picked) == SUMMARY_SENTENCES:
            break
    if not picked:
        picked = [x["index"] for x in scored[:SUMMARY_SENTENCES]]
    picked.sort()
    base_ids = list(range(min(SUMMARY_SENTENCES, len(scored))))
    pick_set = set(picked)
    base_set = set(base_ids)

    rows = []
    for x in scored:
        rows.append({
            "index": x["index"],
            "text": x["text"],
            "posd": x["posd"],
            "posp": x["posp"],
            "score": x["score"],
            "weight": x["weight"],
            "selected": x["index"] in pick_set,
            "baseline": x["index"] in base_set,
        })

    classic = " ".join(sents[i]["text"] for i in picked)
    baseline = " ".join(sents[i]["text"] for i in base_ids)
    kws, net = build_keywords(doc, title, domain, n, df)

    terms = []
    for t, c in tf.most_common(40):
        terms.append({
            "term": t,
            "tf": c,
            "weight": round(c * idf(n, df.get(t, 1)), 4),
        })

    return {
        "classic": classic,
        "baseline": baseline,
        "keywords": kws,
        "network": net,
        "selected": picked,
        "baseline_selected": base_ids,
        "sentences": rows,
        "terms": terms,
        "char_len": doc["char_len"],
        "vocabulary": doc["vocabulary"],
    }


def build_keywords(doc, title, domain, n, df):
    tf = doc["tf"]
    weighted = []
    for t, c in tf.items():
        w = c * idf(n, df.get(t, 1))
        if w > 0:
            weighted.append((t, w))
    weighted.sort(key=lambda x: x[1], reverse=True)
    top = weighted[:KEYWORD_LIMIT]

    nodes = {}
    for t, w in top:
        nodes[t] = {"term": t, "weight": round(w, 4), "children": []}
    top_set = set(nodes)

    phrases = Counter()
    how = {}
    together = Counter()
    for s in doc["sentences"]:
        toks = s["tokens"]
        here = [t for t in top_set if t in toks]
        for a, b in zip(here, here[1:]):
            if a != b:
                together[tuple(sorted((a, b)))] += 1
        for a, b in zip(toks, toks[1:]):
            key = (a, b)
            phrases[key] += 1
            if key not in how:
                how[key] = f"{a} {b}"

    for key, cnt in phrases.items():
        if cnt < PHRASE_MIN_COUNT:
            continue
        a, b = key
        child = {
            "term": how[key],
            "weight": round(nodes.get(a, {}).get("weight", 0) + nodes.get(b, {}).get("weight", 0), 4),
            "children": [],
        }
        head = None
        if b in nodes:
            head = b
        elif a in nodes:
            head = a
        if head and len(nodes[head]["children"]) < 4:
            nodes[head]["children"].append(child)

    tree = sorted(nodes.values(), key=lambda x: x["weight"], reverse=True)
    root = title or "документ"
    area = domain or "предметная_область"
    net = [{"source": root, "relation": "относится_к", "target": area}]
    for node in tree:
        net.append({"source": root, "relation": "ключевое_понятие", "target": node["term"]})
        net.append({"source": node["term"], "relation": "принадлежит", "target": area})
        for ch in node["children"]:
            net.append({"source": node["term"], "relation": "включает", "target": ch["term"]})
    for (a, b), cnt in together.most_common(8):
        if cnt >= 1:
            net.append({"source": a, "relation": "совстречается_с", "target": b})
    return tree, net
