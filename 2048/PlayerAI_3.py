from BaseAI_3 import BaseAI
import sys
import math
import time
import logging


class PlayerAI(BaseAI):

    def __init__(self):
        self.cache = dict()
        self.possible_values = tuple([2, 4])
        self.max_time = 0.02
        logging.basicConfig(level=logging.DEBUG)

    def getMove(self, grid):
        self.start_time = time.process_time()
        if len(grid.getAvailableMoves()) == 0:
            # no more moves can be done, return anything
            return 0
        else:
            move = grid.getAvailableMoves()[0]
            max_depth = 1
            while self.hasTime() :
                logging.debug('iterative DFS - iteration %d', max_depth)
                result = self.maximize(grid, 0, max_depth, Pruning())
                if result is not None:
                    move = result.move
                    logging.debug('iterative DFS - iteration %d: result %d with score of %.10f', max_depth, result.move, result.utility)
                else:
                    # This could happen when there is no time left to continue processing
                    logging.debug('iterative DFS - iteration %d: result none', max_depth)
                if self.hasTime():
                    max_depth += 1
            logging.debug('final result: iterations %d, move %d', max_depth, move)
            return move

    def hasTime(self):
        return time.process_time() - self.start_time < self.max_time

    def maximize(self, grid, depth, max_depth, pruning): 
        moves = grid.getAvailableMoves()
        if max_depth == depth or len(moves) == 0:
            return PlayerMove(self.evaluate(grid), None)
        if not self.hasTime():
            # no more time left, we stop
            return self.time_is_over()
        
        max_move = None
        max_utility = -1 * sys.maxsize
        for move in moves:
            if self.hasTime():
                grid_copy = grid.clone()
                grid_copy.move(move)
                utility = self.minimize(grid_copy, depth + 1, max_depth, pruning)
                if utility is not None:
                    if utility > max_utility:
                        max_move = move
                        max_utility = utility
                    if max_utility >= pruning.beta:
                        break
                    if max_utility > pruning.alpha:
                        pruning.alpha = max_utility
                elif self.hasTime():
                    return self.time_is_over()

            else:
                return self.time_is_over()
        if max_move is None:
            return None
        else:
            return PlayerMove(max_utility, max_move)
 
    def minimize(self, grid, depth, max_depth, pruning):
        available_cells = grid.getAvailableCells()
        if max_depth == depth or len(available_cells) == 0:
            return self.evaluate(grid)
        if not self.hasTime():
            return self.time_is_over()

        min_utility = sys.maxsize        
        prune_done = False
        for cell in available_cells:
            if prune_done:
                break
            for value in self.possible_values:
                if self.hasTime():
                    grid_copy = grid.clone()
                    grid_copy.insertTile(cell, value)
                    move = self.maximize(grid_copy, depth + 1, max_depth, pruning)
                    if move is not None:
                        if move.utility < min_utility:
                            min_utility = move.utility
                        if min_utility <= pruning.alpha:
                            prune_done = True
                            break
                        if min_utility < pruning.beta:
                            pruning.beta = min_utility
                    elif not self.hasTime():
                        return self.time_is_over()
        
                else:
                    return self.time_is_over()
        
        if min_utility == sys.maxsize:
            return None
        else:
            return min_utility
    
    def evaluate(self, grid):
        key = self.key(grid)
        utility = self.cache.get(key)
        weight_avtiles = 3
        weight_mono = 0.8
        weight_smooth = 0.5
        weight_max_tile = 1

        monotonicity_up = 0
        monotonicity_down = 0
        monotonicity_left = 0
        monotonicity_right = 0
        smoothness = 0

        if utility is None:
            maxTile = -1
            available_tiles = 0
            last_column = [0] * grid.size
            monotonicity = 0

            for x in range(grid.size):
                last_value = 0
                for y in range(grid.size):                    
                    value = grid.map[x][y]
                    value_factor = 0

                    if value == 0:
                        available_tiles += 1
                    else:
                        value_factor = math.log2(value)

                    if value_factor > last_value:
                        monotonicity_right += last_value - value_factor
                    elif last_value > value_factor:
                        monotonicity_left += value_factor - last_value
                    last_value = value_factor

                    if value_factor > last_column[y]:
                        monotonicity_down += last_column[y] - value_factor
                    elif last_column[y] > value_factor:
                        monotonicity_up += value_factor - last_column[y]
                    last_column[y] = value_factor

                    maxTile = max(maxTile, value)

                    if value != 0:
                        next_right = self.get_next_tile(grid, [x, y], lambda position: [position[0] + 1, position[1]])
                        if next_right is not None:
                            smoothness += abs(value_factor - next_right)
                        next_left = self.get_next_tile(grid, [x, y], lambda position: [position[0] - 1, position[1]])
                        if next_left is not None:
                            smoothness += abs(value_factor - next_left)
                        next_up = self.get_next_tile(grid, [x, y], lambda position: [position[0], position[1] - 1])
                        if next_up is not None:
                            smoothness += abs(value_factor - next_up)
                        next_down = self.get_next_tile(grid, [x, y], lambda position: [position[0], position[1] + 1])
                        if next_down is not None:
                            smoothness += abs(value_factor - next_down)

            utility = weight_max_tile * maxTile
            monotonicity = weight_mono * (max(monotonicity_up, monotonicity_down) + max(monotonicity_left, monotonicity_right))
            utility += monotonicity
            empty_tiles = weight_avtiles * available_tiles * math.log2(maxTile)
            utility += empty_tiles
            utility -= weight_smooth * smoothness

            logging.debug('grid: %s / max = %d / tiles = %.5f / mono = %.5f / smoothness = %.5f / utility = %.5f', grid.map, maxTile, empty_tiles, monotonicity, weight_smooth * smoothness, utility)

            self.cache[key] = utility

        return max(0, utility)

    def get_next_tile(self, grid, position, position_function):
        current_position = position
        for i in range(grid.size):
            current_position = position_function(current_position)
            tile = grid.getCellValue(current_position)
            if tile is None:
                return None
            elif tile != 0:
                return math.log2(tile)
            

    def key(self, grid):
        key = []
        for i in range(grid.size):
            key += grid.map[i]
        return tuple(key)

    def time_is_over(self):
        logging.debug('time is over')
        return None

class PlayerMove:
    def __init__(self, utility, move):
        self.utility = utility
        self.move = move

class Pruning:
    def __init__(self):
        self.alpha = -1
        self.beta = sys.maxsize