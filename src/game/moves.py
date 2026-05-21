"""Move parsing and legal-move lookup shared by CLI and UI."""

from __future__ import annotations

from models.bitboard import Board, Move, Piece, Sqr

PROMO_LETTER: dict[str, Piece] = {
    "q": Piece.QUEEN,
    "r": Piece.ROOK,
    "b": Piece.BISHOP,
    "n": Piece.KNIGHT,
}

PROMO_PIECE_LETTER: dict[Piece, str] = {v: k for k, v in PROMO_LETTER.items()}


def parse_move_input(
    line: str,
) -> tuple[str, str, Piece | None] | str:
    """Parse user input into (from_alg, to_alg, promotion) or an error message."""
    raw = line.strip().lower()
    if not raw:
        return "empty"

    promo: Piece | None = None
    if "=" in raw:
        base, suffix = raw.split("=", 1)
        raw = base.strip()
        letter = suffix.strip()[:1]
        if letter not in PROMO_LETTER:
            return f"unknown promotion piece '{suffix.strip()}' (use q, r, b, or n)"
        promo = PROMO_LETTER[letter]

    token = raw.replace("-", "").replace(" ", "")
    if len(token) >= 5 and token[-1] in PROMO_LETTER:
        promo = PROMO_LETTER[token[-1]]
        token = token[:-1]

    if len(token) == 4:
        return token[:2], token[2:], promo

    parts = raw.replace("-", " ").split()
    if len(parts) == 2 and all(len(p) == 2 for p in parts):
        return parts[0], parts[1], promo

    return "use e2e4, e2 e4, or e7e8q"


def find_legal_move(
    board: Board,
    from_alg: str,
    to_alg: str,
    promotion: Piece | None,
) -> Move | list[Move] | None:
    """Return a unique legal move, a list of promotion choices, or None."""
    legal = board.get_all_legal_moves()
    matches = [
        m
        for m in legal
        if m.from_square.alg == from_alg and m.to_square.alg == to_alg
    ]
    if not matches:
        return None

    promo_moves = [m for m in matches if m.promotion_piece is not None]
    if promo_moves:
        if promotion is not None:
            chosen = [m for m in promo_moves if m.promotion_piece == promotion]
            return chosen[0] if chosen else None
        if len(promo_moves) == 1:
            return promo_moves[0]
        return promo_moves

    non_promo = [m for m in matches if m.promotion_piece is None]
    return non_promo[0] if non_promo else matches[0]


def try_apply_move(
    board: Board,
    from_alg: str,
    to_alg: str,
    promotion: Piece | None = None,
) -> tuple[Move | None, list[Move] | None, str | None]:
    """Apply a move if legal.

    Returns (move, promotion_choices, error). Exactly one of the three tuple
    elements is non-None on success paths; on error, error is set.
    """
    try:
        Sqr(from_alg)
        Sqr(to_alg)
    except (ValueError, IndexError) as e:
        return None, None, str(e)

    result = find_legal_move(board, from_alg, to_alg, promotion)
    if result is None:
        return None, None, f"illegal move: {from_alg}{to_alg}"
    if isinstance(result, list):
        return None, result, None
    board.make_move(result)
    return result, None, None
