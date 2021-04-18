#!/usr/bin/env python


"""
Read pgn and clk comment and tabulate players with time pressure and its perf.

Requirements:
    install python
    pip install pandas
    pip install chess
"""


__version__ = 'v1.0'
__author__ = 'fsmosca'
__script_name__ = 'time_pressure'
__goal__ = 'Read games in pgn file and calculate if a player is in time pressure or not.'


import argparse
import statistics as stat
from pathlib import Path

import pandas as pd
import chess.pgn


def get_event(fn):
    """
    Read pgn file fn and return the Event value in the first game.
    """
    with open(fn) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            return game.headers['Event']


def get_player_score(fn):
    """
    Read pgn file fn and return the number of games and points.
    """
    game_data = {}

    names = get_player_names(fn)
    for p in names:
        game_data.update({p: {'g': 0, 'pts': 0}})

    with open(fn) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            wp, bp = game.headers['White'], game.headers['Black']
            res = game.headers['Result']

            if res == '1-0':
                game_data[wp]['pts'] += 1
                
                game_data[wp]['g'] += 1
                game_data[bp]['g'] += 1

            elif res == '0-1':
                game_data[bp]['pts'] += 1

                game_data[bp]['g'] += 1
                game_data[wp]['g'] += 1

            elif res == '1/2-1/2':
                game_data[wp]['pts'] += 0.5
                game_data[bp]['pts'] += 0.5
    
                game_data[wp]['g'] += 1
                game_data[bp]['g'] += 1

    return game_data


def get_player_names(fn):
    """
    Read the pgn file fn and return unique player names sorted from a ... z
    """
    names = []

    with open(fn) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            wp, bp = game.headers['White'], game.headers['Black']

            names.append(wp)
            names.append(bp)

    return sorted(list(set(names)))


def get_sec(comment):
    """
    Read time left move comment in the game and return it in seconds.
    An example comment in the game is [%clk 0:15:20].
    """

    hr = comment.split()[1].split(']')[0].split(':')[0]
    mm = comment.split()[1].split(']')[0].split(':')[1]
    ss = comment.split()[1].split(']')[0].split(':')[2]

    return int(hr)*60*60 + int(mm)*60 + int(ss)


def get_time_left(game):
    """
    Read game and return a list of time left in seconds for both players.
    """
    w_clk_sec, b_clk_sec = [], []
    
    # Parse the moves in the game.
    for node in game.mainline():
        game_move = node.move
        board = node.board()

        # Convert comment in sec.
        comment = node.comment
        sec = get_sec(comment)

        if not board.turn:
            w_clk_sec.append(sec)
        else:
            b_clk_sec.append(sec)

    return w_clk_sec, b_clk_sec


def get_time_press_data(fn, tp_sec, last_m, player_names):
    """
    Get number of games where a player is in time pressure. A player is in
    time pressure when the average of the last n moves is tp_sec and below.
    """
    time_pressure_data = {}

    for p in player_names:
        time_pressure_data.update({p: {'g': 0, 'pts': 0}})
    
    with open(fn) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            wp = game.headers['White']
            bp = game.headers['Black']
            res = game.headers['Result']

            w_clk, b_clk = get_time_left(game)

            # Get the average time in the last n moves.
            w_ave = stat.mean(w_clk[-last_m:])
            if w_ave <= tp_sec:
                time_pressure_data[wp]['g'] += 1
                if res == '1-0':
                    time_pressure_data[wp]['pts'] += 1
                elif res == '1/2-1/2':
                    time_pressure_data[wp]['pts'] += 0.5

            b_ave = stat.mean(b_clk[-last_m:])
            if b_ave <= tp_sec:
                time_pressure_data[bp]['g'] += 1
                if res == '0-1':
                    time_pressure_data[bp]['pts'] += 1
                elif res == '1/2-1/2':
                    time_pressure_data[bp]['pts'] += 0.5

    return time_pressure_data


def main():
    parser = argparse.ArgumentParser(
        prog='%s %s' % (__script_name__, __version__),
        description=__goal__, epilog='%(prog)s')

    parser.add_argument('--input', required=True,
        help='Input pgn filename (required).')
    parser.add_argument('--time-pressure-sec', required=False, type=int,
        help='The time pressure threshold in seconds (not required) default=120. If time-pressure-sec is'
              ' 120 sec or 2 minutes and the average time remaining in the last 10 moves is 2 minutes or less'
              ' then this game will considered under time pressure for the player.',
        default=120)
    parser.add_argument('--last-n-moves', required=False, type=int,
        help='The last n moves to be considered in the calculation of time pressure (not required) default=10. If last-n-moves is 10'
              ' then we calculate the average time in those moves. If the value is time-pressure-sec and below then the player'
              ' is in time pressure.',
        default=10)
    parser.add_argument('--save-csv', action='store_true',
        help='If specified the data will be saved in csv file <input pgn file>.csv.'
             ' Example: python time_pressure.py --save-csv --input skilling_open.pgn')

    # Get value from command line.
    args = parser.parse_args()

    input_pgn_fn = args.input
    tp_sec = args.time_pressure_sec
    last_m = args.last_n_moves
    save_to_csv = args.save_csv

    tour_name = f'{get_event(input_pgn_fn)}'

    player_names = get_player_names(input_pgn_fn)

    # Get time pressure data
    time_pressure_data = get_time_press_data(input_pgn_fn, tp_sec, last_m, player_names)

    # Get player scores and num games.
    scores_data = get_player_score(input_pgn_fn)

    # Print summary.
    print()
    print(f'Time pressure stats in {tour_name}\n')
    data = {}

    for p in player_names:
        for (k, v), (k1, v1) in zip(scores_data.items(), time_pressure_data.items()):
            if p == k:
                assert k == k1, 'names should be the same'

                gtp_perf = 0.0
                if v1['g']:
                    gtp_perf = v1['pts'] / v1['g']
                    gtp_perf = round(gtp_perf, 2)
                else:
                    gtp_perf = None

                data.update({p: {'games': v['g'], 'pts': v['pts'], 'gtp': v1['g'], 'gtp_perf': gtp_perf}})
                break

    # Convert dict to panadas data frame.
    df = pd.DataFrame(data)
    df = df.transpose()  # swap column and row

    df = df.sort_values(by=['pts'], ascending=False)
    df = df.astype({'games': int, 'pts': float, 'gtp': int})
    df = df.rename_axis('name').reset_index()
    print(df.to_string(index=True))

    print('\n\n:: Column name definition ::\n')
    print('gtp     : The number of games where a player is in time pressure.')
    print('          A player is in time pressure when the average time in seconds remaining')
    print(f'          on his clock in the last {last_m} moves in a game is {tp_sec} seconds and below.')
    print('gtp_perf: The score ratio or score/games for games under time pressure only.')

    if save_to_csv:
        csv_fn = f'{Path(input_pgn_fn).stem}.csv'
        df.to_csv(csv_fn, header=True, index=False)


if __name__ == '__main__':
    main()
