"""PGN/FEN position I/O via python-chess (adapter for ChessDex Board)."""

from __future__ import annotations

from pathlib import Path
from typing import TextIO

import chess
import chess.pgn

from models.bitboard import (
    COLOR_LIST,
    PIECE_LIST,
    Board,
    ChessPiece,
    Color,
    Piece,
    Sqr,
)

_CHESS_COLOR_TO_COLOR = {
    chess.WHITE: Color.WHITE,
    chess.BLACK: Color.BLACK,
}
_COLOR_TO_CHESS_COLOR = {v: k for k, v in _CHESS_COLOR_TO_COLOR.items()}

_CHESS_PIECE_TO_PIECE = {
    chess.PAWN: Piece.PAWN,
    chess.KNIGHT: Piece.KNIGHT,
    chess.BISHOP: Piece.BISHOP,
    chess.ROOK: Piece.ROOK,
    chess.QUEEN: Piece.QUEEN,
    chess.KING: Piece.KING,
}
_PIECE_TO_CHESS_PIECE = {v: k for k, v in _CHESS_PIECE_TO_PIECE.items()}

_CASTLING_SORT = "KQkq"


def _piece_from_chess(piece: chess.Piece) -> ChessPiece:
    return ChessPiece(
        color=_CHESS_COLOR_TO_COLOR[piece.color],
        name=_CHESS_PIECE_TO_PIECE[piece.piece_type],
    )


def _piece_to_chess(piece: ChessPiece) -> chess.Piece:
    return chess.Piece(
        _PIECE_TO_CHESS_PIECE[piece.name],
        _COLOR_TO_CHESS_COLOR[piece.color],
    )


def _castling_frozenset(xfen: str) -> frozenset[str]:
    if xfen == "-":
        return frozenset()
    return frozenset(xfen)


def _castling_xfen(rights: frozenset[str] | None, board: Board) -> str:
    if rights is not None:
        if not rights:
            return "-"
        return "".join(sorted(rights, key=_CASTLING_SORT.index))

    parts: list[str] = []
    for color, kingside_char, queenside_char in (
        (Color.WHITE, "K", "Q"),
        (Color.BLACK, "k", "q"),
    ):
        if not board.moveLog.has_castling_rights(color):
            continue
        if board._king_on_start_square(color) and board._castling_rook_in_place(
            color, kingside=True
        ):
            parts.append(kingside_char)
        if board._king_on_start_square(color) and board._castling_rook_in_place(
            color, kingside=False
        ):
            parts.append(queenside_char)
    return "".join(parts) if parts else "-"


def apply_board_state(target: Board, source: Board) -> None:
    """Copy piece placement, turn, and FEN metadata from source onto target."""
    target.clear_board()
    for color in COLOR_LIST:
        for piece in PIECE_LIST:
            target.bitboards[(color, piece)] = source.bitboards[(color, piece)]
    target.whiteTurn = source.whiteTurn
    target.castling_rights = source.castling_rights
    target.ep_square = source.ep_square
    target._rebuild_aux_state()


def board_from_chess(cb: chess.Board) -> Board:
    """Build a ChessDex Board from a python-chess Board."""
    board = Board()
    board.clear_board()

    for square in chess.SQUARES:
        piece = cb.piece_at(square)
        if piece is not None:
            board.place_piece(_piece_from_chess(piece), Sqr(square))

    board.whiteTurn = cb.turn == chess.WHITE
    board.castling_rights = _castling_frozenset(cb.castling_xfen())
    board.ep_square = Sqr(cb.ep_square) if cb.ep_square is not None else None
    return board


def board_to_fen(board: Board) -> str:
    """Build a FEN string from a ChessDex Board (preserves EP/castling metadata)."""
    cb = chess.Board(None)
    for idx in range(64):
        piece = board.get_piece_at(Sqr(idx))
        if piece is not None:
            cb.set_piece_at(idx, _piece_to_chess(piece))

    side = "w" if board.whiteTurn else "b"
    castling = _castling_xfen(board.castling_rights, board)
    ep = board.ep_square.alg if board.ep_square is not None else "-"
    return f"{cb.board_fen()} {side} {castling} {ep} 0 1"


def chess_board_from_board(board: Board) -> chess.Board:
    """Build a python-chess Board from a ChessDex Board."""
    return chess.Board(board_to_fen(board))


def _chess_board_from_game(game: chess.pgn.Game) -> chess.Board:
    """Return the position after the mainline (or FEN setup when there are no moves)."""
    return game.end().board()


def _load_from_stream(board: Board, stream: TextIO) -> None:
    game = chess.pgn.read_game(stream)
    if game is None:
        raise ValueError("No game found in PGN source")
    apply_board_state(board, board_from_chess(_chess_board_from_game(game)))


def load_into_board(
    board: Board,
    source: str | Path | TextIO,
) -> None:
    """Load the position from the first game in a PGN file or stream.

    Uses the final position after mainline movetext, or the FEN/setup position
    when the game has no moves.
    """
    if isinstance(source, (str, Path)):
        with Path(source).open(encoding="utf-8") as stream:
            _load_from_stream(board, stream)
    else:
        _load_from_stream(board, source)


def save_board(
    board: Board,
    dest: str | Path | TextIO,
    *,
    headers: dict[str, str] | None = None,
) -> None:
    """Write the current position as a one-node PGN (SetUp/FEN when non-standard)."""
    game = chess.pgn.Game()
    fen = board_to_fen(board)
    if fen != chess.STARTING_FEN:
        game.headers["SetUp"] = "1"
        game.headers["FEN"] = fen

    if headers:
        for key, value in headers.items():
            game.headers[key] = value

    if isinstance(dest, (str, Path)):
        with Path(dest).open("w", encoding="utf-8") as stream:
            exporter = chess.pgn.FileExporter(stream)
            game.accept(exporter)
    else:
        exporter = chess.pgn.FileExporter(dest)
        game.accept(exporter)
