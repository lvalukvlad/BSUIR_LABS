from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def _new_session_id() -> str:
    created = client.post("/api/sessions", json={"title": "Тестовая сессия API"})
    assert created.status_code == 200
    sid = created.json()["id"]
    client.delete("/api/dialog/history", params={"session_id": sid})
    return sid


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_sessions_list():
    r = client.get("/api/sessions")
    assert r.status_code == 200
    assert "sessions" in r.json()


def test_stats():
    r = client.get("/api/stats")
    assert r.status_code == 200
    body = r.json()
    assert "corpus_chunks" in body


def test_cannot_edit_assistant_message():
    sid = _new_session_id()
    create = client.post("/api/dialog/reply", json={"text": "Здравствуйте", "session_id": sid})
    assert create.status_code == 200
    assistant_id = create.json()["assistant_message"]["id"]
    patch = client.put(f"/api/dialog/messages/{assistant_id}", json={"content": "new"})
    assert patch.status_code == 403


def test_cannot_delete_assistant_message():
    sid = _new_session_id()
    create = client.post("/api/dialog/reply", json={"text": "Привет", "session_id": sid})
    assert create.status_code == 200
    assistant_id = create.json()["assistant_message"]["id"]
    delete = client.delete(f"/api/dialog/messages/{assistant_id}")
    assert delete.status_code == 403


def test_edit_user_message_regenerates_assistant():
    sid = _new_session_id()
    created = client.post("/api/dialog/reply", json={"text": "Что такое ОРВИ?", "session_id": sid})
    assert created.status_code == 200
    user_id = created.json()["user_message"]["id"]
    assistant_before = created.json()["assistant_message"]["content"]

    edited = client.put(
        f"/api/dialog/messages/{user_id}",
        json={"content": "Что такое СПИД?"},
    )
    assert edited.status_code == 200

    history = client.get("/api/dialog/history", params={"session_id": sid})
    assert history.status_code == 200
    msgs = history.json()["messages"]
    idx = next(i for i, m in enumerate(msgs) if m["id"] == user_id)
    assert idx + 1 < len(msgs)
    assert msgs[idx + 1]["role"] == "assistant"
    assert msgs[idx + 1]["content"] != assistant_before


def test_edit_user_message_in_middle_trims_tail_and_keeps_versions():
    sid = _new_session_id()
    first = client.post("/api/dialog/reply", json={"text": "Что такое ОРВИ?", "session_id": sid})
    second = client.post("/api/dialog/reply", json={"text": "А что делать дальше?", "session_id": sid})
    assert first.status_code == 200
    assert second.status_code == 200
    first_user_id = first.json()["user_message"]["id"]

    edited = client.put(f"/api/dialog/messages/{first_user_id}", json={"content": "Что такое СПИД?"})
    assert edited.status_code == 200

    history = client.get("/api/dialog/history", params={"session_id": sid})
    assert history.status_code == 200
    msgs = history.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["id"] == first_user_id
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert msgs[0].get("versions")
    assert msgs[0]["versions"][0]["user"] == "Что такое ОРВИ?"


def test_edit_user_message_rejects_blank_content():
    sid = _new_session_id()
    created = client.post("/api/dialog/reply", json={"text": "Привет", "session_id": sid})
    assert created.status_code == 200
    user_id = created.json()["user_message"]["id"]
    edited = client.put(f"/api/dialog/messages/{user_id}", json={"content": "    "})
    assert edited.status_code == 400


def test_delete_user_message_keeps_other_chat_messages():
    sid = _new_session_id()
    first = client.post("/api/dialog/reply", json={"text": "Что такое ОРВИ?", "session_id": sid})
    second = client.post("/api/dialog/reply", json={"text": "Что такое ВИЧ?", "session_id": sid})
    assert first.status_code == 200
    assert second.status_code == 200

    first_user_id = first.json()["user_message"]["id"]
    first_assistant_id = first.json()["assistant_message"]["id"]
    second_user_id = second.json()["user_message"]["id"]
    second_assistant_id = second.json()["assistant_message"]["id"]

    deleted = client.delete(f"/api/dialog/messages/{first_user_id}")
    assert deleted.status_code == 200

    history = client.get("/api/dialog/history", params={"session_id": sid})
    assert history.status_code == 200
    ids = [m["id"] for m in history.json()["messages"]]
    assert first_user_id not in ids
    assert first_assistant_id not in ids
    assert second_user_id in ids
    assert second_assistant_id in ids
