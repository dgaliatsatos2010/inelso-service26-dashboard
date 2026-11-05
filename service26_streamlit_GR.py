import pandas as pd
import streamlit as st

st.set_page_config(page_title="INELSO Service 26 — Adaptive Practice Intelligence", page_icon="🧭", layout="wide")

RUBRIC = pd.DataFrame([
    {"criterion": "RC-01", "name": "Εννοιολογική ακρίβεια", "weight": 30},
    {"criterion": "RC-02", "name": "Μέθοδος / συλλογισμός", "weight": 25},
    {"criterion": "RC-03", "name": "Τεκμηρίωση / υποστήριξη", "weight": 15},
    {"criterion": "RC-04", "name": "Πληρότητα", "weight": 15},
    {"criterion": "RC-05", "name": "Σαφήνεια / επικοινωνία", "weight": 15},
])

RESOURCE_MAP = {
    "RC-01": "Foundation Resource — βασικές έννοιες και ορθότητα",
    "RC-02": "Practice Resource — βήματα επίλυσης και συλλογισμός",
    "RC-03": "Evidence Resource — τεκμηρίωση, παραδείγματα και δεδομένα",
    "RC-04": "Advanced Resource — πληρότητα και σύνθεση",
    "RC-05": "Communication Resource — σαφήνεια και δομή απάντησης",
}

LEVEL_LABELS = {0:"Level 0",1:"Level 1",2:"Level 2",3:"Level 3",4:"Level 4"}

history = pd.DataFrame([
    {"learner":"Demo Student 0201","attempt":1,"RC-01":3,"RC-02":2,"RC-03":2,"RC-04":2,"RC-05":3,
     "score":61.25,"mastery":"Developing","confidence":0.65},
    {"learner":"Demo Student 0201","attempt":2,"RC-01":4,"RC-02":4,"RC-03":4,"RC-04":4,"RC-05":4,
     "score":100.00,"mastery":"Mastery","confidence":0.85},
])

cohort = pd.DataFrame([
    {"learner":"Demo Student 0201","score":100,"mastery":"Mastery","confidence":0.85,"status":"READY"},
    {"learner":"Demo Student 0202","score":78.75,"mastery":"Proficient","confidence":0.81,"status":"READY"},
    {"learner":"Demo Student 0203","score":66.25,"mastery":"Developing","confidence":0.68,"status":"ESCALATE"},
    {"learner":"Demo Student 0204","score":91.25,"mastery":"Mastery","confidence":0.88,"status":"READY"},
    {"learner":"Demo Student 0205","score":57.50,"mastery":"Developing","confidence":0.72,"status":"RETRY"},
])

def adaptive_status(score, confidence, rc01):
    if confidence < 0.70 or rc01 <= 1:
        return "ESCALATE"
    if score < 70:
        return "RETRY"
    return "READY"

def gap_analysis(row):
    rows = []
    for _, r in RUBRIC.iterrows():
        code = r["criterion"]
        level = int(row[code])
        gap = 4 - level
        rows.append({"criterion":code,"name":r["name"],"level":level,"gap":gap,"weight":r["weight"],"weighted_gap":gap*r["weight"]})
    return pd.DataFrame(rows).sort_values(["weighted_gap","weight"], ascending=False)

def next_action(row):
    status = adaptive_status(row["score"], row["confidence"], row["RC-01"])
    gaps = gap_analysis(row)
    top = gaps.iloc[0]
    if status == "ESCALATE":
        return "Ανθρώπινος έλεγχος πριν από νέα αυτοματοποιημένη σύσταση.", "Human review / instructor intervention"
    if status == "RETRY":
        return f"Νέα προσπάθεια με εστίαση στο {top['criterion']} — {top['name']}.", RESOURCE_MAP[top["criterion"]]
    return "Δεν απαιτείται νέα προσπάθεια. Προτείνεται enrichment ή επόμενη δραστηριότητα.", "Enrichment Resource"

st.title("INELSO Service 26 — Adaptive Practice Intelligence")
st.caption("Προσαρμοστική formative εξάσκηση με rubric analytics, mastery, confidence/safety gating, criterion-level gaps και εξατομικευμένη επόμενη ενέργεια.")
st.info("Το Moodle παραμένει το σημείο υποβολής και επίσημης διαχείρισης. Ο Service 26 λειτουργεί ως read-only decision-support και adaptive recommendation layer.")

mode = st.sidebar.radio("Προβολή", ["Learner view", "Teacher view"])

