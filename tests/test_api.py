from fastapi.testclient import TestClient
from backend.main import app, QUESTIONS, assess

client = TestClient(app)

def test_root_is_running():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"].lower()

def test_questionnaire_has_at_least_40_questions():
    assert len(QUESTIONS) >= 40
    assert len({q["id"] for q in QUESTIONS}) == len(QUESTIONS)

def test_all_no_answers_produce_low_risk():
    answers = {q["id"]: "no" for q in QUESTIONS}
    result = assess(answers)
    assert result["overall_score"] == 0
    assert result["risk_level"] == "LOW"
    assert result["findings"] == []

def test_all_yes_answers_produce_critical_risk():
    answers = {q["id"]: "yes" for q in QUESTIONS}
    result = assess(answers)
    assert result["overall_score"] == 100
    assert result["risk_level"] == "CRITICAL"
    assert len(result["findings"]) == len(QUESTIONS)

def test_scores_are_bounded():
    result = assess({"phone_public": "yes", "mfa_disabled": "sometimes"})
    assert 0 <= result["overall_score"] <= 100
    assert all(0 <= score <= 100 for score in result["category_scores"].values())

def test_unknown_question_rejected_by_api():
    response = client.post("/api/assessment", json={"answers":{"not_a_question":"yes"}})
    assert response.status_code == 422

def test_assessment_endpoint():
    response = client.post("/api/assessment", json={"answers":{"phone_public":"yes","mfa_disabled":"yes"}})
    assert response.status_code == 200
    body = response.json()
    assert "overall_score" in body
    assert "category_scores" in body
    assert body["findings"]

def test_improvement_simulation_does_not_increase_score():
    response = client.post("/api/assessment/simulate-improvement", json={
        "answers":{"phone_public":"yes","mfa_disabled":"yes"},
        "improvements":["phone_public","mfa_disabled"]
    })
    assert response.status_code == 200
    body = response.json()
    assert body["after"]["overall_score"] <= body["before"]["overall_score"]
    assert body["simulated_only"] is True

def test_privacy_checklist_available():
    response = client.get("/api/privacy-checklist")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 10
