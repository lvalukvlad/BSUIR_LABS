import time, random, requests

BASE = "http://127.0.0.1:8000"
WORDS = ["дом","стол","книга","рука","голова","время","человек","день","жизнь","слово"]

def benchmark(n):
    text = " ".join(random.choices(WORDS, k=n)) + "."
    with open(f"/tmp/bench_{n}.txt","w",encoding="utf-8") as f: f.write(text)
    start = time.time()
    with open(f"/tmp/bench_{n}.txt","rb") as f:
        r = requests.post(f"{BASE}/api/analyze", files={"file": f})
    ms = (time.time()-start)*1000
    data = r.json()
    print(f"{n:5d} слов | {ms:7.1f} мс | {data['unique_lemmas']:4d} лемм | {ms/n*1000:5.2f} мкс/слово")

if __name__ == "__main__":
    print("Быстродействие анализа текста:")
    print("Слов  | Время  | Леммы | Мкс/слово")
    print("-"*45)
    for n in [100, 500, 1000]: benchmark(n)