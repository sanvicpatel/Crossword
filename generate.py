import sys

from crossword import *
import math
from copy import deepcopy


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # Creates copy of self.domains
        domains_copy = deepcopy(self.domains)

        # Traverses through every value of every variable in domain dictionary
        for variable in domains_copy:
            for value in domains_copy[variable]:
                # If the length the variable is supposed to be does not equal length of the value, removes value
                if variable.length != len(value):
                    self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        cell = self.crossword.overlaps[x, y]

        # If no overlap, returns false
        if cell is None:
            return revised

        # Records overlap of both variables in i and j
        i = cell[0]
        j = cell[1]

        domains_x_copy = deepcopy(self.domains[x])

        # Traverses through every value in x's domain
        for value_x in domains_x_copy:
            # Assumes there is a conflict between x and y
            conflict = True
            # Traverses through every value in y's domain
            for value_y in self.domains[y]:
                # If any y value has the same character as the x value at the overlap position, makes conflict False
                if value_x[i:i+1] == value_y[j:j+1]:
                    conflict = False
                    # Stops searching for conflicts if it finds at least one y value works
                    break
            # If conflict is still true, removes that x value from x's domain
            if conflict:
                self.domains[x].remove(value_x)
                revised = True

        return revised

        raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # If ars is None, creates a list of tuples containing every variable, neighbor pair
        if arcs is None:
            arcs = []
            for variable in self.domains:
                for neighbor in self.crossword.neighbors(variable):
                    arcs.append((variable, neighbor))

        # While arcs length is not 0
        while len(arcs) != 0:
            # Takes a random arc
            (x, y) = arcs.pop()
            # If a domain changed while implementing arc consistency,
            if self.revise(x, y):
                # Checks if domain is empty. If it is, returns False
                if len(self.domains[x]) == 0:
                    return False
                # Adds all neighbors of x other than y to arcs
                for z in self.crossword.neighbors(x):
                    if z == y:
                        continue
                    arcs.append((z, x))
        return True

        raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # If there is any variable in crossword.variables that is not in assignment, returns False.
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        # If all variables are in assignment, returns True
        return True
        raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Creates an empty dictionary to hold already-traversed variabls
        assignment_copy = dict()
        # Traverses every variable in assignment
        for variable in assignment:
            # If the variable is in the assignment_copy dictionary, returns False as there are 2 of the same variables
            if variable in assignment_copy:
                return False
            # Adds the variable to the assignment_copy dictionary
            assignment_copy[variable] = assignment[variable]
            # If length of the variable is not equal to length of the variable's value, returns false
            if len(assignment[variable]) != variable.length:
                return False
            neighbors = self.crossword.neighbors(variable)
            # Traverses through each neighbor. If overlap between neighbors contains different letters, returns False
            for neighbor in neighbors:
                (x,y) = self.crossword.overlaps[variable, neighbor]
                if neighbor in assignment:
                    if assignment[variable][x:x+1] != assignment[neighbor][y:y+1]:
                        return False
        # If assignment passed through all the tests above without returning false, returns true
        return True

        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Creates empty dictionary that maps each value to the number of other values it constrains
        constraining_values = dict()
        # Traverses through every value in the domain of var
        for val in self.domains[var]:
            conflict_count = 0
            # Traverses through each neighbor of var
            for neighbor in self.crossword.neighbors(var):
                # Traverses through every value for each neighbor
                for neighbor_value in self.domains[neighbor]:
                    # If the neighbor is not assigned to a value, checks if overlap contains different letters
                    if neighbor not in assignment:
                        (i, j) = self.crossword.overlaps[var, neighbor]
                        # If there is a conflict, increases count to conflict_count
                        if val[i:i+1] != neighbor_value[j:j+1]:
                            conflict_count += 1
            # Adds to the dictionary the value and its corresponding total conflict_count
            constraining_values[val] = conflict_count

        # Sorts through dictionary in ascending order of conflict_count
        sort_constraining_values = sorted(constraining_values.items(), key = lambda x: x[1])

        sorted_values = []
        # Creates list of all the values
        for item in sort_constraining_values:
            sorted_values.append(item[0])

        # Returns the list
        return sorted_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_values = math.inf
        # Creates empty list to hold all variables with equal (but minimum) number of remaining values
        min_remaining_values = []
        # Traverses through every variable
        for var in self.crossword.variables:
            # If the variable is not in assignment,
            if var not in assignment:
                # Assigns length of the domain of the variable to remaining_values
                remaining_values = len(self.domains[var])
                # If remaining_values is equal to the min number of values, adds var to list
                if remaining_values == min_values:
                    min_remaining_values.append(var)
                # If remaining_values is less than current min number of values,
                if remaining_values < min_values:
                    # Makes length of var the new min
                    min_values = remaining_values
                    # Clears current list
                    min_remaining_values.clear()
                    # Adds the new min var to lsit
                    min_remaining_values.append(var)

        # If there is only one minimum, returns that minimum variable
        if len(min_remaining_values) == 1:
            return min_remaining_values[0]

        # If there are several minimums, creates max_neighbors and max_variable variables
        max_neighbors = len(self.crossword.neighbors(min_remaining_values[0]))
        max_var = min_remaining_values[0]
        # Traverses through variables in list
        for var in min_remaining_values:
            neighbors = len(self.crossword.neighbors(var))
            # If number of neighbors of current variable is greater than max number of neighbors,
            if neighbors > max_neighbors:
                # Makes max_neighbors the current length of neighbors
                max_neighbors = neighbors
                # And makes max_var the current var
                max_var = var

        return max_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete, returns assignment
        if self.assignment_complete(assignment):
            return assignment

        # Selects an unassigned variable
        var = self.select_unassigned_variable(assignment)
        # Traverses through every value in the domain of var
        for value in self.order_domain_values(var, assignment):
            # Makes a copy of assignment and adds var:value to copy
            assignment_copy = deepcopy(assignment)
            assignment_copy[var] = value
            # If the copy is consistent, adds var:value pair to real assignment
            if self.consistent(assignment_copy):
                assignment[var] = value
                # Calls backtrack on new assignment
                result = self.backtrack(assignment)
                # If the result is an assignment, returns the result
                if result is not None:
                    return result
            # Deletes var:value pair from the copy of assignment if it wasn't consistent
            del assignment_copy[var]

        return None

        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
