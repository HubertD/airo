from flask import Flask, redirect, url_for, render_template, request, jsonify
from game import Game
from player import Player
import random
import string

app = Flask(__name__)
games = {}
sessions = {} # session_id -> (session, player_name)


def create_session_key():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(8))


def get_data(session: str) -> (Game, Player):
    session, player_name = sessions[session]
    game = games[session]
    player = game.get_player(player_name)
    return game, player


def get_or_create_game(session: str) -> Game:
    if session in games:
        return games[session]

    game = Game(name=session)
    games[game.name] = game
    return game


def get_state(game, player):
    data = game.get_json_state()
    data['self'] = player.get_json_state()
    return jsonify(data)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<session>/')
def main(session):
    game, player = get_data(session)
    tpl = 'lobby.html' if game.state == Game.State.INIT else 'game.html'
    return render_template(tpl, game=game, player=player, session=session)


@app.route('/<session>/round_finished')
def round_finished(session):
    game, player = get_data(session)
    return render_template('round_finished.html', game=game, player=player, session=session)


@app.route('/join', methods=['POST'])
def join():
    session = request.form['game']
    player_name = request.form['player']
    game = get_or_create_game(session)
    player = game.get_or_create_player(player_name)
    session = create_session_key()
    sessions[session] = (game.name, player.name)
    return redirect(url_for('main', session=session))


@app.route('/<session>/state', methods=['GET'])
def state(session):
    game, player = get_data(session=session)
    return get_state(game, player)


@app.route('/<session>/start', methods=['POST'])
def start(session):
    game, player = get_data(session=session)
    game.start()
    return redirect(url_for('main', session=session))


@app.route('/<session>/take/discarded', methods=['POST'])
def take_discarded(session):
    game, player = get_data(session=session)
    game.take_discarded(player=player)
    return get_state(game, player)


@app.route('/<session>/take/deck', methods=['POST'])
def take_deck(session):
    game, player = get_data(session=session)
    game.take_deck(player=player)
    return get_state(game, player)


@app.route('/<session>/keep', methods=['POST'])
def keep(session):
    game, player = get_data(session=session)
    game.keep(player=player)
    return get_state(game, player)


@app.route('/<session>/discard', methods=['POST'])
def discard(session):
    game, player = get_data(session=session)
    game.discard(player=player)
    return get_state(game, player)


@app.route('/<session>/put', methods=['POST'])
def put(session):
    game, player = get_data(session=session)
    card_index = int(request.form['card_index'])
    game.put(player=player, card_index=card_index)
    return get_state(game, player)


@app.route('/<session>/reveal', methods=['POST'])
def reveal(session):
    game, player = get_data(session=session)
    card_index = int(request.form['card_index'])
    game.reveal(player=player, card_index=card_index)
    return get_state(game, player)


@app.route('/<session>/next_round', methods=['POST'])
def next_round(session):
    game, player = get_data(session=session)
    game.next_round(player=player)
    return get_state(game, player)


if __name__ == '__main__':
    app.run()
