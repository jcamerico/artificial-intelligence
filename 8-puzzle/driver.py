"""
Skeleton code for Project 1 of Columbia University's AI EdX course (8-puzzle).
Python 3
"""

from collections import deque

import time

import resource

import sys

import math

#### SKELETON CODE ####

# Class storing the configurations in the frontier (next ones to be processed)
class Frontier(object):
    def __init__(self):
        self.full_states = []
        self.reduced_states = set()
        self.costs = []

    def cheapest(self):
        min_cost_index = self.get_min_cost_index()
        next_state = self.full_states.pop(min_cost_index)        
        self.costs.pop(min_cost_index)
        return next_state
    
    def next(self):
        next_state = self.full_states.pop(0)        
        self.reduced_states.discard(next_state.config)
        return next_state

    def contains(self, state):
        # Membership checks are much faster on sets
        return state.config in self.reduced_states

    def append(self, state):
        self.full_states.append(state)
        self.reduced_states.add(state.config)

    def appendleft(self, state):
        self.full_states.insert(0, state)
        self.reduced_states.add(state.config)

    def append_with_cost(self, state):
        self.full_states.append(state)
        self.reduced_states.add(state.config)
        self.costs.append(calculate_total_cost(state))

    def size(self):
        return len(self.full_states)

    def get_min_cost_index(self):
        min_cost = -1
        min_index = -1
        for index, cost in enumerate(self.costs):
            if min_index == -1 or cost < min_cost:
                min_index = index
                min_cost = cost
        return min_index                

## The Class that Represents the Puzzle
class PuzzleState(object):

    """This class represents a specific configuration of the puzzle"""

    def __init__(self, config, n, parent=None, action="Initial", cost=0):
        if n*n != len(config) or n < 2:
            raise Exception("the length of config is not correct!")
        self.n = n
        self.cost = cost
        self.parent = parent
        self.action = action
        self.dimension = n
        self.config = config
        self.children = []
        for i, item in enumerate(self.config):
            if item == 0:
                self.blank_row = i // self.n
                self.blank_col = i % self.n
                break

    def display(self):
        for i in range(self.n):
            line = []
            offset = i * self.n
            for j in range(self.n):
                line.append(self.config[offset + j])
            print(line)

    def move_left(self):
        if self.blank_col == 0:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index - 1
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Left", cost=self.cost + 1)

    def move_right(self):
        if self.blank_col == self.n - 1:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index + 1
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Right", cost=self.cost + 1)

    def move_up(self):
        if self.blank_row == 0:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index - self.n
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Up", cost=self.cost + 1)

    def move_down(self):
        if self.blank_row == self.n - 1:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index + self.n
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Down", cost=self.cost + 1)

    def expand(self):
        """expand the node"""
        # add child nodes in order of UDLR
        if len(self.children) == 0:
            up_child = self.move_up()
            if up_child is not None:
                self.children.append(up_child)
            down_child = self.move_down()
            if down_child is not None:
                self.children.append(down_child)
            left_child = self.move_left()
            if left_child is not None:
                self.children.append(left_child)
            right_child = self.move_right()
            if right_child is not None:
                self.children.append(right_child)
        return self.children

# Function that Writes to output.txt

def writeOutput(goal_state, visited_states, max_depth, running_time):
    actions = deque()
    node = goal_state
    while (node.parent is not None):
        actions.appendleft(node.action)
        node = node.parent
    print('path_to_goal: ', actions)
    print('cost of path: ', goal_state.cost)
    print('nodes_expanded: ', visited_states)
    print('search_depth: ', goal_state.cost)
    print('max search_depth: ', max_depth)
    print('running_time: ', running_time)
    print('max_ram_usage: ', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)

def bfs_search(initial_state):
    """BFS search"""
    start_time = time.time()
    goal = tuple([i for i in range(initial_state.dimension * initial_state.dimension)])
    visited_states = set()
    frontier = Frontier()
    frontier.append(initial_state)
    max_depth = initial_state.cost
    while frontier.size() > 0:
        current_state = frontier.next()        

        if (current_state.config == goal):
            writeOutput(current_state, len(visited_states), max_depth, time.time() - start_time)
            return

        else:
            visited_states.add(current_state.config)
            for child in current_state.expand():
                if child.config not in visited_states and not frontier.contains(child):
                    if (child.cost > max_depth):
                        max_depth = child.cost
                    frontier.append(child)

    print('FAILURE')

def dfs_search(initial_state):
    """DFS search"""
    start_time = time.time()
    goal = tuple([i for i in range(initial_state.dimension * initial_state.dimension)])
    visited_states = set()
    frontier = Frontier()
    frontier.append(initial_state)
    max_depth = initial_state.cost
    while frontier.size() > 0:
        current_state = frontier.next()        
                
        if (current_state.config == goal):
            writeOutput(current_state, len(visited_states), max_depth, time.time() - start_time)
            return

        else:
            visited_states.add(current_state.config)
            children = current_state.expand()
            children.reverse()
            for child in children:
                if child.config not in visited_states and not frontier.contains(child):
                    if (child.cost > max_depth):
                        max_depth = child.cost
                    frontier.appendleft(child)

def A_star_search(initial_state):
    """A * search"""
    start_time = time.time()
    goal = tuple([i for i in range(initial_state.dimension * initial_state.dimension)])
    visited_states = set()
    frontier = Frontier()
    frontier.append_with_cost(initial_state)
    max_depth = initial_state.cost
    while frontier.size() > 0:
        current_state = frontier.cheapest()        
                
        if (current_state.config == goal):
            writeOutput(current_state, len(visited_states), max_depth, time.time() - start_time)
            return

        else:
            visited_states.add(current_state.config)
            children = current_state.expand()
            for child in children:
                if child.config not in visited_states and not frontier.contains(child):
                    if (child.cost > max_depth):
                        max_depth = child.cost
                    frontier.append_with_cost(child)

def calculate_total_cost(state):
    """calculate the total estimated cost of a state"""
    cost = state.cost
    for i, item in enumerate(state.config): 
        cost += calculate_manhattan_dist(i, item, state.n)
    return cost

def calculate_manhattan_dist(idx, value, n):
    """calculate the manhattan distance of a tile"""
    if value == 0 or idx == value:
        return 0
    else:
        current_row = idx // n
        target_row = value // n
        current_col = idx % n
        target_col = value % n
        return abs(target_row - current_row) + abs(target_col - current_col)

# Main Function that reads in Input and Runs corresponding Algorithm
def main():
    sm = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = tuple(map(int, begin_state))
    size = int(math.sqrt(len(begin_state)))
    hard_state = PuzzleState(begin_state, size)
    if sm == "bfs":
        bfs_search(hard_state)
    elif sm == "dfs":
        dfs_search(hard_state)
    elif sm == "ast":
        A_star_search(hard_state)
    else:
        print("Enter valid command arguments !")

if __name__ == '__main__':
    main()