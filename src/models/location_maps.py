"""Piece-square location modifiers for evaluation.

Each map is an 8×8 grid of floats added to a piece's material value when it
occupies that square. Rows are listed from rank 8 (top) down to rank 1 (bottom),
columns from file a to h — the same orientation as a standard chess diagram
with White on rank 1.

Only White-oriented maps are stored here. Black uses the same values with the
rank mirrored (1↔8, files unchanged); see ``Engine._location_map_index``.

Modifiers use the same scale as ``MATERIAL_BY_PIECE`` (pawn = 1.0).
"""

from __future__ import annotations

from models.bitboard import Piece

# fmt: off
_PAWN = (
    " 0.00  0.00  0.00  0.00  0.00  0.00  0.00  0.00",  # 8
    " 0.50  0.50  0.50  0.50  0.50  0.50  0.50  0.50",  # 7
    " 0.10  0.10  0.20  0.30  0.30  0.20  0.10  0.10",  # 6
    " 0.05  0.05  0.10  0.25  0.25  0.10  0.05  0.05",  # 5
    " 0.00  0.00  0.00  0.20  0.20  0.00  0.00  0.00",  # 4
    " 0.05  0.05  0.10  0.10  0.10  0.10  0.05  0.05",  # 3
    " 0.00  0.00  0.00  0.00  0.00  0.00  0.00  0.00",  # 2
    " 0.00  0.00  0.00  0.00  0.00  0.00  0.00  0.00",  # 1
)

_KNIGHT = (
    "-0.40 -0.20  0.00  0.00  0.00  0.00 -0.20 -0.40",  # 8
    "-0.20  0.00  0.10  0.15  0.15  0.10  0.00 -0.20",  # 7
    " 0.00  0.10  0.15  0.20  0.20  0.15  0.10  0.00",  # 6
    " 0.00  0.15  0.20  0.25  0.25  0.20  0.15  0.00",  # 5
    " 0.00  0.10  0.20  0.25  0.25  0.20  0.10  0.00",  # 4
    " 0.00  0.10  0.15  0.20  0.20  0.15  0.10  0.00",  # 3
    "-0.20  0.00  0.10  0.15  0.15  0.10  0.00 -0.20",  # 2
    "-0.40 -0.20  0.00  0.05  0.05  0.00 -0.20 -0.40",  # 1
)

_BISHOP = (
    "-0.20  0.00  0.00  0.00  0.00  0.00  0.00 -0.20",  # 8
    " 0.00  0.10  0.10  0.10  0.10  0.10  0.10  0.00",  # 7
    " 0.00  0.10  0.15  0.15  0.15  0.15  0.10  0.00",  # 6
    " 0.00  0.10  0.15  0.20  0.20  0.15  0.10  0.00",  # 5
    " 0.00  0.10  0.15  0.20  0.20  0.15  0.10  0.00",  # 4
    " 0.00  0.10  0.15  0.15  0.15  0.15  0.10  0.00",  # 3
    " 0.00  0.10  0.10  0.10  0.10  0.10  0.10  0.00",  # 2
    "-0.20  0.00  0.05  0.00  0.00  0.05  0.00 -0.20",  # 1
)

_ROOK = (
    " 0.00  0.00  0.00  0.00  0.00  0.00  0.00  0.00",  # 8
    " 0.05  0.10  0.10  0.10  0.10  0.10  0.10  0.05",  # 7
    "-0.05  0.00  0.00  0.00  0.00  0.00  0.00 -0.05",  # 6
    "-0.05  0.00  0.00  0.00  0.00  0.00  0.00 -0.05",  # 5
    "-0.05  0.00  0.00  0.00  0.00  0.00  0.00 -0.05",  # 4
    "-0.05  0.00  0.00  0.00  0.00  0.00  0.00 -0.05",  # 3
    "-0.05  0.00  0.00  0.00  0.00  0.00  0.00 -0.05",  # 2
    " 0.00  0.00  0.00  0.05  0.05  0.00  0.00  0.00",  # 1
)

_QUEEN = (
    "-0.20 -0.10 -0.05  0.00  0.00 -0.05 -0.10 -0.20",  # 8
    "-0.10  0.00  0.00  0.00  0.00  0.00  0.00 -0.10",  # 7
    "-0.05  0.00  0.05  0.05  0.05  0.05  0.00 -0.05",  # 6
    " 0.00  0.00  0.05  0.05  0.05  0.05  0.00  0.00",  # 5
    " 0.00  0.00  0.05  0.05  0.05  0.05  0.00  0.00",  # 4
    "-0.05  0.00  0.05  0.05  0.05  0.05  0.00 -0.05",  # 3
    "-0.10  0.00  0.00  0.00  0.00  0.00  0.00 -0.10",  # 2
    "-0.20 -0.10 -0.05  0.00  0.00 -0.05 -0.10 -0.20",  # 1
)

_KING_MIDDLE = (
    "-0.30 -0.40 -0.40 -0.50 -0.50 -0.40 -0.40 -0.30",  # 8
    "-0.30 -0.40 -0.40 -0.50 -0.50 -0.40 -0.40 -0.30",  # 7
    "-0.30 -0.40 -0.40 -0.50 -0.50 -0.40 -0.40 -0.30",  # 6
    "-0.30 -0.30 -0.30 -0.30 -0.30 -0.30 -0.30 -0.30",  # 5
    "-0.20 -0.20 -0.20 -0.20 -0.20 -0.20 -0.20 -0.20",  # 4
    "-0.10 -0.10 -0.10 -0.10 -0.10 -0.10 -0.10 -0.10",  # 3
    " 0.20  0.20  0.00  0.00  0.00  0.00  0.20  0.20",  # 2
    " 0.20  0.30  0.10  0.00  0.00  0.10  0.30  0.20",  # 1
)
# fmt: on


def parse_location_grid(rows: tuple[str, ...]) -> tuple[float, ...]:
    """Parse rank-8-first rows into 64 modifiers indexed by bitboard square."""
    if len(rows) != 8:
        raise ValueError(f"Expected 8 rank rows, got {len(rows)}")
    values: list[float] = []
    for rank_index in range(8):
        row = rows[7 - rank_index]
        tokens = row.split()
        if len(tokens) != 8:
            raise ValueError(
                f"Rank {rank_index + 1} has {len(tokens)} values; expected 8"
            )
        for token in tokens:
            values.append(float(token))
    if len(values) != 64:
        raise ValueError(f"Expected 64 square values, got {len(values)}")
    return tuple(values)


LOCATION_BY_PIECE: dict[Piece, tuple[float, ...]] = {
    Piece.PAWN: parse_location_grid(_PAWN),
    Piece.KNIGHT: parse_location_grid(_KNIGHT),
    Piece.BISHOP: parse_location_grid(_BISHOP),
    Piece.ROOK: parse_location_grid(_ROOK),
    Piece.QUEEN: parse_location_grid(_QUEEN),
    Piece.KING: parse_location_grid(_KING_MIDDLE),
}
