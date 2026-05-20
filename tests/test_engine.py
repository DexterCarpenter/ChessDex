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


def test_eval_material_advantage(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e1"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("h1"))
    board.whiteTurn = True
    assert engine.eval(board) == 9.0


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
    assert engine.eval(board) == 4.0
    assert engine.minimax(board, 1) == 9.0


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


def test_get_best_move_returns_none_when_game_over(engine: Engine):
    board = _empty_board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KING), Sqr("h8"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("f7"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("g6"))
    board.whiteTurn = False
    assert board.is_stalemate()
    assert engine.get_best_move(board, 2) is None
