
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="INELSO Service 26 — Adaptive Practice Dashboard",
    page_icon="📈",
    layout="wide"
)

RUBRIC = pd.DataFrame([
    {"criterion": "RC-01", "name": "Εννοιολογική ακρίβεια", "weight": 30},
    {"criterion": "RC-02", "name": "Μέθοδος / συλλογισμός", "weight": 25},
    {"criterion": "RC-03", "name": "Τεκμηρίωση / υποστήριξη", "weight": 15},
    {"criterion": "RC-04", "name": "Πληρότητα", "weight": 15},
    {"criterion": "RC-05", "name": "Σαφήνεια / επικοινωνία", "weight": 15},
])

attempts = pd.DataFrame([
    {
        "attempt": 1,
        "RC-01": 3, "RC-02": 2, "RC-03": 2, "RC-04": 2, "RC-05": 3,
        "score": 61.25,
        "mastery": "Developing",
        "confidence": 0.65,
        "status": "ESCALATE",
        "action": "Ανθρώπινος έλεγχος και νέα προσπάθεια μετά από στοχευμένη ανατροφοδότηση."
    },
    {
        "attempt": 2,
        "RC-01": 4, "RC-02": 4, "RC-03": 4, "RC-04": 4, "RC-05": 4,
        "score": 100.00,
        "mastery": "Mastery",
        "confidence": 0.85,
        "status": "READY",
        "action": "Δεν απαιτείται νέα προσπάθεια για αυτή τη δραστηριότητα."
    },
])

LEVEL_LABELS = {0:"Level 0",1:"Level 1",2:"Level 2",3:"Level 3",4:"Level 4"}

def critical_rule_text(row):
    if row["RC-01"] <= 1:
        return "Ενεργοποιείται ο κρίσιμος κανόνας: RC-01 σε Level 0–1 δεν επιτρέπει mastery πάνω από Developing."
    return "Δεν ενεργοποιείται ο κρίσιμος κανόνας RC-01."

