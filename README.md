# Othello AI Battle

Pygame-based Othello game with a Q-learning AI. It supports human vs AI
matches, AI pre-training (self-play), and learning statistics.

## Requirements

- Python 3.9+
- pygame
- matplotlib

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install pygame matplotlib
```

## Run

```bash
python main.py
```

Optional: run a quick AI vs AI test.

```bash
python test_ai_vs_ai.py
```

## Generated data

The following files are created at runtime and are not tracked by git:

- qtable.pkl (Q-table)
- learning_history.json (learning stats)
- window_size_config.json (window settings)

Deleting them will reset the stored data.
