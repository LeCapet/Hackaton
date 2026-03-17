from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def estimate_pollution(prompt):
    
    # estimation simple du nombre de tokens
    tokens = len(prompt.split())

    # estimations fictives (à ajuster selon ton modèle scientifique)
    energy_per_token = 0.0001
    co2_per_kwh = 0.4

    energy = tokens * energy_per_token
    co2 = energy * co2_per_kwh

    return {
        "tokens": tokens,
        "energy": round(energy, 6),
        "co2": round(co2, 6)
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()
    prompt = data["prompt"]

    pollution = estimate_pollution(prompt)

    return jsonify({
        "prompt": prompt,
        "pollution": pollution
    })

if __name__ == "__main__":
    app.run(debug=True)