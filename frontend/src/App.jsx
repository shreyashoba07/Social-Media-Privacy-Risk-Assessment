import { useEffect, useMemo, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const API = "http://127.0.0.1:8000";
const choices = [
  { value: "yes", label: "Yes" },
  { value: "no", label: "No" },
  { value: "sometimes", label: "Sometimes" },
  { value: "not sure", label: "Not sure" }
];

export default function App() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [sim, setSim] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/questions`).then(r => {
      if (!r.ok) throw new Error("Could not load questionnaire");
      return r.json();
    }).then(d => {
      setQuestions(d.questions);
      setAnswers(Object.fromEntries(d.questions.map(q => [q.id, "no"])));
    }).catch(() => setError("Backend is not running yet. Start the FastAPI server on port 8000, then refresh this page."));
  }, []);

  const grouped = useMemo(() => questions.reduce((acc, q) => {
    (acc[q.category] ||= []).push(q);
    return acc;
  }, {}), [questions]);

  async function analyze(e) {
    e?.preventDefault();
    setBusy(true); setError(""); setSim(null);
    try {
      const response = await fetch(`${API}/api/assessment`, {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({answers})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Assessment failed");
      setResult(data);
      document.getElementById("results")?.scrollIntoView({behavior:"smooth"});
    } catch (err) { setError(err.message || "Could not connect to backend."); }
    finally { setBusy(false); }
  }

  async function simulate() {
    if (!result) return;
    const improvements = result.findings.map(f => f.question_id);
    try {
      const response = await fetch(`${API}/api/assessment/simulate-improvement`, {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({answers, improvements})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Simulation failed");
      setSim(data);
    } catch (err) { setError(err.message || "Simulation failed."); }
  }

  function useDemo() {
    const risky = ["profile_public","phone_public","birthday_public","real_time_location","travel_public",
      "unknown_connections","tag_review_off","mfa_disabled","login_alerts_off","apps_unreviewed",
      "old_posts","privacy_review","password_reuse","suspicious_links"];
    setAnswers(prev => Object.fromEntries(Object.keys(prev).map(k => [k, risky.includes(k) ? "yes" : "no"])));
    setResult(null); setSim(null);
    window.scrollTo({top:0, behavior:"smooth"});
  }

  function downloadReport() {
    if (!result) return;
    const report = {
      report_title: "Social Media Privacy Risk Assessment",
      assessment_date: new Date().toISOString(),
      overall_score: result.overall_score,
      risk_level: result.risk_level,
      category_scores: result.category_scores,
      findings: result.findings,
      disclaimer: result.disclaimer
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], {type:"application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "privacy-assessment-report.json"; a.click();
    URL.revokeObjectURL(url);
  }

  const chartData = result ? Object.entries(result.category_scores).map(([category, score]) => ({
    category: category.replace("Messaging & Social Engineering", "Social Engineering")
      .replace("Friends / Followers", "Connections").replace("Personal Information", "Personal Info")
      .replace("Third-Party Apps", "Third-Party Apps"), score
  })) : [];

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand-mark">PG</div>
      <div className="brand-copy"><strong>PrivacyGuard</strong><span>PERSONAL PRIVACY AWARENESS</span></div>
      <div className="top-tag">DEFENSIVE CYBERSECURITY</div>
    </header>

    <main className="container">
      <section className="hero">
        <div className="eyebrow"><span className="pulse"/> PRIVACY RISK ASSESSMENT FRAMEWORK</div>
        <h1>Your digital footprint.<br/><em>Your control.</em></h1>
        <p>Understand your social-media exposure, identify risky settings, and get practical steps to strengthen your privacy.</p>
        <div className="hero-actions">
          <a className="primary-btn" href="#assessment">Start privacy assessment <span>↘</span></a>
          <button className="secondary-btn" onClick={useDemo}>Load fictional demo</button>
        </div>
        <div className="trust-row"><span>✓ No scraping</span><span>✓ No passwords or actual PII</span><span>✓ Explainable scoring</span></div>
      </section>

      <section className="stat-grid">
        <article className="stat-card"><span className="stat-icon">◈</span><div><small>ASSESSMENT AREAS</small><strong>10</strong><span>Privacy & security categories</span></div></article>
        <article className="stat-card"><span className="stat-icon">☷</span><div><small>SELF-CHECK QUESTIONS</small><strong>{questions.length || "40+"}</strong><span>Settings, not sensitive values</span></div></article>
        <article className="stat-card"><span className="stat-icon">◎</span><div><small>RISK SCALE</small><strong>0–100</strong><span>Higher means more exposure</span></div></article>
      </section>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <section className="section-heading" id="assessment">
        <div><div className="eyebrow">01 / SELF-ASSESSMENT</div><h2>Review your privacy settings</h2><p>Choose the answer that best describes your current practice. No account details are requested.</p></div>
        <span className="section-pill">40+ QUESTIONS</span>
      </section>

      <form onSubmit={analyze} className="assessment-layout">
        <div className="questionnaire">
          {Object.entries(grouped).map(([category, qs], index) => <section className="question-card" key={category}>
            <div className="category-heading"><span className="category-number">{String(index+1).padStart(2,"0")}</span><div><h3>{category}</h3><span>{qs.length} questions</span></div></div>
            {qs.map((q, i) => <div className="question-row" key={q.id}>
              <div className="question-text"><span>{i+1}.</span>{q.text}</div>
              <div className="answer-options">{choices.map(c => <label className={`answer-choice ${answers[q.id] === c.value ? "selected":""}`} key={c.value}>
                <input type="radio" name={q.id} value={c.value} checked={answers[q.id] === c.value} onChange={() => setAnswers(p => ({...p,[q.id]:c.value}))}/>{c.label}
              </label>)}</div>
            </div>)}
          </section>)}
          <button className="primary-btn submit-btn" type="submit" disabled={busy || !questions.length}>{busy ? "Assessing…" : "Analyze my privacy risk"} <span>→</span></button>
        </div>
        <aside className="side-note">
          <div className="shield">◇</div><h3>Privacy by design</h3>
          <p>This tool never needs your actual phone number, email, address, date of birth, password, or private messages.</p>
          <ul><li>Self-reported settings only</li><li>Transparent rule-based scoring</li><li>Recommendations you can act on</li><li>Educational demo, no account access</li></ul>
          <div className="side-warning"><strong>Remember</strong><p>A score is a coaching signal, not a guarantee that an account is safe or compromised.</p></div>
        </aside>
      </form>

      {result && <section className="results-section" id="results">
        <div className="section-heading"><div><div className="eyebrow">02 / ASSESSMENT RESULTS</div><h2>Your privacy overview</h2><p>Use these findings to decide which settings to review first.</p></div><button className="secondary-btn" onClick={downloadReport}>Export report ↓</button></div>
        <div className="result-top">
          <article className="score-card"><div className="score-label">OVERALL PRIVACY RISK</div><div className="score-line"><strong>{result.overall_score}</strong><span>/100</span></div><div className="score-track"><div style={{width:`${result.overall_score}%`}}/></div><span className={`risk-badge ${result.risk_level.toLowerCase()}`}>{result.risk_level} RISK</span><p>Higher score = more assessed exposure</p></article>
          <article className="summary-card"><div className="summary-number">{result.findings.length}</div><div><h3>Items to review</h3><p>Potential privacy weaknesses identified from your answers.</p></div><div className="summary-divider"/><div className="summary-number">{result.high_risk_categories.length}</div><div><h3>Higher-risk categories</h3><p>Categories with a score of 60 or above.</p></div></article>
        </div>
        <article className="panel chart-panel"><div className="panel-title"><div><h3>Category risk scores</h3><p>All scores use the same 0–100 scale.</p></div><span className="mini-legend"><i/> Assessed risk</span></div>
          <div className="chart-wrap"><ResponsiveContainer width="100%" height={330}><BarChart data={chartData} margin={{top:10,right:12,bottom:60,left:0}}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8edf4"/><XAxis dataKey="category" angle={-28} textAnchor="end" interval={0} height={78} tick={{fontSize:11,fill:"#667085"}}/><YAxis domain={[0,100]} tick={{fontSize:11,fill:"#667085"}}/><Tooltip/><Bar dataKey="score" name="Risk score" fill="#6b8afd" radius={[6,6,0,0]}/></BarChart></ResponsiveContainer></div>
        </article>
        <div className="section-heading compact"><div><div className="eyebrow">03 / ACTION PLAN</div><h2>Findings & recommendations</h2></div></div>
        <div className="findings-list">{result.findings.length ? result.findings.map((f,i)=><article className="finding-card" key={f.question_id}><span className={`priority-dot ${f.priority.toLowerCase().replace(" ","-")}`}/><div className="finding-content"><div className="finding-meta"><span>{f.category}</span><b>{f.priority}</b></div><h3>{f.finding}</h3><p>{f.recommendation}</p></div></article>) : <div className="empty-state">No high-exposure answers were reported. Keep reviewing your settings periodically.</div>}</div>
        <article className="panel simulator"><div><div className="eyebrow">04 / WHAT-IF SIMULATOR</div><h2>Imagine safer settings</h2><p>Simulate switching the flagged answers to “No”. This changes only the local assessment calculation; it does not change any social-media account settings.</p></div><button className="primary-btn" onClick={simulate}>Simulate improvements <span>↗</span></button>
          {sim && <div className="simulation-result"><div><small>CURRENT</small><strong>{sim.before.overall_score}/100</strong><span>{sim.before.risk_level}</span></div><div className="sim-arrow">→</div><div><small>SIMULATED</small><strong>{sim.after.overall_score}/100</strong><span>{sim.after.risk_level}</span></div><div className="reduction"><small>RISK REDUCTION</small><strong>{sim.risk_reduction} points</strong></div><p>Simulation only—not a guarantee of real-world safety.</p></div>}
        </article>
        <p className="disclaimer">{result.disclaimer}</p>
      </section>}
      <footer><div className="footer-brand">PrivacyGuard <span>· Student cybersecurity project</span></div><p>Built for defensive privacy education. Synthetic and self-reported data only.</p></footer>
    </main>
  </div>;
}
