"""
    To use this implementation, you simply have to implement `agent_function` such that it returns a legal action.
    You can then let your agent compete on the server by calling
        python3 client_simple.py path/to/your/config.json
    
    The script will keep running forever.
    You can interrupt it at any time.
    The server will remember the actions you have sent.

    Note:
        By default the client bundles multiple requests for efficiency.
        This can complicate debugging.
        You can disable it by setting `single_request=True` in the last line.
"""
import itertools
import json
import logging

import requests
import time

class GameState:
    def __init__(self, board, player_pegs, opponent_pegs, goal_positions, opponent_goal_positions, center_pieces):
        self.board = board
        self.player_pegs = player_pegs
        self.opponent_pegs = opponent_pegs
        self.goal_positions = goal_positions
        self.opponent_goal_positions = opponent_goal_positions
        self.center_pieces = center_pieces

    def get_possible_moves(self, maximizing_player=True):
        if maximizing_player:
            pegs = self.player_pegs
            goal_positions = self.goal_positions
        else:
            pegs = self.opponent_pegs
            goal_positions = self.opponent_goal_positions

        moves = []
        for peg in pegs:
            moves.extend(self.possible_moves(peg, goal_positions))

        return moves

    def get_new_state(self, move, maximizing_player=True):
        if maximizing_player:
            new_player_pegs = self.player_pegs.copy()
            new_player_pegs.remove(move[0])
            new_player_pegs.append(move[-1])
            new_opponent_pegs = self.opponent_pegs
        else:
            new_opponent_pegs = self.opponent_pegs.copy()
            new_opponent_pegs.remove(move[0])
            new_opponent_pegs.append(move[-1])
            new_player_pegs = self.player_pegs

        return GameState(self.board, new_player_pegs, new_opponent_pegs, self.goal_positions, self.opponent_goal_positions, self.center_pieces)

    def score(self):
        own_score = -sum(min(abs(px - gx) + abs(py - gy) for gx, gy in self.goal_positions) for px, py in self.player_pegs)
        opponent_score = sum(min(abs(px - gx) + abs(py - gy) for gx, gy in self.opponent_goal_positions) for px, py in self.opponent_pegs)
        return own_score + opponent_score

    def is_terminal(self):
        return all(pos in self.goal_positions for pos in self.player_pegs) or all(pos in self.opponent_goal_positions for pos in self.opponent_pegs)

    def possible_moves(self, peg_position, goal_positions):
        if peg_position in goal_positions:
            return []

        x, y = peg_position
        move_sequence = []

        directions = [(-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0)]

        def hop_sequences(pos, current_sequence, visited):
            hops = []
            px, py = pos
            for dx, dy in directions:
                mid_pos = (px + dx, py + dy)
                hop_pos = (px + (2 * dx), py + (2 * dy))

                if mid_pos in self.board and (mid_pos in self.player_pegs or mid_pos in self.opponent_pegs or mid_pos in self.center_pieces) and hop_pos in self.board and hop_pos not in self.player_pegs and hop_pos not in self.opponent_pegs and hop_pos not in self.center_pieces and hop_pos not in visited:
                    new_sequence = current_sequence + [hop_pos]
                    visited.add(hop_pos)
                    further_hops = hop_sequences(hop_pos, new_sequence, visited)
                    hops.extend(further_hops)
                    visited.remove(hop_pos)
            if not hops:
                hops.append(current_sequence)
            return hops

        for dx, dy in directions:
            new_pos = (x + dx, y + dy)
            if new_pos in self.board and new_pos not in self.player_pegs and new_pos not in self.opponent_pegs and new_pos not in self.center_pieces:
                move_sequence.append([peg_position, new_pos])
            else:
                mid_pos = (x + dx, y + dy)
                hop_pos = (x + (2 * dx), y + (2 * dy))
                if mid_pos in self.board and (mid_pos in self.player_pegs or mid_pos in self.opponent_pegs or mid_pos in self.center_pieces) and hop_pos in self.board and hop_pos not in self.player_pegs and hop_pos not in self.opponent_pegs and hop_pos not in self.center_pieces:
                    hop_sequences_list = hop_sequences(hop_pos, [peg_position, hop_pos], set([peg_position]))
                    for seq in hop_sequences_list:
                        move_sequence.append(seq)

        return move_sequence



