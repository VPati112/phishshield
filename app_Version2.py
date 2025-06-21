import re
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')

# Simple keyword and link detection
URGENT_KEYWORDS = [
    "act now", "urgent", "your account", "reset your password",
    "verify your account", "login to", "confirm your identity",
    "limited time", "click here", "update your info"
]
RED_FLAG_DOMAINS = [
    "bit.ly", "tinyurl", "goo.gl", "rb.gy", "ow.ly"
]

def analyze_text(text):
    scam_score = 0
    reasons = []

    # Check for suspicious links
    links = re.findall(r'https?://[^\s]+', text)
    flagged_links = [link for link in links if any(d in link for d in RED_FLAG_DOMAINS)]
    if flagged_links:
        scam_score += 2
        reasons.append(f"Suspicious short-link(s) detected: {', '.join(flagged_links)}")

    # Check for urgent words/phrases
    for keyword in URGENT_KEYWORDS:
        if keyword.lower() in text.lower():
            scam_score += 1
            reasons.append(f"Urgent/pressure keyword detected: \"{keyword}\"")

    # Basic sender checks
    if "from:" in text.lower() and ("support" in text.lower() or "admin" in text.lower()) and "gmail.com" in text.lower():
        scam_score += 1
        reasons.append("Weird sender info (claims official but uses Gmail address)")

    # Grammar check (very basic: lots of mistakes == suspicious)
    if len(re.findall(r'[.!?]', text)) > 0:
        fragments = re.split(r'[.!?]', text)
        bad_grammar = sum(1 for frag in fragments if len(frag.split()) < 3 and frag.strip())
        if bad_grammar > 2:
            scam_score += 1
            reasons.append("Poor grammar detected")

    # Scam Likelihood
    if scam_score >= 3:
        likelihood = "High"
    elif scam_score == 2:
        likelihood = "Medium"
    else:
        likelihood = "Low"

    return {
        "likelihood": likelihood,
        "reasons": reasons if reasons else ["No obvious scam signals detected."]
    }

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    text = data.get("text", "")
    result = analyze_text(text)
    return jsonify(result)

@app.route("/", methods=["GET"])
def root():
    return app.send_static_file("index.html")

@app.route("/<path:path>", methods=["GET"])
def static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(debug=True)