if mode == "Learner view":
    tabs = st.tabs(["Συνοπτική εικόνα","Κενά ανά κριτήριο","Πρόοδος","Adaptive next action","Εξαγωγή"])
    latest = history.iloc[-1]
    prev = history.iloc[-2]
    gain = latest["score"] - prev["score"]
    status = adaptive_status(latest["score"], latest["confidence"], latest["RC-01"])
    action, resource = next_action(latest)

    with tabs[0]:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Score", f"{latest['score']:.2f}/100")
        c2.metric("Mastery", latest["mastery"])
        c3.metric("Confidence", f"{latest['confidence']:.2f}")
        c4.metric("Status", status)
        c5.metric("Πρόοδος", f"+{gain:.2f}")
        if status == "READY":
            st.success("READY — η απόκριση μπορεί να προχωρήσει χωρίς ανθρώπινη κλιμάκωση.")
        elif status == "RETRY":
            st.warning("RETRY — χρειάζεται νέα προσπάθεια με στοχευμένη ενίσχυση.")
        else:
            st.error("ESCALATE — απαιτείται ανθρώπινος έλεγχος.")
        st.write("**Προτεινόμενη ενέργεια:**", action)
        st.write("**Προτεινόμενο resource:**", resource)

    with tabs[1]:
        gaps = gap_analysis(latest)
        show = gaps[["criterion","name","level","gap","weight"]].copy()
        show.columns = ["Κριτήριο","Περιγραφή","Τρέχον επίπεδο","Κενό προς Level 4","Βάρος (%)"]
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.bar_chart(show.set_index("Κριτήριο")[["Τρέχον επίπεδο","Κενό προς Level 4"]])
        top = gaps.iloc[0]
        if top["gap"] > 0:
            st.warning(f"Υψηλότερη προτεραιότητα: {top['criterion']} — {top['name']}.")
        else:
            st.success("Δεν υπάρχουν criterion-level gaps στην τελευταία προσπάθεια.")

    with tabs[2]:
        st.line_chart(history[["attempt","score"]].set_index("attempt"))
        rubric_progress = pd.DataFrame({
            "Κριτήριο": RUBRIC["criterion"],
            "Attempt 1": [history.iloc[0][c] for c in RUBRIC["criterion"]],
            "Attempt 2": [history.iloc[1][c] for c in RUBRIC["criterion"]],
        }).set_index("Κριτήριο")
        st.bar_chart(rubric_progress)
        st.success(f"Βελτίωση {prev['score']:.2f} → {latest['score']:.2f} ({gain:+.2f} μονάδες), με μετάβαση {prev['mastery']} → {latest['mastery']}.")

    with tabs[3]:
        st.subheader("Adaptive next action")
        st.write("**Decision state:**", status)
        st.write("**Next action:**", action)
        st.write("**Recommended resource:**", resource)
        st.markdown("#### Λογική απόφασης")
        st.write("1. Confidence/safety gate → 2. Κρίσιμος κανόνας RC-01 → 3. Score threshold → 4. Weighted criterion gap → 5. RETRY / enrichment / human review.")

    with tabs[4]:
        processed = history.copy()
        for c in RUBRIC["criterion"]:
            processed[c] = processed[c].map(LEVEL_LABELS)
        st.download_button("Λήψη ιστορικού Service 26 CSV", processed.to_csv(index=False).encode("utf-8-sig"), "INELSO_Service26_learner_history.csv", "text/csv")
        summary = (
            f"INELSO Service 26 — Learner Summary\nLearner: {latest['learner']}\n"
            f"Current score: {latest['score']:.2f}/100\nMastery: {latest['mastery']}\n"
            f"Confidence: {latest['confidence']:.2f}\nStatus: {status}\nProgress: {gain:+.2f}\n"
            f"Next action: {action}\nRecommended resource: {resource}\n"
        )
        st.download_button("Λήψη learner summary", summary.encode("utf-8"), "INELSO_Service26_learner_summary.txt", "text/plain")
else:
    tabs = st.tabs(["Cohort overview","Learners needing action","Decision rules","Export"])
    with tabs[0]:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Learners", len(cohort))
        c2.metric("Μέσο score", f"{cohort['score'].mean():.1f}")
        c3.metric("READY", int((cohort["status"]=="READY").sum()))
        c4.metric("Χρειάζονται ενέργεια", int((cohort["status"]!="READY").sum()))
        st.dataframe(cohort, use_container_width=True, hide_index=True)
        counts = cohort["status"].value_counts().rename_axis("Status").reset_index(name="Count")
        st.bar_chart(counts.set_index("Status"))
    with tabs[1]:
        needs = cohort[cohort["status"]!="READY"].copy()
        st.dataframe(needs, use_container_width=True, hide_index=True)
        if not needs.empty:
            st.warning("Τα ESCALATE προηγούνται των RETRY cases επειδή απαιτούν ανθρώπινο έλεγχο.")
    with tabs[2]:
        st.markdown("""
- **Confidence < 0.70 → ESCALATE**
- **RC-01 Level 0–1 → ESCALATE / mastery cap = Developing**
- **Score < 70 και safety OK → RETRY**
- **Score ≥ 70 και safety OK → READY**
- Στο **RETRY**, επιλέγεται το criterion με το μεγαλύτερο weighted gap.
- Στο **READY**, προτείνεται enrichment ή επόμενη δραστηριότητα.
""")
        st.info("Οι κανόνες είναι ερμηνεύσιμοι και deterministic. Δεν αλλάζουν αυτόματα επίσημους βαθμούς ή submissions στο Moodle.")
    with tabs[3]:
        st.download_button("Λήψη cohort CSV", cohort.to_csv(index=False).encode("utf-8-sig"), "INELSO_Service26_teacher_cohort.csv", "text/csv")
        st.download_button("Λήψη λίστας ενεργειών", cohort[cohort["status"]!="READY"].to_csv(index=False).encode("utf-8-sig"), "INELSO_Service26_action_list.csv", "text/csv")
