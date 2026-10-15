"""Generate fictional privacy-assessment records. No real profiles or PII are used."""
import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "social_media_privacy_assessments.csv"
random.seed(42)
FIELDS = [
    "profile_id", "profile_visibility", "phone_public", "email_public",
    "birthday_public", "location_public", "workplace_public", "education_public",
    "relationship_public", "posts_public", "location_tagging", "travel_posts",
    "unknown_connections", "tag_review_enabled", "third_party_apps_reviewed",
    "mfa_enabled", "login_alerts_enabled", "password_reuse_reported",
    "suspicious_link_awareness", "old_posts_reviewed", "privacy_settings_reviewed",
    "risk_score", "risk_level"
]
def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for i in range(1, 1001):
            row = {"profile_id": f"SYN-{i:04d}"}
            for field in FIELDS[1:-2]:
                row[field] = random.choice(["yes", "no"])
            risky = [
                "profile_visibility", "phone_public", "email_public", "birthday_public",
                "location_public", "workplace_public", "education_public", "relationship_public",
                "posts_public", "location_tagging", "travel_posts", "unknown_connections",
                "password_reuse_reported"
            ]
            protective = ["tag_review_enabled", "third_party_apps_reviewed", "mfa_enabled",
                          "login_alerts_enabled", "old_posts_reviewed", "privacy_settings_reviewed"]
            score = round(100 * (
                sum(row[k] == "yes" for k in risky) / len(risky) * 0.65 +
                sum(row[k] == "no" for k in protective) / len(protective) * 0.35
            ))
            row["risk_score"] = score
            row["risk_level"] = "LOW" if score <= 20 else "MODERATE" if score <= 40 else "HIGH" if score <= 70 else "CRITICAL"
            writer.writerow(row)
    print(f"Generated 1,000 fictional records: {OUT}")
if __name__ == "__main__":
    main()
