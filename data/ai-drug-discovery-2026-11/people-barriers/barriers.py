"""an earlier step B1 and B2: cut the risk-factor section from each latest annual report, list every AI sentence
and the classes its words match (B1), and extract stated-runway and going-concern sentences (B2).
Rules fixed in the research record Usage (from repo root): python3 analysis/015/barriers.py
Writes ai_sentences.csv, sections.json, runway.csv.
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(HERE, "raw", "latest_index.json")))

AI = re.compile(r"artificial intelligence|machine learning|deep learning|neural network|\bgenerative\b|\bAI\b|\bML\b|"
                r"foundation model|large language model", re.I)
CLASSES = {
    "data": re.compile(r"\bdata\b.*\b(access|quality|sufficient|insufficient|obtain|availab|licen[cs]e|privacy|"
                       r"proprietary|incomplete|biased|bias)|\b(access|quality|sufficient|insufficient|obtain|availab|"
                       r"licen[cs]e|privacy|proprietary|incomplete|biased|bias)\w*\b.*\bdata\b", re.I),
    "validation": re.compile(r"unproven|not been validated|may not|might not|\bfail|inaccurate|flawed|"
                             r"no .{0,40}approved|not .{0,40}successful|predict", re.I),
    "ai_regulation": re.compile(r"regulat|legislation|\blaws?\b|AI Act|guidance|executive order", re.I),
    "compute_tools": re.compile(r"comput|cloud|GPU|third.party|vendor|infrastructure|supercomputer", re.I),
}
# Section markers: start = line matching START, end = next line matching END; the longest span is used.
START = re.compile(r"^ ?(Item 1A\.? ?Risk Factors?\.?|Item 1A\. Ris|Item 1A\. R|D\. ?RISK FACTORS|D\. Risk Factors ?|"
                   r"3\.D\. Risk Factors)\s*$", re.I)
END = re.compile(r"^ ?(Item 1B\.?.*|Item 4\.? Information on the.*|ITEM 4\. INFORMATION ON THE.*)$", re.I)
# Eikon's body headings are not in "Item 1A" form: start at the first risk heading after the summary,
# end at "Item 1C. Cybersecurity." (lines located by hand, an earlier step.
OVERRIDE = {"Eikon": (re.compile(r"^Risks Related to Our Business, Limited Operating History"),
                      re.compile(r"^Item 1C\. Cybersecurity\.?$"))}


def section(name, lines):
    st, en = OVERRIDE.get(name, (START, END))
    best = (0, 0)
    for i, l in enumerate(lines):
        if st.match(l.strip() if name in OVERRIDE else l):
            for j in range(i + 1, len(lines)):
                if en.match(lines[j].strip() if name in OVERRIDE else lines[j]):
                    if j - i > best[1] - best[0]:
                        best = (i, j)
                    break
    return best


def sentences(text):
    text = re.sub(r"\s*\n\s*", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.;!?])\s+(?=[A-Z“\"(•])", text) if s.strip()]


RUNWAY = re.compile(r"sufficient to fund|sufficient to meet|enable us to fund|fund our (operating expenses|operations)"
                    r".{0,120}(into|through|until|at least)", re.I)
GC = re.compile(r"substantial doubt", re.I)


def main():
    rows, runway, secs = [], [], {}
    for name, c in IDX["companies"].items():
        f = c["filing"]
        if not f:
            secs[name] = None
            continue
        full = open(os.path.join(HERE, f["text"])).read()
        lines = full.split("\n")
        a, b = section(name, lines)
        sec = "\n".join(lines[a:b])
        secs[name] = {"start_line": a + 1, "end_line": b + 1, "chars": len(sec), "form": f["form"], "filed": f["filed"]}
        for k, s in enumerate(sentences(sec)):
            if AI.search(s):
                r = {"company": name, "n": k, "sentence": s}
                for cl, rx in CLASSES.items():
                    r[cl] = int(bool(rx.search(s)))
                rows.append(r)
        allsent = sentences(full)
        rw = [s for s in allsent if RUNWAY.search(s) and re.search(r"20[2-3]\d|months", s)]
        gc = [s for s in allsent if GC.search(s)]
        runway.append({"company": name, "filed": f["filed"], "runway_sentences": " || ".join(rw[:4]),
                       "n_going_concern_sentences": len(gc), "going_concern_first": gc[0] if gc else ""})
    with open(os.path.join(HERE, "ai_sentences.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["company", "n", "sentence"] + list(CLASSES))
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, "runway.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(runway[0]))
        w.writeheader(); w.writerows(runway)
    json.dump(secs, open(os.path.join(HERE, "sections.json"), "w"), indent=1)
    for n, s in secs.items():
        k = sum(1 for r in rows if r["company"] == n)
        print(n, s and s["chars"], "AI sentences:", k,
              {cl: sum(r[cl] for r in rows if r["company"] == n) for cl in CLASSES})


if __name__ == "__main__":
    main()
