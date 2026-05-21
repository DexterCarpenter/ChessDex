#!/usr/bin/env python3
"""Profile engine search; run from repo root: python scripts/profile_engine.py."""

from __future__ import annotations

import cProfile
import pstats
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from models.bitboard import Board
from models.engine import Engine


def _run(depth: int) -> None:
    board = Board()
    board.setup_starting_position()
    engine = Engine()
    engine.get_best_move(board, depth)


def main() -> None:
    engine = Engine()
    board = Board()
    board.setup_starting_position()

    print("ChessDex engine profile (starting position)")
    for depth in (2, 3, 4):
        board.setup_starting_position()
        t0 = time.perf_counter()
        engine.get_best_move(board, depth)
        elapsed = time.perf_counter() - t0
        print(f"  depth {depth}: {elapsed:.3f}s")

    print("\ncProfile (depth 4):")
    prof = cProfile.Profile()
    prof.enable()
    _run(4)
    prof.disable()
    stats = pstats.Stats(prof).sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(25)


if __name__ == "__main__":
    main()
