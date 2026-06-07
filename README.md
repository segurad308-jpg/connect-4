# Connect 4 AI

A high-performance Connect Four AI developed in Python. The project implements an advanced game-playing agent capable of analyzing board positions and selecting strong moves within a strict time limit.

## Overview

This AI plays Connect Four autonomously using a combination of:

* Minimax search
* Alpha-Beta Pruning
* Principal Variation Search (PVS)
* Iterative Deepening
* Zobrist Hashing
* Transposition Tables
* Move Ordering Heuristics

The objective is to maximize the AI's chances of winning while efficiently exploring the game tree under a one-second decision limit.

---

## Features

### Minimax Algorithm

The core of the AI is based on the Minimax algorithm, which evaluates future game states by assuming both players make optimal decisions.

### Alpha-Beta Pruning

Branches that cannot influence the final decision are discarded early, significantly reducing the number of explored positions.

### Principal Variation Search (PVS)

An optimized version of Alpha-Beta search that performs narrow-window searches to improve performance.

### Iterative Deepening

The AI gradually increases search depth until the available time expires, ensuring that a valid move is always available.

### Zobrist Hashing

Each board state is assigned a unique hash value, allowing efficient storage and retrieval of previously evaluated positions.

### Transposition Table

A cache stores evaluated board positions to avoid redundant computations and speed up the search process.

### Smart Move Ordering

Moves are prioritized according to their strategic importance:

1. Immediate winning moves
2. Blocking opponent winning moves
3. Center columns
4. Remaining legal moves

This greatly improves Alpha-Beta efficiency.

---

## Board Evaluation

The AI evaluates positions by analyzing windows of four cells across:

* Rows
* Columns
* Diagonals

The heuristic rewards:

* Potential winning alignments
* Three-in-a-row opportunities
* Two-in-a-row opportunities
* Control of the center column

It also penalizes equivalent opportunities for the opponent.

---

## Performance Optimizations

To maximize search depth within the one-second limit, several optimizations are used:

* In-place move simulation
* Constant-time move undoing
* Efficient winner detection
* Cached board evaluations
* Principal Variation Search
* Iterative deepening search

These optimizations allow the AI to analyze thousands of positions per move.

---

## Project Structure

```text
team_strategy.py
│
├── MinimaxStrategy
├── Zobrist Hashing Functions
├── Board Evaluation Functions
├── Winner Detection
├── Move Ordering
├── Alpha-Beta Search
├── Principal Variation Search
└── Iterative Deepening
```

---

## Search Process

```text
Current Position
       │
       ▼
 Move Ordering
       │
       ▼
 Iterative Deepening
       │
       ▼
 Minimax Search
       │
       ▼
 Alpha-Beta Pruning
       │
       ▼
 Transposition Table Lookup
       │
       ▼
 Position Evaluation
       │
       ▼
 Best Move
```

---

## Technologies Used

* Python 3
* Object-Oriented Programming
* Game Tree Search Algorithms
* Heuristic Evaluation Functions
* Hash Tables
* Time-Constrained Search

---

## How It Works

1. Generate all legal moves.
2. Check for immediate wins.
3. Check for necessary defensive moves.
4. Search future positions using Minimax.
5. Prune irrelevant branches using Alpha-Beta.
6. Reuse previously analyzed positions through the Transposition Table.
7. Continue increasing search depth until the time limit is reached.
8. Return the best move found.

---

## Future Improvements

Possible enhancements include:

* Better evaluation heuristics
* Threat-space search
* Opening book support
* Endgame databases
* Parallel search
* Monte Carlo Tree Search (MCTS) comparison

---

## Authors

Developed as part of a university Artificial Intelligence project focused on creating a competitive Connect Four agent capable of participating in tournaments against other AI strategies.
