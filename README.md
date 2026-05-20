# ChessDex
My attempt at programming a chess engine from scratch

## Environment
Enter python environment
```bash
source /workspaces/ChessDex/.venv/bin/activate
. .venv/bin/activate
```

## Unit Testing
```bash
pytest -v
```

## Load a PGN
```python
from pathlib import Path
from models.bitboard import Board

PATH_TO = Path(__file__).parent / "path" / "to"
board = Board().from_pgn(PATH_TO / "easyM2.pgn")
```
