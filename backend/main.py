from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Social Media Privacy Risk Assessment API",
    description="Defensive educational assessment using self-reported settings only.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# A "risk" answer means more exposure. Questions intentionally ask about settings,
# not the actual sensitive values (phone number, address, password, etc.).
QUESTIONS = [
    {"id":"profile_public","category":"Profile Visibility","text":"Is your profile visible to the public?","kind":"yes_risk"},
    {"id":"search_engine","category":"Profile Visibility","text":"Can search engines show your profile?","kind":"yes_risk"},
    {"id":"followers_public","category":"Profile Visibility","text":"Can anyone view your followers/friends list?","kind":"yes_risk"},
    {"id":"discoverable","category":"Profile Visibility","text":"Can strangers find you using your phone/email lookup setting?","kind":"yes_risk"},
    {"id":"phone_public","category":"Personal Information","text":"Is your phone number publicly visible?","kind":"yes_risk"},
    {"id":"email_public","category":"Personal Information","text":"Is your personal email publicly visible?","kind":"yes_risk"},
    {"id":"birthday_public","category":"Personal Information","text":"Is your full birth date publicly visible?","kind":"yes_risk"},
    {"id":"home_info","category":"Personal Information","text":"Do public posts reveal home-related details?","kind":"yes_risk"},
    {"id":"workplace_public","category":"Personal Information","text":"Is your workplace or organization publicly visible?","kind":"yes_risk"},
    {"id":"education_public","category":"Personal Information","text":"Is your school/college publicly visible?","kind":"yes_risk"},
    {"id":"family_public","category":"Personal Information","text":"Are family or relationship details publicly visible?","kind":"yes_risk"},
    {"id":"real_time_location","category":"Location Privacy","text":"Do you share your current location in real time?","kind":"yes_risk"},
    {"id":"geotagging","category":"Location Privacy","text":"Do you leave geotags enabled on posts/photos?","kind":"yes_risk"},
    {"id":"checkins","category":"Location Privacy","text":"Do you publish frequent location check-ins?","kind":"yes_risk"},
    {"id":"travel_public","category":"Location Privacy","text":"Do you post travel plans before or during a trip?","kind":"yes_risk"},
    {"id":"routine_public","category":"Location Privacy","text":"Do public posts reveal recurring routes or routines?","kind":"yes_risk"},
    {"id":"posts_public","category":"Posts & Content","text":"Are most of your posts visible to everyone?","kind":"yes_risk"},
    {"id":"screens_documents","category":"Posts & Content","text":"Could photos expose badges, documents, screens, or vehicle details?","kind":"yes_risk"},
    {"id":"child_images","category":"Posts & Content","text":"Do public posts include children or other people who may not have consented?","kind":"yes_risk"},
    {"id":"old_posts","category":"Posts & Content","text":"Have you not reviewed old public posts in the last year?","kind":"yes_risk"},
    {"id":"unknown_connections","category":"Friends / Followers","text":"Do you often accept requests from people you do not know?","kind":"yes_risk"},
    {"id":"followers_review","category":"Friends / Followers","text":"Have you not reviewed your followers/friends list recently?","kind":"yes_risk"},
    {"id":"unknown_dms","category":"Friends / Followers","text":"Can unknown users contact you without meaningful restrictions?","kind":"yes_risk"},
    {"id":"tag_anyone","category":"Tagging & Mentions","text":"Can anyone tag or mention you without approval?","kind":"yes_risk"},
    {"id":"tag_review_off","category":"Tagging & Mentions","text":"Is tag/post review disabled?","kind":"yes_risk"},
    {"id":"tagged_auto","category":"Tagging & Mentions","text":"Can tagged posts appear on your profile automatically?","kind":"yes_risk"},
    {"id":"mfa_disabled","category":"Account Security","text":"Is multi-factor authentication (MFA) disabled?","kind":"yes_risk"},
    {"id":"password_reuse","category":"Account Security","text":"Do you reuse passwords across accounts? (Do not enter any password.)","kind":"yes_risk"},
    {"id":"login_alerts_off","category":"Account Security","text":"Are login/security alerts disabled where available?","kind":"yes_risk"},
    {"id":"sessions_unreviewed","category":"Account Security","text":"Have you not reviewed active sessions or unknown devices recently?","kind":"yes_risk"},
    {"id":"recovery_unreviewed","category":"Account Security","text":"Have you not checked account recovery options recently?","kind":"yes_risk"},
    {"id":"apps_unreviewed","category":"Third-Party Apps","text":"Have you not reviewed connected third-party apps recently?","kind":"yes_risk"},
    {"id":"unused_apps","category":"Third-Party Apps","text":"Do unused apps still have account access?","kind":"yes_risk"},
    {"id":"excess_permissions","category":"Third-Party Apps","text":"Have you granted app permissions without checking whether they are needed?","kind":"yes_risk"},
    {"id":"suspicious_links","category":"Messaging & Social Engineering","text":"Might you click unexpected links before verifying the sender?","kind":"yes_risk"},
    {"id":"verification_codes","category":"Messaging & Social Engineering","text":"Are you unsure that verification codes should never be shared with others?","kind":"yes_risk"},
    {"id":"impersonation","category":"Messaging & Social Engineering","text":"Do you accept claims from familiar-looking accounts without verification?","kind":"yes_risk"},
    {"id":"giveaways","category":"Messaging & Social Engineering","text":"Do you interact with giveaways that request unusual personal information?","kind":"yes_risk"},
    {"id":"metadata_awareness","category":"Digital Footprint","text":"Are you unfamiliar with photo metadata (such as EXIF timestamps/location)?","kind":"yes_risk"},
    {"id":"old_accounts","category":"Digital Footprint","text":"Do unused/old accounts remain active and unreviewed?","kind":"yes_risk"},
    {"id":"public_comments","category":"Digital Footprint","text":"Do you rarely review old public comments or profile history?","kind":"yes_risk"},
    {"id":"privacy_review","category":"Digital Footprint","text":"Do you rarely review privacy settings?","kind":"yes_risk"},
]
CATEGORIES = [
    "Profile Visibility", "Personal Information", "Location Privacy", "Posts & Content",
    "Friends / Followers", "Tagging & Mentions", "Account Security", "Third-Party Apps",
    "Messaging & Social Engineering", "Digital Footprint"
]
WEIGHTS = {
    "Profile Visibility": 10, "Personal Information": 15, "Location Privacy": 15,
    "Posts & Content": 10, "Friends / Followers": 10, "Tagging & Mentions": 5,
    "Account Security": 15, "Third-Party Apps": 5,
    "Messaging & Social Engineering": 10, "Digital Footprint": 5
}
RECOMMENDATIONS = {
    "profile_public": ("IMPORTANT", "Limit profile visibility and search-engine discovery to what you intentionally share."),
    "phone_public": ("IMMEDIATE", "Hide phone-number visibility where the platform allows it; do not enter the number into this tool."),
    "email_public": ("IMPORTANT", "Remove personal email from public profile fields; consider a contact form or separate public-facing address."),
    "birthday_public": ("IMPORTANT", "Hide your full birth date or show only the minimum information you choose."),
    "real_time_location": ("IMMEDIATE", "Avoid broadcasting real-time location; consider posting after leaving."),
    "geotagging": ("IMPORTANT", "Review geotagging settings and remove location metadata from sensitive images before sharing."),
    "travel_public": ("IMMEDIATE", "Avoid public travel announcements while away from home."),
    "unknown_connections": ("IMPORTANT", "Verify unfamiliar profiles before accepting connection requests."),
    "tag_review_off": ("IMPORTANT", "Enable tag review or approval where supported."),
    "mfa_disabled": ("IMMEDIATE", "Enable multi-factor authentication using the strongest supported method."),
    "password_reuse": ("IMMEDIATE", "Use unique passwords for each account and consider a reputable password manager."),
    "login_alerts_off": ("IMPORTANT", "Enable sign-in alerts where available."),
    "apps_unreviewed": ("IMPORTANT", "Review connected apps and revoke access that is unused or unnecessary."),
    "unused_apps": ("IMPORTANT", "Remove unused integrations and follow the principle of least privilege."),
    "suspicious_links": ("IMMEDIATE", "Verify unexpected links through a separate trusted channel before opening them."),
    "verification_codes": ("IMMEDIATE", "Never share one-time verification codes with another person."),
    "metadata_awareness": ("GOOD PRACTICE", "Learn how EXIF metadata can contain device, timestamp, or location details; review before sharing."),
    "old_posts": ("GOOD PRACTICE", "Review older public posts and change audience or remove content you no longer want public."),
    "privacy_review": ("GOOD PRACTICE", "Schedule a periodic privacy-settings review.")
}