def html_report(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    gain = latest["score"] - prev["score"]

    attempt_rows = ""
    for _, r in df.iterrows():
        attempt_rows += f"<tr><td>{int(r['attempt'])}</td><td>{r['score']:.2f}</td><td>{r['mastery']}</td><td>{r['confidence']:.2f}</td><td>{r['status']}</td><td>{r['action']}</td></tr>"

    rubric_rows = ""
    for _, rr in RUBRIC.iterrows():
        code = rr["criterion"]
        rubric_rows += f"<tr><td>{code}</td><td>{rr['name']}</td><td>{rr['weight']}%</td><td>{LEVEL_LABELS[int(latest[code])]}</td></tr>"

    return f"""<!doctype html>
<html lang="el"><head><meta charset="utf-8"><title>INELSO Service 26 Report</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1100px;margin:40px auto;color:#1f2937}}
h1,h2{{color:#183153}} table{{border-collapse:collapse;width:100%;margin:15px 0 30px}}
th,td{{border:1px solid #d1d5db;padding:8px;text-align:left}} th{{background:#f3f4f6}}
.box{{padding:14px;border-radius:8px;background:#eef6ff;margin:12px 0}}
</style></head>
<body>
<h1>INELSO Service 26 — Αναφορά Προσαρμοστικής Εξάσκησης</h1>
<div class="box"><b>Τρέχουσα επίδοση:</b> {latest['score']:.2f}/100 — {latest['mastery']}</div>
<div class="box"><b>Πρόοδος:</b> +{gain:.2f} μονάδες</div>
<div class="box"><b>Confidence:</b> {latest['confidence']:.2f} — <b>{latest['status']}</b></div>
<h2>Ιστορικό προσπαθειών</h2>
<table><tr><th>Προσπάθεια</th><th>Score</th><th>Mastery</th><th>Confidence</th><th>Status</th><th>Ενέργεια</th></tr>{attempt_rows}</table>
<h2>Rubric τελευταίας προσπάθειας</h2>
<table><tr><th>Κριτήριο</th><th>Περιγραφή</th><th>Βάρος</th><th>Επίπεδο</th></tr>{rubric_rows}</table>
<p><b>Σημείωση:</b> Η αναφορά αφορά formative practice / decision support και δεν αντικαθιστά επίσημη summative αξιολόγηση.</p>
</body></html>"""

st.title("INELSO Service 26 — Πίνακας Προσαρμοστικής Εξάσκησης")
st.caption("Formative practice analytics για rubric scoring, mastery, confidence/safety gating, ανατροφοδότηση και παρακολούθηση προόδου.")
st.info("Το Moodle παραμένει το σημείο υποβολής και αξιολόγησης. Ο πίνακας παρουσιάζει ερμηνεύσιμα αποτελέσματα και υποστήριξη απόφασης χωρίς να γράφει επίσημους βαθμούς.")

tab1, tab2, tab3, tab4 = st.tabs(["Συνοπτική εικόνα","Ανάλυση rubric","Πρόοδος μαθητή","Αναφορά / Εξαγωγή"])

with tab1:
    current = attempts.iloc[-1]
    previous = attempts.iloc[-2]
    gain = current["score"] - previous["score"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Τρέχουσα επίδοση", f"{current['score']:.2f}/100")
    c2.metric("Mastery", current["mastery"])
    c3.metric("Confidence", f"{current['confidence']:.2f}")
    c4.metric("Πρόοδος", f"+{gain:.2f}")

    st.subheader("Κατάσταση απόφασης")
    if current["status"] == "READY":
        st.success("READY — confidence ≥ 0.70 και δεν απαιτείται ανθρώπινη κλιμάκωση.")
    else:
        st.warning("ESCALATE — confidence < 0.70. Απαιτείται ανθρώπινος έλεγχος.")

    st.write("**Προτεινόμενη ενέργεια:**", current["action"])
    st.write("**Κρίσιμος κανόνας:**", critical_rule_text(current))
    st.subheader("Ροή Service 26")
    st.write("Υποβολή → Rubric → Weighted score → Mastery → Confidence/Safety gate → Feedback → Νέα προσπάθεια → Σύγκριση προόδου")

with tab2:
    st.subheader("Rubric 5 κριτηρίων")
    display_rubric = RUBRIC.copy()
    display_rubric["Attempt 1"] = [LEVEL_LABELS[int(attempts.iloc[0][c])] for c in display_rubric["criterion"]]
    display_rubric["Attempt 2"] = [LEVEL_LABELS[int(attempts.iloc[1][c])] for c in display_rubric["criterion"]]
    st.dataframe(display_rubric.rename(columns={"criterion":"Κριτήριο","name":"Περιγραφή","weight":"Βάρος (%)"}), use_container_width=True, hide_index=True)

    st.subheader("Σύγκριση rubric ανά προσπάθεια")
    chart_df = pd.DataFrame({
        "Κριτήριο": RUBRIC["criterion"],
        "Attempt 1": [attempts.iloc[0][c] for c in RUBRIC["criterion"]],
        "Attempt 2": [attempts.iloc[1][c] for c in RUBRIC["criterion"]],
    }).set_index("Κριτήριο")
    st.bar_chart(chart_df)
    st.caption("Οι τιμές είναι επίπεδα 0–4. Το RC-01 έχει κρίσιμο κανόνα: Level 0 ή 1 περιορίζει το τελικό mastery σε Developing.")

with tab3:
    st.subheader("Εξέλιξη επίδοσης")
    st.line_chart(attempts[["attempt","score"]].set_index("attempt"))

    gain = attempts.iloc[-1]["score"] - attempts.iloc[-2]["score"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Attempt 1", f"{attempts.iloc[0]['score']:.2f}")
    c2.metric("Attempt 2", f"{attempts.iloc[1]['score']:.2f}")
    c3.metric("Learning gain", f"+{gain:.2f}")

    st.subheader("Mastery και safety status")
    st.dataframe(
        attempts[["attempt","score","mastery","confidence","status","action"]].rename(columns={
            "attempt":"Προσπάθεια","score":"Score","mastery":"Mastery","confidence":"Confidence","status":"Status","action":"Προτεινόμενη ενέργεια"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.success("Η ελεγχόμενη επίδειξη δείχνει βελτίωση 61.25 → 100.00 (+38.75 μονάδες), με μετάβαση από Developing σε Mastery.")

with tab4:
    st.subheader("Λήψη επεξεργασμένων αποτελεσμάτων")
    processed = attempts.copy()
    for c in RUBRIC["criterion"]:
        processed[c] = processed[c].map(LEVEL_LABELS)

    st.download_button(
        "Λήψη CSV Service 26",
        processed.to_csv(index=False).encode("utf-8-sig"),
        "INELSO_Service26_processed_results.csv",
        "text/csv"
    )

    gain = attempts.iloc[-1]["score"] - attempts.iloc[-2]["score"]
    teacher_summary = (
        "INELSO Service 26 — Σύνοψη Εκπαιδευτή\n"
        f"Attempt 1: {attempts.iloc[0]['score']:.2f}/100 — {attempts.iloc[0]['mastery']} — confidence {attempts.iloc[0]['confidence']:.2f} — {attempts.iloc[0]['status']}\n"
        f"Attempt 2: {attempts.iloc[1]['score']:.2f}/100 — {attempts.iloc[1]['mastery']} — confidence {attempts.iloc[1]['confidence']:.2f} — {attempts.iloc[1]['status']}\n"
        f"Progress: +{gain:.2f} points\n"
        "Recommended action: No further retry is required for this practice task.\n"
        "Critical rule: RC-01 Level 0–1 caps mastery at Developing.\n"
    )
    st.download_button(
        "Λήψη σύνοψης εκπαιδευτή",
        teacher_summary.encode("utf-8"),
        "INELSO_Service26_teacher_summary.txt",
        "text/plain"
    )

    st.download_button(
        "Λήψη πλήρους αναφοράς HTML",
        html_report(attempts).encode("utf-8"),
        "INELSO_Service26_full_report.html",
        "text/html"
    )
    st.caption("Η HTML αναφορά είναι αυτόνομη και ανοίγει απευθείας σε πρόγραμμα περιήγησης.")
