from collections import Counter

class Board(object):
    def cross(self, A, B):
        "Cross product of elements in A and elements in B."
        return [s+t for s in A for t in B]

    def assign_value(self, values, box, value):
        """
        Please use this function to update your values dictionary!
        Assigns a value to a given box. If it updates the board record it.
        """
        # Don't waste memory appending actions that don't actually change any values
        if values[box] == value:
            return values
        values[box] = value
        if len(value) == 1:
            assignments.append(values.copy())
        return values

    def naked_twins(self, values):
        """Eliminate values using the naked twins strategy.
        Args:
            values(dict): a dictionary of the form {'box_name': '123456789', ...}

        Returns:
            the values dictionary with the naked twins eliminated from peers.
        """
        # Find all instances of naked twins
        # Eliminate the naked twins as possibilities for their peers
        #Naked twin: when any two boxes in a unit contain the same two possible values,
        #both of those values can be eliminated from all other boxes in the unit.
        for unit in self.unitlist:
            two_values = [values[box] for box in unit if len(values[box]) == 2]
            counts = Counter(two_values)
            for item in counts:
                if counts[item] == 2:
                    #eliminate those two numbers from all boxes in the unit
                    twins = list(item)
                    for peer in unit:
                        if values[peer] != item:
                            for digit in twins:
                                values[peer] = values[peer].replace(digit,'')
        return values

    def grid_values(self, grid):
        """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        Args:
            grid(string) - A grid in string form.
        Returns:
            A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
        chars = []
        digits = '123456789'
        for c in grid:
            if c in digits:
                chars.append(c)
            if c == '.':
                chars.append(digits)
        assert len(chars) == 81
        return dict(zip(self.boxes, chars))

    def display(self, values):
        """
        Display the values as a 2-D grid.
        Args:
            values(dict): The sudoku in dictionary form
        """
        width = 1+max(len(values[s]) for s in self.boxes)
        line = '+'.join(['-'*(width*3)]*3)
        for r in self.rows:
            print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in self.cols))
            if r in 'CF': print(line)
        return

    def eliminate(self, values):
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        for box in solved_values:
            digit = values[box]
            for peer in self.peers[box]:
                values[peer] = values[peer].replace(digit,'')
        return values

    def only_choice(self, values):
        for unit in self.unitlist:
            for digit in '123456789':
                dplaces = [box for box in unit if digit in values[box]]
                if len(dplaces) == 1:
                    values[dplaces[0]] = digit
        return values

    def reduce_puzzle(self, values):
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        stalled = False
        while not stalled:
            solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
            values = self.eliminate(values)
            values = self.only_choice(values)
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            stalled = solved_values_before == solved_values_after
            if len([box for box in values.keys() if len(values[box]) == 0]):
                return False
        return values

    def search(self, values):
        "Using depth-first search and propagation, try all possible values."
        # First, reduce the puzzle using the previous function
        values = self.reduce_puzzle(values)
        if values is False:
            return False ## Failed earlier
        if all(len(values[s]) == 1 for s in self.boxes):
            return values ## Solved!
        # Choose one of the unfilled squares with the fewest possibilities
        n,s = min((len(values[s]), s) for s in self.boxes if len(values[s]) > 1)
        # Now use recurrence to solve each one of the resulting sudokus, and
        for value in values[s]:
            new_sudoku = values.copy()
            new_sudoku[s] = value
            attempt = self.naked_twins(new_sudoku)
            attempt = self.search(new_sudoku)
            if attempt:
                return attempt

    def solve(self):
        """
        Find the solution to a Sudoku grid.
        Args:
            grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
            The dictionary representation of the final sudoku grid. False if no solution exists.
        """
        values = self.grid_values(self.grid)
        return self.search(values)

    def __init__(self, grid):
        self.rows = 'ABCDEFGHI'
        self.cols = '123456789'
        self.assignments = []
        self.grid = grid
        self.boxes = self.cross(self.rows, self.cols)
        self.row_units = [self.cross(r, self.cols) for r in self.rows]
        self.column_units = [self.cross(self.rows, c) for c in self.cols]
        self.square_units = [self.cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
        self.diagonal_units = [['A1','B2','C3','D4','E5','F6','G7','H8','I9'],['A9','B8','C7','D6','E5','F4','G3','H2','I1']]
        self.unitlist = self.row_units + self.column_units + self.square_units + self.diagonal_units
        self.units = dict((s, [u for u in self.unitlist if s in u]) for s in self.boxes)
        self.peers = dict((s, set(sum(self.units[s],[]))-set([s])) for s in self.boxes)


if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #diag_sudoku_grid = '2..............2....1....7...6..8...3.......7...6......4....8.....2.............3'
    #diag_sudoku_grid = '.........................7......8...3.......7...6................................'

    #'Hard' example found online(not diagonal):
    #diag_sudoku_grid = '....1.8..8..6...5.45.9.3.7....3...9.9.7...4.3.3...1....1.8.4.65.4...6..1..6.7....'

    #Diagonal example from online
    diag_sudoku_grid = '....2.7........5..14..........6.7...8.......4...1.8..........52..8........3.7....'

    board = Board(diag_sudoku_grid)
    solution = board.solve()
    board.display(solution)
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

'''
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]
def naked_twins(values):
    print("Original Board:")
    Board(values).display(values)
    rows = 'ABCDEFGHI'
    cols = '123456789'
    boxes = cross(rows, cols)
    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    unitlist = row_units + column_units + square_units
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    #Naked twin: when any two boxes in a unit contain the same two possible values,
    #both of those values can be eliminated from all other boxes in the unit.
    for unit in unitlist:
        two_values = [values[box] for box in unit if len(values[box]) == 2]
        print(two_values)
        counts = Counter(two_values)
        #print(counts)
        for item in counts:
            if counts[item] == 2:
                print(item)
                #eliminate those two numbers from all boxes in the unit
                twins = list(item)
                #print(twins)
                for peer in unit:
                    #print(peer)
                    if values[peer] != item:
                        #print(values[peer])
                        for digit in twins:
                            values[peer] = values[peer].replace(digit,'')
                        print("reduction made")
                        Board(values).display(values)
    print("Final Board:")
    Board(values).display(values)


    possible_solutions_1 = [
        {'G7': '6', 'G6': '3', 'G5': '2', 'G4': '9', 'G3': '1', 'G2': '8', 'G1': '7', 'G9': '5', 'G8': '4', 'C9': '1',
         'C8': '5', 'C3': '8', 'C2': '237', 'C1': '23', 'C7': '9', 'C6': '6', 'C5': '37', 'A4': '2357', 'A9': '8',
         'A8': '6', 'F1': '6', 'F2': '4', 'F3': '23', 'F4': '1235', 'F5': '8', 'F6': '125', 'F7': '35', 'F8': '9',
         'F9': '7', 'B4': '27', 'B5': '1', 'B6': '8', 'B7': '27', 'E9': '2', 'B1': '9', 'B2': '5', 'B3': '6', 'C4': '4',
         'B8': '3', 'B9': '4', 'I9': '9', 'I8': '7', 'I1': '23', 'I3': '23', 'I2': '6', 'I5': '5', 'I4': '8', 'I7': '1',
         'I6': '4', 'A1': '1', 'A3': '4', 'A2': '237', 'A5': '9', 'E8': '1', 'A7': '27', 'A6': '257', 'E5': '347',
         'E4': '6', 'E7': '345', 'E6': '579', 'E1': '8', 'E3': '79', 'E2': '37', 'H8': '2', 'H9': '3', 'H2': '9',
         'H3': '5', 'H1': '4', 'H6': '17', 'H7': '8', 'H4': '17', 'H5': '6', 'D8': '8', 'D9': '6', 'D6': '279',
         'D7': '34', 'D4': '237', 'D5': '347', 'D2': '1', 'D3': '79', 'D1': '5'},
        {'I6': '4', 'H9': '3', 'I2': '6', 'E8': '1', 'H3': '5', 'H7': '8', 'I7': '1', 'I4': '8', 'H5': '6', 'F9': '7',
         'G7': '6', 'G6': '3', 'G5': '2', 'E1': '8', 'G3': '1', 'G2': '8', 'G1': '7', 'I1': '23', 'C8': '5', 'I3': '23',
         'E5': '347', 'I5': '5', 'C9': '1', 'G9': '5', 'G8': '4', 'A1': '1', 'A3': '4', 'A2': '237', 'A5': '9',
         'A4': '2357', 'A7': '27', 'A6': '257', 'C3': '8', 'C2': '237', 'C1': '23', 'E6': '579', 'C7': '9', 'C6': '6',
         'C5': '37', 'C4': '4', 'I9': '9', 'D8': '8', 'I8': '7', 'E4': '6', 'D9': '6', 'H8': '2', 'F6': '125',
         'A9': '8', 'G4': '9', 'A8': '6', 'E7': '345', 'E3': '79', 'F1': '6', 'F2': '4', 'F3': '23', 'F4': '1235',
         'F5': '8', 'E2': '3', 'F7': '35', 'F8': '9', 'D2': '1', 'H1': '4', 'H6': '17', 'H2': '9', 'H4': '17',
         'D3': '79', 'B4': '27', 'B5': '1', 'B6': '8', 'B7': '27', 'E9': '2', 'B1': '9', 'B2': '5', 'B3': '6',
         'D6': '279', 'D7': '34', 'D4': '237', 'D5': '347', 'B8': '3', 'B9': '4', 'D1': '5'}
        ]
    print("Possible Solutions(1):")
    Board(values).display(possible_solutions_1[0])
    Board(values).display(possible_solutions_1[1])

    return values
'''
