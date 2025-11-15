from flask import Flask, render_template, request, jsonify
from nim_core import (
    is_terminal, generate_moves, apply_move,
    best_move_minimax, best_move_bfs
)

app = Flask(__name__)

# حالة اللعبة البسيطة – في مشروع حقيقي ممكن تخزن في جلسة أو DB
game_state = {
    "piles": [3, 5, 2],
    "turn": "human",          # "human" أو "ai"
    "strategy": "Minimax",    # "Minimax" أو "BFS"
    "difficulty": "Medium"    # Easy / Medium / Hard
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/state")
def state():
    return jsonify(game_state)


@app.route("/set_options", methods=["POST"])
def set_options():
    data = request.json or {}
    game_state["strategy"] = data.get("strategy", "Minimax")
    game_state["difficulty"] = data.get("difficulty", "Medium")
    # إعادة ضبط الأكوام ودور اللاعب
    game_state["piles"] = [3, 5, 2]
    game_state["turn"] = "human"
    return jsonify(game_state)


@app.route("/move/human", methods=["POST"])
def human_move():
    if game_state["turn"] != "human":
        return jsonify({"error": "Not your turn"}), 400

    data = request.json or {}
    pile = data.get("pile")
    remove = data.get("remove")

    piles = game_state["piles"]

    # تحقّق من صحة الحركة
    if (
        pile is None or remove is None
        or pile < 0 or pile >= len(piles)
        or remove < 1 or remove > piles[pile]
    ):
        return jsonify({"error": "Invalid move"}), 400

    # تطبيق حركة اللاعب
    piles[pile] -= remove

    # هل انتهت اللعبة؟
    if is_terminal(piles):
        game_state["turn"] = "none"
        return jsonify({"piles": piles, "winner": "human"})

    # دور الذكاء الاصطناعي الآن
    game_state["turn"] = "ai"
    return jsonify({"piles": piles, "winner": None})


@app.route("/move/ai", methods=["POST"])
def ai_move():
    if game_state["turn"] != "ai":
        return jsonify({"error": "Not AI turn"}), 400

    import random

    piles = game_state["piles"]
    strategy = game_state["strategy"]
    difficulty = game_state["difficulty"]

    moves = generate_moves(piles)
    if not moves:
        game_state["turn"] = "none"
        return jsonify({"piles": piles, "winner": "human"})

    # صعوبة سهلة: عشوائية بالكامل
    if difficulty == "Easy":
        move = random.choice(moves)
    else:
        # متوسط: 50٪ من الوقت عشوائي
        if difficulty == "Medium" and random.random() < 0.5:
            move = random.choice(moves)
        else:
            # صعب: يعتمد على الخوارزمية المختارة
            if strategy == "Minimax":
                move = best_move_minimax(piles)
            else:  # BFS
                move = best_move_bfs(piles)

    i, r = move
    piles[i] -= r

    if is_terminal(piles):
        game_state["turn"] = "none"
        return jsonify(
            {
                "piles": piles,
                "winner": "ai",
                "move": {"pile": i, "remove": r},
            }
        )

    game_state["turn"] = "human"
    return jsonify(
        {
            "piles": piles,
            "winner": None,
            "move": {"pile": i, "remove": r},
        }
    )


if __name__ == "__main__":
    # شغّل السيرفر
    app.run(debug=True)