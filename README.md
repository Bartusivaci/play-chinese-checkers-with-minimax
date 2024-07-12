# Repository for ss24.1.2/team049

**Topic:** SS24 Assignment 1.2: Play FAUhalma

## Requirements

This project was run with Python 3.11 and wasn't tested for other versions. It will work most likely.

- ``requests`` was used to communicate with the server to test our agent
- ``time`` was used to wait between calls to not overload the server
- ``math`` was used for mathematical computations

Since they're all preinstalled, we only need to import them.

## Repository Structure

- ``agent-configs`` file has different configuration files for different environments separated by difficulty levels for our agent
- ``client_simple.py`` file is the algorithm that solves the problem

## How To Run

There are different version of this problem such as ``2-player`` or `3-player` so we should comment / uncomment 
the lines accordingly. For 2-player environments we should uncomment the lines ``133`` and ``139`` and comment the lines
``134`` and `140`. For 3-player vice versa. 

After that we can open the terminal in the IDE and run the command:
- ``py client_simple.py path/to/config``

## The Problem

We need an algorithm that will play ``Chinese Checkers`` and win against other opponent algorithms.

| Environment | Challenges          |
|-------------|---------------------|
| 1           | test environment    |
| 2           | 2-player (easy)     |
| 3           | 2-player (medium)   |
| 4           | 2-player (hard)     |
| 5           | 3-player (easy)     |
| 6           | 3-player (medium)   | 
| 7           | 3-player (hard)     |
| 8           | 3-player (hardcore) |

## My Approach

**The Board**: Since the board of this game is not our typical rectangle shape, I created a variable called ``board`` 
that will hold every coordinate. So that when my agent is moving I can be sure that it is indeed inside the boundaries.

**Move Directions**: To generate the adjacent coordinates of our pegs, I checked and found out adding these ``[(-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0)]``
coordinates will give us the exact 6 adjacent cell that we can move. Additional if statement is needed to be sure they're inside boundaries.

Also, to find the cell that we can hop into I used the formula:
``x + (2 * x_of_direction), y + (2 * y_of_direction)`` The direction is one of the six coordinates I stated above.

**Greedy Algorithm**: At first I used ``Greedy Algorithm`` to always chose the moves that got me closest to the goals.
This implementation worked well for the environment 1 which is the easy one and managed to get around 0.85 rating. But when
I tried using it on harder environments I got very low ratings, so I switched to Minimax with alpha beta pruning.

**Minimax Algorithm**: I decided that an ``Adversarial Search`` will get me better results since I'll anticipate my opponent's
moves and then pick better moves accordingly. We are the maximizing player since we want to maximize our score and
the opponent(s) are minimizing players who want to minimize it. After implementing this approach my rating became solid
1.0 in environment 1 and managed to get way better results in 2-player medium and 3-player easy as well.

**Depth**: Currently the recursive minimax algorithm expands the branches 3 times, so the depth is set to be 3. I tried 
running with more than 3 to get better moves but decision tree branches grows exponential so even with 4 the calculation
time is too much to complete a game. Even after alpha-beta pruning, 3 is optimal for this algorithm.

**Evaluation Function**: After we implement the next 3 moves in total for our agent and opponent, we update the board with
current peg placements. Then the ``score`` function evaluates the board. We calculate the distances between the pegs and
goals. We want the distance of our pegs to goals to be minimum as much as possible while opponent's maximum as much as possible.

Basically, for every possible move that our agent can perform, we try to predict the state of our board after 3 moves,
and select the best move that will give us the best board score. That is why the calculation time grows exponential as we 
increase the depth of our algorithm.

To calculate the distance, I tried both ``Manhattan Distance`` and `Euclidean Distance`. I got slightly better results
with Euclidean Distance so used it to calculate the distance between pegs and goals.

## Challenges

**Getting Stuck**: At the beginning I realized that I was losing a lot of the games because my algorithm would place 5 
of my pegs in the goal coordinates but only leave the top corner empty, so my last peg could never reach there and
go back and forth in the same coordinates.

I simply added an if statement that checks if top corner is empty but adjacent are not, then move the peg in adjacent into 
top corner.

**3-player**: Minimax algorithm is for 2 players but there are environments with 3 players.

I considered both B and C as one opponent so defined the board accordingly. Created a single opponent pegs variable
that keeps both opponent's pegs and also combined their goal coordinates. It seems to be working for environment 5 which
is 3-player (easy) and my agent got 1.62 rating.




