import pytest

from models.bitboard import (
    Board,
    ChessPiece,
    Color,
    Move,
    MoveLog,
    Piece,
    Position,
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


def test_move_log_append_and_length():
    log = MoveLog()
    move_a = Move(Sqr("e2"), Sqr("e4"))
    move_b = Move(Sqr("e7"), Sqr("e5"))

    log.append(move_a)
    log.append(move_b)

    assert len(log.moves) == 2
    assert log.moves[0] is move_a
    assert log.moves[1] is move_b


def test_move_log_undo_move():
    log = MoveLog()
    move = Move(Sqr("e2"), Sqr("e4"))
    log.append(move)

    undone = log.undo_move()
    assert undone is move
    assert len(log.moves) == 0
    assert log.undo_move() is None


def test_move_log_clear():
    log = MoveLog()
    log.append(Move(Sqr("e1"), Sqr("g1")))
    assert log.white_castled is True

    log.clear()
    assert log.moves == []
    assert log.white_castled is False
    assert log.black_castled is False


def test_move_log_castle_flags_white():
    log = MoveLog()
    log.append(Move(Sqr("e1"), Sqr("g1")))
    assert log.white_castled is True
    assert log.black_castled is False

    log.undo_move()
    assert log.white_castled is False


def test_move_log_castle_flags_black():
    log = MoveLog()
    log.append(Move(Sqr("e8"), Sqr("c8")))
    assert log.black_castled is True
    assert log.white_castled is False


def test_board_make_move_logs_half_move():
    board = Board()
    board.setup_starting_position()
    board.make_move(Move(Sqr("e2"), Sqr("e4")))
    assert len(board.moveLog.moves) == 1
    assert board.moveLog.moves[0].from_square.alg == "e2"
    assert board.moveLog.moves[0].to_square.alg == "e4"


def test_board_clear_board_resets_move_log():
    board = Board()
    board.setup_starting_position()
    board.make_move(Move(Sqr("e2"), Sqr("e4")))
    assert len(board.moveLog.moves) == 1

    board.clear_board()
    assert board.moveLog.moves == []


def test_board_setup_resets_move_log():
    board = Board()
    board.setup_starting_position()
    board.make_move(Move(Sqr("e2"), Sqr("e4")))
    assert len(board.moveLog.moves) == 1

    board.setup_starting_position()
    assert board.moveLog.moves == []


def test_clear_pieces_does_not_reset_move_log():
    board = Board()
    board.setup_starting_position()
    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    board.clear_pieces(ChessPiece(color=Color.WHITE, name=Piece.PAWN))
    assert len(board.moveLog.moves) == 1


def test_board_setup_and_move():
    board = Board()
    board.setup_starting_position()
    assert board.whiteTurn is True

    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    assert board.whiteTurn is False
    assert len(board.moveLog.moves) == 1
    assert board.get_piece_at(Sqr("e2")) is None
    moved_piece = board.get_piece_at(Sqr("e4"))
    assert moved_piece is not None
    assert moved_piece.name == Piece.PAWN
    assert moved_piece.color == Color.WHITE
    assert "♙" in board.render()


def test_board_undo_move():
    board = Board()
    board.setup_starting_position()
    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    board.undo_move()

    assert board.whiteTurn is True
    assert board.moveLog.moves == []
    pawn = board.get_piece_at(Sqr("e2"))
    assert pawn is not None
    assert pawn.name == Piece.PAWN
    assert pawn.color == Color.WHITE
    assert board.get_piece_at(Sqr("e4")) is None


def _move_algs(moves: list[Move]) -> set[tuple[str, str]]:
    return {(m.from_square.alg, m.to_square.alg) for m in moves}


def test_get_pawn_moves_starting_position_white():
    board = Board()
    board.setup_starting_position()

    moves = _move_algs(board.get_pawn_moves())

    assert len(moves) == 16
    assert ("e2", "e3") in moves
    assert ("e2", "e4") in moves
    assert ("a2", "a3") in moves
    assert ("h2", "h4") in moves


def test_get_pawn_moves_single_push():
    board = Board()
    board.setup_starting_position()
    board.make_move(Move(Sqr("e2"), Sqr("e4")))
    board.make_move(Move(Sqr("a7"), Sqr("a6")))

    moves = _move_algs(board.get_pawn_moves())

    assert ("e4", "e5") in moves
    assert ("e4", "e6") not in moves


def test_get_pawn_moves_no_double_when_blocked():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e2"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KING), Sqr("e3"))

    moves = _move_algs(board.get_pawn_moves())

    assert ("e2", "e3") not in moves
    assert ("e2", "e4") not in moves


def test_get_pawn_moves_diagonal_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("d4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("c5"))

    moves = _move_algs(board.get_pawn_moves())

    assert ("d4", "c5") in moves
    assert ("d4", "e5") not in moves


def test_get_pawn_moves_en_passant_white():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e5"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d7"))
    board.whiteTurn = False
    board.make_move(Move(Sqr("d7"), Sqr("d5")))

    moves = _move_algs(board.get_pawn_moves())

    assert ("e5", "d6") in moves