class AssessmentRequest(BaseModel):
    answers: dict[str, Any] = Field(..., description="Question ID to Yes/No/Sometimes/Not sure")

class SimulationRequest(BaseModel):
    answers: dict[str, Any]
    improvements: list[str] = Field(default_factory=list)

def risk_answer(value: Any) -> float:
    """Convert a self-reported response to an exposure contribution from 0 to 1."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    normalized = str(value).strip().lower()
    return {"yes": 1.0, "often": 1.0, "public": 1.0,
            "sometimes": 0.5, "not sure": 0.5, "friends": 0.5,
            "no": 0.0, "never": 0.0, "private": 0.0}.get(normalized, 0.0)

def assess(answers: dict[str, Any]) -> dict[str, Any]:
    known_ids = {q["id"] for q in QUESTIONS}
    unknown = set(answers) - known_ids
    if unknown:
        raise ValueError(f"Unknown question IDs: {', '.join(sorted(unknown))}")
    category_scores = {}
    for category in CATEGORIES:
        qs = [q for q in QUESTIONS if q["category"] == category]
        if not qs:
            category_scores[category] = 0
            continue
        points = [risk_answer(answers.get(q["id"], "no")) for q in qs]
        category_scores[category] = round(sum(points) / len(qs) * 100)
    # Configurable category weights sum to 100; weighted mean keeps score in 0..100.
    overall = round(sum(category_scores[c] * WEIGHTS[c] for c in CATEGORIES) / sum(WEIGHTS.values()))
    if overall <= 20: level = "LOW"
    elif overall <= 40: level = "MODERATE"
    elif overall <= 70: level = "HIGH"
    else: level = "CRITICAL"
    findings = []
    for q in QUESTIONS:
        if risk_answer(answers.get(q["id"], "no")) > 0:
            priority, fix = RECOMMENDATIONS.get(
                q["id"], ("GOOD PRACTICE", "Review this setting and limit exposure to the minimum necessary.")
            )
            findings.append({
                "question_id": q["id"], "category": q["category"],
                "finding": q["text"], "priority": priority, "recommendation": fix
            })
    findings.sort(key=lambda f: {"IMMEDIATE":0, "IMPORTANT":1, "GOOD PRACTICE":2}[f["priority"]])
    return {
        "overall_score": overall, "risk_level": level,
        "category_scores": category_scores,
        "high_risk_categories": [c for c, s in category_scores.items() if s >= 60],
        "findings": findings,
        "recommendations": findings[:10],
        "disclaimer": "Educational self-assessment only. Scores are based on assumed weights and do not predict or guarantee compromise."
    }

@app.get("/")
def root():
    return {"message": "Social Media Privacy Risk Assessment API is running", "docs": "/docs"}

@app.get("/api/questions")
def get_questions():
    return {"categories": CATEGORIES, "questions": QUESTIONS}

@app.post("/api/assessment")
def create_assessment(payload: AssessmentRequest):
    try:
        return assess(payload.answers)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/api/assessment/simulate-improvement")
def simulate_improvement(payload: SimulationRequest):
    try:
        before = assess(payload.answers)
        improved = dict(payload.answers)
        known_ids = {q["id"] for q in QUESTIONS}
        invalid = set(payload.improvements) - known_ids
        if invalid:
            raise ValueError(f"Unknown improvement IDs: {', '.join(sorted(invalid))}")
        for question_id in payload.improvements:
            improved[question_id] = "no"
        after = assess(improved)
        return {"before": before, "after": after,
                "risk_reduction": max(0, before["overall_score"] - after["overall_score"]),
                "simulated_only": True}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/api/privacy-checklist")
def checklist():
    return {"items": [
        "Review profile visibility and search-engine discovery",
        "Hide unnecessary contact information and full birth date",
        "Review location sharing and avoid real-time travel posts",
        "Review tagging permissions and follower lists",
        "Verify unfamiliar connection requests",
        "Enable MFA and login alerts where available",
        "Review active sessions and recovery options",
        "Revoke unused third-party application access",
        "Review older public posts and comments",
        "Never share passwords or verification codes",
        "Review privacy settings periodically"
    ]}
