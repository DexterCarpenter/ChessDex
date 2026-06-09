# ChessDex

![Tests](https://github.com/DexterCarpenter/ChessDex/actions/workflows/ci.yml/badge.svg)

My attempt at programming a chess engine from scratch

Play against the engine [on my website](https://dextercarpenter.dev/chessdex/)!

## Environment
Enter python environment
```bash
source /workspaces/ChessDex/.venv/bin/activate
. .venv/bin/activate
```

## Play UI
Start the local web UI (board in the browser, JSON API on port 8765):

```bash
source .venv/bin/activate
python src/play_ui.py
# or: python src/main.py
```

Open http://127.0.0.1:8765/ — click squares to move, choose mode (human/human, vs engine, engine/engine), toggle **Show engine best move**, undo, etc. Terminal-only play: `python src/play_solo.py`.

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