def agent_function(request_dict):
    print('The request:\n')
    print(request_dict)

    board = {
                                                (-3, 6),
                                            (-3, 5), (-2, 5),
                                        (-3, 4), (-2, 4), (-1, 4),
        (-6, 3), (-5, 3), (-4, 3), (-3, 3), (-2, 3), (-1, 3), (0, 3), (1, 3), (2, 3), (3, 3),
            (-5, 2), (-4, 2), (-3, 2), (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2), (3, 2),
                (-4, 1), (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1),
                    (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0),
                (-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (3, -1), (4, -1),
            (-3, -2), (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2), (3, -2), (4, -2), (5, -2),
        (-3, -3), (-2, -3), (-1, -3), (0, -3), (1, -3), (2, -3), (3, -3), (4, -3), (5, -3), (6, -3),
                                        (1, -4), (2, -4), (3, -4),
                                            (2, -5), (3, -5),
                                                (3, -6)
    }

    goal_positions = {(-3, 6), (-3, 5), (-2, 5), (-3, 4), (-2, 4), (-1, 4)}
    # opponent_goal_positions = {(3, -6), (3, -5), (2, -5), (3, -4), (2, -4), (1, -4)} # for 2 players
    opponent_goal_positions = {(-3, -3), (-2, -3), (-1, -3), (-3, -2), (-2, -2), (-3, -1), (4, -3), (5, -3), (6, -3), (4, -2), (5, -2), (4, -1)} # for 3 players

    center_pieces = {(-1, 2), (0, 0), (-1, -1), (2, -1)}

    player_pegs = [tuple(pos) for pos in request_dict['A']]
    # opponent_pegs = [tuple(pos) for pos in request_dict['B']] # for 2 players
    opponent_pegs = [tuple(pos) for pos in request_dict['B']] + [tuple(pos) for pos in request_dict['C']] # for 3 players

    initial_state = GameState(board, player_pegs, opponent_pegs, goal_positions, opponent_goal_positions, center_pieces)

    def minimax(game_state, depth, maximizingPlayer, alpha=float('-inf'), beta=float('inf')):
        if depth == 0 or game_state.is_terminal():
            return game_state.score(), None

        if maximizingPlayer:
            value = float('-inf')
            best_move = None
            possible_moves = game_state.get_possible_moves(maximizingPlayer)
            for move in possible_moves:
                child = game_state.get_new_state(move, maximizingPlayer)
                tmp, _ = minimax(child, depth - 1, False, alpha, beta)
                if tmp > value:
                    value = tmp
                    best_move = move
                if value >= beta:
                    break
                alpha = max(alpha, value)
            return value, best_move
        else:
            value = float('inf')
            best_move = None
            possible_moves = game_state.get_possible_moves(maximizingPlayer)
            for move in possible_moves:
                child = game_state.get_new_state(move, maximizingPlayer)
                tmp, _ = minimax(child, depth - 1, True, alpha, beta)
                if tmp < value:
                    value = tmp
                    best_move = move
                if value <= alpha:
                    break
                beta = min(beta, value)
            return value, best_move

    depth = 3
    best_move = None

    if (-3, 6) not in player_pegs and ((-3, 5) in player_pegs or (-2, 5) in player_pegs):
        if (-3, 5) in player_pegs:
            best_move = [(-3, 5), (-3, 6)]
        elif (-2, 5) in player_pegs:
            best_move = [(-2, 5), (-3, 6)]
    else:
        _, best_move = minimax(initial_state, depth, True)

    print(best_move)
    return best_move




def run(config_file, action_function, single_request=False):
    logger = logging.getLogger(__name__)

    with open(config_file, 'r') as fp:
        config = json.load(fp)
    
    logger.info(f'Running agent {config["agent"]} on environment {config["env"]}')
    logger.info(f'Hint: You can see how your agent performs at {config["url"]}agent/{config["env"]}/{config["agent"]}')

    actions = []
    for request_number in itertools.count():
        logger.debug(f'Iteration {request_number} (sending {len(actions)} actions)')
        # send request
        response = requests.put(f'{config["url"]}/act/{config["env"]}', json={
            'agent': config['agent'],
            'pwd': config['pwd'],
            'actions': actions,
            'single_request': single_request,
        })
        if response.status_code == 200:
            response_json = response.json()
            for error in response_json['errors']:
                logger.error(f'Error message from server: {error}')
            for message in response_json['messages']:
                logger.info(f'Message from server: {message}')

            action_requests = response_json['action-requests']
            if not action_requests:
                logger.info('The server has no new action requests - waiting for 1 second.')
                time.sleep(1)  # wait a moment to avoid overloading the server and then try again
            # get actions for next request
            actions = []
            for action_request in action_requests:
                actions.append({'run': action_request['run'], 'action': action_function(action_request['percept'])})
        elif response.status_code == 503:
            logger.warning('Server is busy - retrying in 3 seconds')
            time.sleep(3)  # server is busy - wait a moment and then try again
        else:
            # other errors (e.g. authentication problems) do not benefit from a retry
            logger.error(f'Status code {response.status_code}. Stopping.')
            break


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    run(sys.argv[1], agent_function, single_request=False)
