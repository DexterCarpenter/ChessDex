import time

import pytest

from models.bitboard import (
    Board,
    ChessPiece,
    Color,
    GameOutcome,
    Move,
    Piece,
    Sqr,
)
from models.engine import Engine, MATE_SCORE


def _empty_board() -> Board:
    board = Board()
    board.clear_board()
    board.castling_rights = frozenset()
    return board


def _find_legal_move(board: Board, from_alg: str, to_alg: str) -> Move:
    for move in board.get_all_legal_moves():
        if move.from_square.alg == from_alg and move.to_square.alg == to_alg:
            return move
    raise AssertionError(f"No legal move {from_alg}{to_alg}")


@pytest.fixture
def engine() -> Engine:
    return Engine()


def test_eval_starting_position_is_zero(engine: Engine):
    board = Board()
    board.setup_starting_position()
    assert engine.eval(board) == 0.0
    assert engine.location_eval(board) == 0.0


def test_location_eval_mirrors_black_squares(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KNIGHT), Sqr("e5"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("e1"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("e8"))
    board.whiteTurn = True
    assert engine.location_eval(board) == 0.0


def test_location_eval_prefers_centered_knight(engine: Engine):
    centered = _empty_board()
    centered.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    centered.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("e1"))
    centered.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("e8"))
    centered.whiteTurn = True

    cornered = _empty_board()
    cornered.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("a1"))
    cornered.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("e1"))
    cornered.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("e8"))
    cornered.whiteTurn = True

    assert engine.location_eval(centered) > engine.location_eval(cornered)


def test_material_eval_includes_location(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("e1"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("e8"))
    board.whiteTurn = True
    assert engine._material_eval(board) == 3.0 + engine.location_eval(board)


def test_eval_material_advantage(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e1"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("h1"))
    board.whiteTurn = True
    assert board.material_score == 9.0
    assert engine.eval(board) == 9.0 + engine.location_eval(board)


def test_eval_checkmate_favors_winner(engine: Engine):
    board = Board()
    board.setup_starting_position()
    for from_alg, to_alg in (
        ("e2", "e4"),
        ("e7", "e5"),
        ("f1", "c4"),
        ("b8", "c6"),
        ("d1", "h5"),
        ("g8", "f6"),
    ):
        board.make_move(_find_legal_move(board, from_alg, to_alg))
    board.make_move(_find_legal_move(board, "h5", "f7"))
    assert board.game_outcome() == GameOutcome.CHECKMATE
    assert engine.eval(board) == MATE_SCORE


def test_eval_stalemate_is_draw(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("h8"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("f7"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("g6"))
    board.whiteTurn = False
    assert board.is_stalemate()
    assert engine.eval(board) == 0.0


def test_minimax_depth_zero_equals_eval(engine: Engine):
    board = Board()
    board.setup_starting_position()
    assert engine.minimax(board, 0) == engine.eval(board)


def test_minimax_restores_board(engine: Engine):
    board = Board()
    board.setup_starting_position()
    before = board._position_key()
    engine.minimax(board, 2)
    assert board._position_key() == before
    assert board.whiteTurn


def test_minimax_finds_winning_capture(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("a8"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("h8"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("a1"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("b1"))
    board.whiteTurn = True
    assert board.material_score == 4.0
    assert engine.eval(board) == 4.0 + engine.location_eval(board)
    winning_capture = _find_legal_move(board, "a1", "a8")
    board.make_move(winning_capture)
    expected = 9.0 + engine.location_eval(board)
    board.undo_move()
    assert engine.minimax(board, 1) == expected


def test_get_best_move_finds_winning_capture(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("a8"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("h8"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("a1"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("b1"))
    board.whiteTurn = True

    move = engine.get_best_move(board, 1)
    assert move is not None
    assert move.from_square.alg == "a1"
    assert move.to_square.alg == "a8"


def test_get_best_move_restores_board(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("a8"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("h8"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("a1"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("b1"))
    board.whiteTurn = True
    before = board._position_key()

    engine.get_best_move(board, 2)

    assert board._position_key() == before
    assert board.whiteTurn


def test_get_best_move_random_among_equal_scores(engine: Engine):
    board = Board()
    board.setup_starting_position()
    seen: set[tuple[str, str]] = set()
    for _ in range(40):
        move = engine.get_best_move(board, 1)
        assert move is not None
        seen.add((move.from_square.alg, move.to_square.alg))
    assert len(seen) > 1


def test_get_best_move_depth4_under_time_limit(engine: Engine):
    board = Board()
    board.setup_starting_position()
    t0 = time.perf_counter()
    move = engine.get_best_move(board, 4)
    elapsed = time.perf_counter() - t0
    assert move is not None
    assert elapsed < 5.0


def test_get_best_move_returns_none_when_game_over(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("h8"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("f7"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("g6"))
    board.whiteTurn = False
    assert board.is_stalemate()
    assert engine.get_best_move(board, 2) is None
