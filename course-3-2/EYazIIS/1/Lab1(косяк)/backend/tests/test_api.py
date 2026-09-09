import requests

BASE = "http://127.0.0.1:8000"

def test_health():
    r = requests.get(f"{BASE}/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_analyze_txt():
    with open("/tmp/test.txt", "w", encoding="utf-8") as f:
        f.write("Дом дома дому.")
    with open("/tmp/test.txt", "rb") as f:
        r = requests.post(f"{BASE}/api/analyze", files={"file": f})
    assert r.status_code == 200
    data = r.json()
    assert data["unique_lemmas"] >= 1
    assert "lemmas" in data

def test_generate():
    r = requests.post(f"{BASE}/api/generate", json={
        "lemma": "дом",
        "grammemes": {"падеж": "предложный", "число": "ед"}
    })
    assert r.status_code == 200
    assert r.json()["form"] == "доме"

if __name__ == "__main__":
    test_health(); print("✓ health")
    test_analyze_txt(); print("✓ analyze")
    test_generate(); print("✓ generate")
    print("\nВсе тесты пройдены!")