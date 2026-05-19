import pytest

from models.bitboard import (
    Board,
    ChessPiece,
    Color,
    Move,
    Piece,
    Sqr,
    decomp_sqr,
    idx2sqr,
    valid_index,
    sqr2idx,
)


@pytest.mark.parametrize(
    "square, expected",
    [
        ("a1", 0),
        ("h1", 7),
        ("a8", 56),
        ("h8", 63),
        ("e4", 28),
    ],
)
def test_sqr2idx_valid(square, expected):
    assert sqr2idx(square) == expected


@pytest.mark.parametrize(
    "index, expected",
    [
        (0, "a1"),
        (7, "h1"),
        (56, "a8"),
        (63, "h8"),
        (28, "e4"),
    ],
)
def test_idx2sqr_valid(index, expected):
    assert idx2sqr(index) == expected


@pytest.mark.parametrize(
    "square, expected",
    [
        ("a1", [0, 0]),
        ("h1", [7, 0]),
        ("a8", [0, 7]),
        ("e4", [4, 3]),
    ],
)
def test_decomp_sqr_valid(square, expected):
    assert decomp_sqr(square) == expected


@pytest.mark.parametrize(
    "invalid_square",
    ["", "a0", "i1", "a9", "z3", "a1a"],
)
def test_sqr2idx_invalid_raises_value_error(invalid_square):
    with pytest.raises(ValueError):
        sqr2idx(invalid_square)


@pytest.mark.parametrize("invalid_index", [-1, 64, 999])
def test_idx2sqr_invalid_raises_index_error(invalid_index):
    with pytest.raises(IndexError):
        idx2sqr(invalid_index)


@pytest.mark.parametrize("index", [0, 1, 31, 63])
def test_index_is_valid_returns_true(index):
    assert valid_index(index) is True


@pytest.mark.parametrize("invalid_index", [-1, 64])
def test_index_is_valid_invalid_raises_index_error(invalid_index):
    with pytest.raises(IndexError):
        valid_index(invalid_index)


def test_chesspiece_symbol():
    piece = ChessPiece(color=Color.WHITE, name=Piece.KING)
    assert piece.symbol == "♔"

    piece = ChessPiece(color=Color.BLACK, name=Piece.QUEEN)
    assert piece.symbol == "♛"


def test_move_initialization():
    move = Move(Sqr("a2"), Sqr("a4"))
    assert isinstance(move.from_square, Sqr)
    assert isinstance(move.to_square, Sqr)
    assert move.from_square.alg == "a2"
    assert move.to_square.alg == "a4"
    assert move.from_square.idx == sqr2idx("a2")
    assert move.to_square.idx == sqr2idx("a4")


def test_sqr_init_from_algebraic():
    square = Sqr("b3")
    assert square.alg == "b3"
    assert square.idx == 17
    assert square.file == "b"
    assert square.rank == 3
    assert square.color == Color.WHITE


def test_sqr_init_from_index():
    square = Sqr(0)
    assert square.alg == "a1"
    assert square.idx == 0


@pytest.mark.parametrize("value", [64, -1])
def test_sqr_init_from_index_raises_index_error(value):
    with pytest.raises(IndexError):
        Sqr(value)


@pytest.mark.parametrize("invalid_square", ["", "i2", "a0", "a9"])
def test_sqr_init_from_alg_raises_value_error(invalid_square):
    with pytest.raises(ValueError):
        Sqr(invalid_square)


def test_board_default_state():
    board = Board()
    assert board.whiteTurn is True
    assert isinstance(board.bitboards, dict)
    for value in board.bitboards.values():
        assert value == 0


def test_board_place_and_remove_piece():
    board = Board()
    pawn = ChessPiece(color=Color.WHITE, name=Piece.PAWN)
    square = Sqr("a2")

    board.place_piece(pawn, square)
    current = board.get_piece_at(square)
    assert current is not None
    assert current.name == Piece.PAWN
    assert current.color == Color.WHITE

    board.remove_piece(pawn, square)
    assert board.get_piece_at(square) is None


def test_board_setup_and_move():
    board = Board()
    board.setup_starting_position()
    assert board.whiteTurn is True

    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    assert board.whiteTurn is False
    assert board.get_piece_at(Sqr("e2")) is None
    moved_piece = board.get_piece_at(Sqr("e4"))
    assert moved_piece is not None
    assert moved_piece.name == Piece.PAWN
    assert moved_piece.color == Color.WHITE
    assert "♙" in board.render()