def test_get_pawn_moves_en_passant_black():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e2"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d4"))
    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    moves = _move_algs(board.get_pawn_moves())

    assert ("d4", "e3") in moves


def test_get_pawn_moves_no_en_passant_after_intervening_move():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e5"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("b1"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d7"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KNIGHT), Sqr("b8"))
    board.whiteTurn = False
    board.make_move(Move(Sqr("d7"), Sqr("d5")))
    board.make_move(Move(Sqr("b1"), Sqr("c3")))
    board.make_move(Move(Sqr("b8"), Sqr("c6")))

    moves = _move_algs(board.get_pawn_moves())

    assert ("e5", "d6") not in moves


def test_board_undo_move_restores_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("a1"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("a2"))

    board.make_move(Move(Sqr("a1"), Sqr("a2")))
    board.undo_move()

    rook = board.get_piece_at(Sqr("a1"))
    pawn = board.get_piece_at(Sqr("a2"))
    assert rook is not None
    assert rook.name == Piece.ROOK
    assert rook.color == Color.WHITE
    assert pawn is not None
    assert pawn.name == Piece.PAWN
    assert pawn.color == Color.BLACK


def test_position_default_board_is_empty():
    pos = Position()
    for row in pos.board:
        assert all(cell is None for cell in row)


@pytest.mark.parametrize(
    "square",
    ["a1", "h8", "e4", "b3"],
)
def test_position_getitem_setitem_with_sqr(square):
    pos = Position()
    piece = ChessPiece(color=Color.WHITE, name=Piece.KNIGHT)

    pos[Sqr(square)] = piece
    assert pos[Sqr(square)] is piece


def test_position_getitem_setitem_with_sqr_from_index():
    pos = Position()
    square = Sqr(28)
    piece = ChessPiece(color=Color.BLACK, name=Piece.QUEEN)

    pos[square] = piece
    assert pos[Sqr("e4")] is piece


def test_position_sqr_index_maps_to_board_coords():
    pos = Position()
    marker = object()
    square = Sqr("e4")
    pos[square] = marker

    file_index, rank_index = decomp_sqr("e4")
    assert pos.board[rank_index][file_index] is marker
    assert pos.board[square.idx // 8][square.idx % 8] is marker


def test_position_int_index_getitem_setitem_row():
    pos = Position()
    row = [ChessPiece(color=Color.WHITE, name=Piece.ROOK)] + [None] * 7

    pos[0] = row
    assert pos[0] is row
    assert pos.board[0] is row


def test_position_int_index_replaces_row_without_affecting_other_ranks():
    pos = Position()
    piece = ChessPiece(color=Color.WHITE, name=Piece.PAWN)
    custom_row = [None] * 8

    pos[Sqr("a8")] = piece
    pos[0] = custom_row

    assert pos[Sqr("a8")] is piece
    assert pos[0] is custom_row
