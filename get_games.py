from flask import Response
import requests
import chess.pgn
import io
from chess.polyglot import open_reader
import csv
import re
import json

def clean_move(san):
    return san.lower().replace("+", "").replace("#", "").replace("x", "").strip()

def is_move_token(token):
    return not re.match(r"^\d+\.$", token)

openings = []

tsv_files = [
    "datasets/a.tsv",
    "datasets/b.tsv",
    "datasets/c.tsv",
    "datasets/d.tsv",
    "datasets/e.tsv"
]

for file_path in tsv_files:
    with open(file_path, newline='', encoding="utf-8") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            tokens = row["pgn"].strip().split()
            move_list = [clean_move(t) for t in tokens if is_move_token(t)]
            openings.append({
                "eco": row["eco"],
                "name": row["name"],
                "moves": move_list
            })

def detect_opening_from_moves(game_moves):
    if isinstance(game_moves, str):
        game_moves = game_moves.strip().lower().split()

    for opening in sorted(openings, key=lambda x: len(x["moves"]), reverse=True):
        if game_moves[:len(opening["moves"])] == opening["moves"]:
            return f'{opening["eco"]}: {opening["name"]}'
    
    return "Unknown"


def get_games_from_archives(username):
    games = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    response = requests.get(archives_url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:200]}")

    if response.status_code == 200:
        data = response.json()
        # -1 is one month
        latest_archive = data['archives'][-1]

        games_response = requests.get(latest_archive, headers=headers)
        games_data = games_response.json()


        for i, game_data in enumerate(games_data['games']):
            pgn_str = game_data['pgn']
            pgn_io = io.StringIO(pgn_str)
            pgn_game = chess.pgn.read_game(pgn_io)

            board = pgn_game.board()
            moves_san = []
            for move in pgn_game.mainline_moves():
                moves_san.append(board.san(move))
                board.push(move)

            moves_str = " ".join(moves_san)
            opening = detect_opening_from_moves(moves_str)

            white = game_data['white']['username']
            black = game_data['black']['username']
            white_rating = game_data['white'].get('rating', '?')
            black_rating = game_data['black'].get('rating', '?')
            result = pgn_game.headers.get("Result", "?")

            


            fen = game_data["fen"]

            date = pgn_game.headers.get("Date", "?")

            games.append({
                "white": white,
                "black": black,
                "white_rating": white_rating,
                "black_rating": black_rating,
                "result": result,
                "opening": opening,
                "moves": moves_str,
                "fen": fen,
                "pgn": pgn_str,
                "date": date
            })
        
        gamesJson = 0
        gamesJson = json.dumps(games, ensure_ascii=False, separators=(",", ":"))
        return Response(gamesJson, mimetype="application/json")
    else:
        return "X Failed to fetch archives."
