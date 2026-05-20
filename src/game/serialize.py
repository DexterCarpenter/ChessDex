"""Serialize board state for the web UI (JSON-friendly dicts)."""

from __future__ import annotations

from models.bitboard import (
    FILES,
    Board,
    ChessPiece,
    Color,
    GameOutcome,
    Move,
    Piece,
    RANKS,
    Sqr,
)
from models.engine import Engine

PIECE_API_NAMES: dict[Piece, str] = {
    Piece.KING: "king",
    Piece.QUEEN: "queen",
    Piece.ROOK: "rook",
    Piece.BISHOP: "bishop",
    Piece.KNIGHT: "knight",
    Piece.PAWN: "pawn",
}


def _piece_payload(piece: ChessPiece) -> dict[str, str]:
    return {
        "color": "white" if piece.color == Color.WHITE else "black",
        "type": PIECE_API_NAMES[piece.name],
        "symbol": piece.symbol,
    }


def board_squares(board: Board) -> list[dict[str, object]]:
    """Return 64 square records in rank 8 → rank 1 order (white POV)."""
    squares: list[dict[str, object]] = []
    for rank in range(7, -1, -1):
        for file_index in range(8):
            alg = f"{FILES[file_index]}{RANKS[rank]}"
            piece = board.get_piece_at(Sqr(alg))
            entry: dict[str, object] = {
                "sq": alg,
                "index": rank * 8 + file_index,
                "light": (file_index + rank) % 2 == 1,
            }
            if piece is not None:
                entry["piece"] = _piece_payload(piece)
            squares.append(entry)
    return squares


def move_to_api(move: Move, board: Board, *, san: str | None = None) -> dict[str, str]:
    if san is None:
        san = board.get_san(move)
    payload: dict[str, str] = {
        "from": move.from_square.alg,
        "to": move.to_square.alg,
        "san": san,
    }
    if move.promotion_piece is not None:
        from game.moves import PROMO_PIECE_LETTER

        payload["promotion"] = PROMO_PIECE_LETTER[move.promotion_piece]
    return payload


def outcome_message(board: Board) -> str | None:
    outcome = board.game_outcome()
    if outcome == GameOutcome.ONGOING:
        return None
    if outcome == GameOutcome.CHECKMATE:
        winner = "Black" if board.whiteTurn else "White"
        return f"Checkmate — {winner} wins"
    if outcome == GameOutcome.STALEMATE:
        return "Stalemate — draw"
    if outcome == GameOutcome.THREEFOLD_REPETITION:
        return "Draw by threefold repetition"
    return str(outcome)


def engine_hint(
    board: Board,
    engine: Engine,
    *,
    depth: int,
    enabled: bool,
) -> dict[str, str] | None:
    if not enabled or board.is_game_over():
        return None
    move = engine.get_best_move(board, depth)
    if move is None:
        return None
    return move_to_api(move, board)
