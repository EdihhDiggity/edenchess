from flask import Flask, render_template, jsonify
import json, os, random

app = Flask(__name__)

def load_puzzle_set(setname):
    """Load all puzzles from puzzles/<setname>/*.json"""
    basepath = os.path.join("puzzles", setname)
    all_puzzles = []
    if not os.path.isdir(basepath):
        raise FileNotFoundError(f"No such puzzle set: {setname}")

    for fname in os.listdir(basepath):
        if fname.endswith(".json"):
            with open(os.path.join(basepath, fname), "r") as f:
                try:
                    puzzles = json.load(f)
                    all_puzzles.extend(puzzles)
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON in {fname}, skipping")

    return all_puzzles

@app.route("/<setname>")
def serve_set(setname):
    try:
        puzzles = load_puzzle_set(setname)
    except FileNotFoundError:
        return jsonify({"error": "Puzzle set not found"}), 404

    # shuffle puzzles so first load is random
    random.shuffle(puzzles)

    return render_template("board.html", puzzles=puzzles)

if __name__ == "__main__":
    app.run(debug=True)
