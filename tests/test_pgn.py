from io import StringIO
from pathlib import Path

import pytest

from models.bitboard import Board, ChessPiece, Color, Piece, Sqr

FIXTURES = Path(__file__).parent / "fixtures"


def _pieces_equal(a: Board, b: Board) -> bool:
    for idx in range(64):
        if a.get_piece_at(Sqr(idx)) != b.get_piece_at(Sqr(idx)):
            return False
    return True


def test_load_starting_position():
    board = Board.from_pgn(FIXTURES / "starting.pgn")
    expected = Board()
    expected.setup_starting_position()
    assert _pieces_equal(board, expected)
    assert board.whiteTurn is True


def test_round_trip_custom_fen(tmp_path):
    board = Board.from_pgn(FIXTURES / "custom_fen.pgn")
    out = tmp_path / "out.pgn"
    board.save_to_pgn(out, headers={"Event": "RoundTrip"})

    reloaded = Board.from_pgn(out)
    assert _pieces_equal(board, reloaded)
    assert board.whiteTurn == reloaded.whiteTurn
    assert board.castling_rights == reloaded.castling_rights


def test_round_trip_with_ep(tmp_path):
    board = Board.from_pgn(FIXTURES / "with_ep.pgn")
    out = tmp_path / "ep_out.pgn"
    board.save_to_pgn(out)

    reloaded = Board.from_pgn(out)
    assert _pieces_equal(board, reloaded)
    assert board.ep_square == reloaded.ep_square
    assert board.whiteTurn == reloaded.whiteTurn


def test_castling_rights_from_fen():
    board = Board.from_pgn(FIXTURES / "custom_fen.pgn")
    assert board.castling_rights == frozenset({"K", "Q", "k", "q"})


def test_castling_rights_kingside_only():
    fen_pgn = """[SetUp "1"]
[FEN "8/8/8/8/8/8/8/R3K2R w K - 0 1"]

*
"""
    board = Board.from_pgn(StringIO(fen_pgn))
    assert board.castling_rights == frozenset({"K"})
    assert board._can_castle_kingside(Color.WHITE)
    assert not board._can_castle_queenside(Color.WHITE)


def test_ep_square_from_fen():
    board = Board.from_pgn(FIXTURES / "with_ep.pgn")
    assert board.ep_square == Sqr("e6")
    assert board._en_passant_target_index(Color.WHITE) == Sqr("e6").idx


def test_load_position_after_movetext():
    """PGN with movetext loads the final position, not the game start."""
    board = Board.from_pgn(FIXTURES / "with_moves.pgn")
    start = Board()
    start.setup_starting_position()
    assert not _pieces_equal(board, start)
    assert board.get_piece_at(Sqr("g1")) == ChessPiece(
        color=Color.WHITE, name=Piece.KING
    )
    assert board.get_piece_at(Sqr("f8")) == ChessPiece(
        color=Color.BLACK, name=Piece.KING
    )


def test_load_empty_raises():
    with pytest.raises(ValueError, match="No game found"):
        Board.from_pgn(StringIO("\n"))
