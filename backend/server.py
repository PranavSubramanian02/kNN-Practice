import os

from config import Base_Dir, Data_Path, Target_Player
from dataloader import load_data
from evaluator import SimilarityEvaluator
from flask import Flask, jsonify, request, send_from_directory

# Directory containing index.html, styles.css, and app.js
frontend_dir = os.path.join(Base_Dir, "frontend")
app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
# Preload dataset and initialize evaluator once on startup
df = load_data(Data_Path)
evaluator = SimilarityEvaluator(df, target_name=Target_Player)


@app.route("/")
def index():
    """Serves the main analytics dashboard HTML page."""
    return send_from_directory(frontend_dir, "index.html")


@app.route("/api/players", methods=["GET"])
def get_players():

    players = [
        {
            "name": str(row["player"]),
            "club": str(row["club"]),
            "league": str(row["league"]),
            "position": str(row["position"]),
        }
        for _, row in df.iterrows()
    ]
    return jsonify(players)


@app.route("/api/compare", methods=["GET"])
def compare():

    competitor = request.args.get("player")
    benchmark = request.args.get("benchmark", Target_Player)
    if not competitor:
        return jsonify({"error": "Missing required 'player' query parameter."}), 400
    try:
        comparison_payload = evaluator.compare_strikers(
            competitor_name=competitor, benchmark_name=benchmark
        )
        return jsonify(comparison_payload)
    except IndexError as e:
        return jsonify({"error": str(e)}), 404
    except (KeyError, ValueError, RuntimeError) as e:
        return jsonify({"error": f"Server calculation error: {e}"}), 500


if __name__ == "__main__":
    port = 5000
    print("=" * 65)
    print("  European Striker Analytics Server Running")
    print(f"  Dashboard URL: http://127.0.0.1:{port}")
    print(f"  Target Benchmark: {Target_Player}")
    print("=" * 65)
    app.run(host="127.0.0.1", port=port, debug=False)
