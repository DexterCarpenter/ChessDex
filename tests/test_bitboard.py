import pytest

from models.bitboard import (
    PROMOTION_PIECES,
    Board,
    ChessPiece,
    Color,
    Move,
    MoveLog,
    MoveType,
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
    assert move.promotion_piece is None
    assert move.type == MoveType.NORMAL


def test_move_promotion_initialization():
    move = Move(Sqr("e7"), Sqr("e8"), promotion_piece=Piece.QUEEN)
    assert move.promotion_piece == Piece.QUEEN
    assert move.type == MoveType.PROMOTION


@pytest.mark.parametrize("invalid_piece", [Piece.PAWN, Piece.KING])
def test_move_invalid_promotion_piece_raises(invalid_piece):
    with pytest.raises(ValueError):
        Move(Sqr("e7"), Sqr("e8"), promotion_piece=invalid_piece)


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


def _find_move(
    moves: list[Move],
    from_alg: str,
    to_alg: str,
    promotion_piece: Piece | None = None,
) -> Move | None:
    for move in moves:
        if move.from_square.alg != from_alg or move.to_square.alg != to_alg:
            continue
        if promotion_piece is not None and move.promotion_piece != promotion_piece:
            continue
        return move
    return None


def _moves_to_square(moves: list[Move], from_alg: str, to_alg: str) -> list[Move]:
    return [
        m
        for m in moves
        if m.from_square.alg == from_alg and m.to_square.alg == to_alg
    ]


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

    moves = board.get_pawn_moves()

    assert ("d4", "c5") in _move_algs(moves)
    assert ("d4", "e5") not in _move_algs(moves)
    capture = _find_move(moves, "d4", "c5")
    assert capture is not None
    assert capture.type == MoveType.NORMAL


def test_get_pawn_moves_en_passant_white():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e5"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d7"))
    board.whiteTurn = False
    board.make_move(Move(Sqr("d7"), Sqr("d5")))

    moves = board.get_pawn_moves()

    assert ("e5", "d6") in _move_algs(moves)
    ep = _find_move(moves, "e5", "d6")
    assert ep is not None
    assert ep.type == MoveType.EN_PASSANT


def test_get_pawn_moves_en_passant_black():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e2"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d4"))
    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    moves = board.get_pawn_moves()

    assert ("d4", "e3") in _move_algs(moves)
    ep = _find_move(moves, "d4", "e3")
    assert ep is not None
    assert ep.type == MoveType.EN_PASSANT


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


def test_get_pawn_moves_promotion_forward_white():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e7"))

    promo_moves = _moves_to_square(board.get_pawn_moves(), "e7", "e8")

    assert len(promo_moves) == 4
    assert {m.promotion_piece for m in promo_moves} == set(PROMOTION_PIECES)
    assert all(m.type == MoveType.PROMOTION for m in promo_moves)


def test_get_pawn_moves_promotion_forward_black():
    board = Board()
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("e2"))
    board.whiteTurn = False

    promo_moves = _moves_to_square(board.get_pawn_moves(), "e2", "e1")

    assert len(promo_moves) == 4
    assert {m.promotion_piece for m in promo_moves} == set(PROMOTION_PIECES)
    assert all(m.type == MoveType.PROMOTION for m in promo_moves)


def test_get_pawn_moves_promotion_capture_white():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e7"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("d8"))

    promo_moves = _moves_to_square(board.get_pawn_moves(), "e7", "d8")

    assert len(promo_moves) == 4
    assert {m.promotion_piece for m in promo_moves} == set(PROMOTION_PIECES)
    assert all(m.type == MoveType.PROMOTION for m in promo_moves)


def _knight_targets(moves: list[Move], from_alg: str) -> set[str]:
    return {m.to_square.alg for m in moves if m.from_square.alg == from_alg}


def test_knight_moves_from_square_empty_returns_empty():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    board.remove_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))

    assert board._knight_moves_from_square(Sqr("e4")) == []


def test_knight_moves_from_square_center_e4():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))

    moves = board._knight_moves_from_square(Sqr("e4"))

    assert _knight_targets(moves, "e4") == {
        "c3",
        "c5",
        "d2",
        "d6",
        "f2",
        "f6",
        "g3",
        "g5",
    }
    assert all(m.from_square.alg == "e4" for m in moves)
    assert all(m.type == MoveType.NORMAL for m in moves)


@pytest.mark.parametrize(
    "from_alg, expected_targets",
    [
        ("a1", {"b3", "c2"}),
        ("h8", {"f7", "g6"}),
        ("a8", {"b6", "c7"}),
    ],
)
def test_knight_moves_from_square_corners_no_wrap(from_alg, expected_targets):
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr(from_alg))

    moves = board._knight_moves_from_square(Sqr(from_alg))

    assert _knight_targets(moves, from_alg) == expected_targets


def test_knight_moves_from_square_blocks_friendly_piece():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("f6"))

    moves = board._knight_moves_from_square(Sqr("e4"))

    assert "f6" not in _knight_targets(moves, "e4")
    assert len(_knight_targets(moves, "e4")) == 7


def test_knight_moves_from_square_allows_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("f6"))

    moves = board._knight_moves_from_square(Sqr("e4"))

    assert ("e4", "f6") in _move_algs(moves)
    capture = _find_move(moves, "e4", "f6")
    assert capture is not None
    assert capture.type == MoveType.NORMAL


def test_get_knight_moves_starting_position_white():
    board = Board()
    board.setup_starting_position()

    moves = _move_algs(board.get_knight_moves())

    assert len(moves) == 4
    assert ("b1", "a3") in moves
    assert ("b1", "c3") in moves
    assert ("g1", "f3") in moves
    assert ("g1", "h3") in moves
    assert ("b1", "d2") not in moves
    assert ("g1", "f2") not in moves


def test_get_knight_moves_only_current_side():
    board = Board()
    board.setup_starting_position()
    board.whiteTurn = False

    moves = board.get_knight_moves()

    assert all(m.from_square.alg in {"b8", "g8"} for m in moves)
    assert ("b8", "a6") in _move_algs(moves)
    assert ("g8", "h6") in _move_algs(moves)


def test_get_knight_moves_ignores_opponent_knights():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.KNIGHT), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.KNIGHT), Sqr("c6"))
    board.whiteTurn = True

    moves = board.get_knight_moves()

    assert _knight_targets(moves, "e4") == {
        "c3",
        "c5",
        "d2",
        "d6",
        "f2",
        "f6",
        "g3",
        "g5",
    }
    assert _knight_targets(moves, "c6") == set()


def _bishop_targets(moves: list[Move], from_alg: str) -> set[str]:
    return {m.to_square.alg for m in moves if m.from_square.alg == from_alg}


def test_bishop_moves_from_square_empty_returns_empty():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))
    board.remove_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))

    assert board._bishop_moves_from_square(Sqr("e4")) == []


def test_bishop_moves_from_square_center_e4():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))

    moves = board._bishop_moves_from_square(Sqr("e4"))

    assert _bishop_targets(moves, "e4") == {
        "a8",
        "b1",
        "b7",
        "c2",
        "c6",
        "d3",
        "d5",
        "f3",
        "f5",
        "g2",
        "g6",
        "h1",
        "h7",
    }
    assert len(moves) == 13
    assert all(m.type == MoveType.NORMAL for m in moves)


@pytest.mark.parametrize(
    "from_alg, expected_targets",
    [
        ("a1", {"b2", "c3", "d4", "e5", "f6", "g7", "h8"}),
        ("h8", {"a1", "b2", "c3", "d4", "e5", "f6", "g7"}),
    ],
)
def test_bishop_moves_from_square_corners(from_alg, expected_targets):
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr(from_alg))

    moves = board._bishop_moves_from_square(Sqr(from_alg))

    assert _bishop_targets(moves, from_alg) == expected_targets


def test_bishop_moves_from_square_blocks_friendly_piece():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("g6"))

    targets = _bishop_targets(board._bishop_moves_from_square(Sqr("e4")), "e4")

    assert "f5" in targets
    assert "g6" not in targets
    assert "h7" not in targets


def test_bishop_moves_from_square_allows_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("g6"))

    moves = board._bishop_moves_from_square(Sqr("e4"))

    assert ("e4", "g6") in _move_algs(moves)
    assert "h7" not in _bishop_targets(moves, "e4")


def test_bishop_moves_from_square_one_ray_blocked_others_open():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("d5"))

    targets = _bishop_targets(board._bishop_moves_from_square(Sqr("e4")), "e4")

    assert "d5" not in targets
    assert "c6" not in targets
    assert "a8" not in targets
    assert "f5" in targets
    assert "h7" in targets


def test_get_bishop_moves_starting_position_white():
    board = Board()
    board.setup_starting_position()

    assert board.get_bishop_moves() == []


def test_get_bishop_moves_only_current_side():
    board = Board()
    board.setup_starting_position()
    board.whiteTurn = False

    assert board.get_bishop_moves() == []


def test_get_bishop_moves_ignores_opponent_bishops():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.BISHOP), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.BISHOP), Sqr("c6"))
    board.whiteTurn = True

    moves = board.get_bishop_moves()

    assert _bishop_targets(moves, "e4") == {
        "b1",
        "c2",
        "c6",
        "d3",
        "d5",
        "f3",
        "f5",
        "g2",
        "g6",
        "h1",
        "h7",
    }
    assert _bishop_targets(moves, "c6") == set()


def _rook_targets(moves: list[Move], from_alg: str) -> set[str]:
    return {m.to_square.alg for m in moves if m.from_square.alg == from_alg}


def test_rook_moves_from_square_empty_returns_empty():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))
    board.remove_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))

    assert board._rook_moves_from_square(Sqr("e4")) == []


def test_rook_moves_from_square_center_e4():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))

    moves = board._rook_moves_from_square(Sqr("e4"))

    assert _rook_targets(moves, "e4") == {
        "a4",
        "b4",
        "c4",
        "d4",
        "e1",
        "e2",
        "e3",
        "e5",
        "e6",
        "e7",
        "e8",
        "f4",
        "g4",
        "h4",
    }
    assert len(moves) == 14
    assert all(m.type == MoveType.NORMAL for m in moves)


@pytest.mark.parametrize(
    "from_alg, expected_targets",
    [
        ("a1", {"a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "c1", "d1", "e1", "f1", "g1", "h1"}),
        ("h8", {"a8", "b8", "c8", "d8", "e8", "f8", "g8", "h1", "h2", "h3", "h4", "h5", "h6", "h7"}),
    ],
)
def test_rook_moves_from_square_corners(from_alg, expected_targets):
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr(from_alg))

    moves = board._rook_moves_from_square(Sqr(from_alg))

    assert _rook_targets(moves, from_alg) == expected_targets


def test_rook_moves_from_square_blocks_friendly_piece():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("g4"))

    targets = _rook_targets(board._rook_moves_from_square(Sqr("e4")), "e4")

    assert "f4" in targets
    assert "g4" not in targets
    assert "h4" not in targets


def test_rook_moves_from_square_allows_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("g4"))

    moves = board._rook_moves_from_square(Sqr("e4"))

    assert ("e4", "g4") in _move_algs(moves)
    assert "h4" not in _rook_targets(moves, "e4")


def test_rook_moves_from_square_one_ray_blocked_others_open():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e6"))

    targets = _rook_targets(board._rook_moves_from_square(Sqr("e4")), "e4")

    assert "e5" in targets
    assert "e6" not in targets
    assert "e7" not in targets
    assert "e8" not in targets
    assert "h4" in targets


def test_get_rook_moves_starting_position_white():
    board = Board()
    board.setup_starting_position()

    assert board.get_rook_moves() == []


def test_get_rook_moves_only_current_side():
    board = Board()
    board.setup_starting_position()
    board.whiteTurn = False

    assert board.get_rook_moves() == []


def test_get_rook_moves_ignores_opponent_rooks():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.ROOK), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("e6"))
    board.whiteTurn = True

    moves = board.get_rook_moves()

    assert _rook_targets(moves, "e4") == {
        "a4",
        "b4",
        "c4",
        "d4",
        "e1",
        "e2",
        "e3",
        "e5",
        "e6",
        "f4",
        "g4",
        "h4",
    }
    assert _rook_targets(moves, "e6") == set()


def _queen_targets(moves: list[Move], from_alg: str) -> set[str]:
    return {m.to_square.alg for m in moves if m.from_square.alg == from_alg}


_E4_BISHOP_TARGETS = {
    "a8",
    "b1",
    "b7",
    "c2",
    "c6",
    "d3",
    "d5",
    "f3",
    "f5",
    "g2",
    "g6",
    "h1",
    "h7",
}
_E4_ROOK_TARGETS = {
    "a4",
    "b4",
    "c4",
    "d4",
    "e1",
    "e2",
    "e3",
    "e5",
    "e6",
    "e7",
    "e8",
    "f4",
    "g4",
    "h4",
}


def test_queen_moves_from_square_empty_returns_empty():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))
    board.remove_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))

    assert board._queen_moves_from_square(Sqr("e4")) == []


def test_queen_moves_from_square_center_e4():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))

    moves = board._queen_moves_from_square(Sqr("e4"))

    assert _queen_targets(moves, "e4") == _E4_BISHOP_TARGETS | _E4_ROOK_TARGETS
    assert len(moves) == 27
    assert all(m.type == MoveType.NORMAL for m in moves)


def test_queen_moves_from_square_corners_a1():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("a1"))

    moves = board._queen_moves_from_square(Sqr("a1"))

    assert _queen_targets(moves, "a1") == {
        "a2",
        "a3",
        "a4",
        "a5",
        "a6",
        "a7",
        "a8",
        "b1",
        "b2",
        "c1",
        "c3",
        "d1",
        "d4",
        "e1",
        "e5",
        "f1",
        "f6",
        "g1",
        "g7",
        "h1",
        "h8",
    }


def test_queen_moves_from_square_blocks_friendly_on_diagonal():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("g6"))

    targets = _queen_targets(board._queen_moves_from_square(Sqr("e4")), "e4")

    assert "f5" in targets
    assert "g6" not in targets
    assert "h7" not in targets
    assert "h4" in targets


def test_queen_moves_from_square_blocks_friendly_on_rank():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("g4"))

    targets = _queen_targets(board._queen_moves_from_square(Sqr("e4")), "e4")

    assert "f4" in targets
    assert "g4" not in targets
    assert "h4" not in targets
    assert "g6" in targets


def test_queen_moves_from_square_allows_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("g4"))

    moves = board._queen_moves_from_square(Sqr("e4"))

    assert ("e4", "g4") in _move_algs(moves)
    assert "h4" not in _queen_targets(moves, "e4")


def test_queen_moves_from_square_one_ray_blocked_others_open():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e6"))

    targets = _queen_targets(board._queen_moves_from_square(Sqr("e4")), "e4")

    assert "e5" in targets
    assert "e6" not in targets
    assert "e7" not in targets
    assert "h7" in targets


def test_get_queen_moves_starting_position_white():
    board = Board()
    board.setup_starting_position()

    assert board.get_queen_moves() == []


def test_get_queen_moves_only_current_side():
    board = Board()
    board.setup_starting_position()
    board.whiteTurn = False

    assert board.get_queen_moves() == []


def test_get_queen_moves_ignores_opponent_queens():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.QUEEN), Sqr("e4"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.QUEEN), Sqr("e6"))
    board.whiteTurn = True

    moves = board.get_queen_moves()

    assert _queen_targets(moves, "e4") == (
        _E4_BISHOP_TARGETS | _E4_ROOK_TARGETS
    ) - {"e7", "e8"}
    assert _queen_targets(moves, "e6") == set()


@pytest.mark.parametrize("promo", PROMOTION_PIECES)
def test_make_move_promotion_forward_white(promo):
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e7"))

    move = Move(Sqr("e7"), Sqr("e8"), promotion_piece=promo)
    board.make_move(move)

    assert move.type == MoveType.PROMOTION
    assert move.promotion_piece == promo
    assert move.moved_piece is not None
    assert move.moved_piece.name == Piece.PAWN
    assert board.get_piece_at(Sqr("e7")) is None
    piece = board.get_piece_at(Sqr("e8"))
    assert piece is not None
    assert piece.color == Color.WHITE
    assert piece.name == promo


def test_make_move_promotion_capture():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e7"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("d8"))

    move = Move(Sqr("e7"), Sqr("d8"), promotion_piece=Piece.ROOK)
    board.make_move(move)

    assert move.type == MoveType.PROMOTION
    assert move.captured_piece is not None
    assert move.captured_piece.name == Piece.ROOK
    assert board.get_piece_at(Sqr("d8")) is not None
    assert board.get_piece_at(Sqr("d8")).name == Piece.ROOK
    assert board.get_piece_at(Sqr("d8")).color == Color.WHITE


def test_board_undo_move_promotion():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e7"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.ROOK), Sqr("d8"))

    board.make_move(Move(Sqr("e7"), Sqr("d8"), promotion_piece=Piece.QUEEN))
    board.undo_move()

    assert board.whiteTurn is True
    assert board.get_piece_at(Sqr("d8")) is not None
    assert board.get_piece_at(Sqr("d8")).name == Piece.ROOK
    assert board.get_piece_at(Sqr("d8")).color == Color.BLACK
    pawn = board.get_piece_at(Sqr("e7"))
    assert pawn is not None
    assert pawn.name == Piece.PAWN
    assert pawn.color == Color.WHITE


def test_make_move_en_passant_white():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e5"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d7"))
    board.whiteTurn = False
    board.make_move(Move(Sqr("d7"), Sqr("d5")))

    ep = Move(Sqr("e5"), Sqr("d6"))
    board.make_move(ep)

    assert ep.type == MoveType.EN_PASSANT
    assert ep.captured_piece is not None
    assert ep.captured_piece.color == Color.BLACK
    assert ep.captured_piece.name == Piece.PAWN
    assert board.get_piece_at(Sqr("e5")) is None
    assert board.get_piece_at(Sqr("d5")) is None
    capturer = board.get_piece_at(Sqr("d6"))
    assert capturer is not None
    assert capturer.color == Color.WHITE
    assert capturer.name == Piece.PAWN


def test_make_move_en_passant_black():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e2"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d4"))
    board.make_move(Move(Sqr("e2"), Sqr("e4")))

    ep = Move(Sqr("d4"), Sqr("e3"))
    board.make_move(ep)

    assert ep.type == MoveType.EN_PASSANT
    assert ep.captured_piece is not None
    assert ep.captured_piece.color == Color.WHITE
    assert ep.captured_piece.name == Piece.PAWN
    assert board.get_piece_at(Sqr("d4")) is None
    assert board.get_piece_at(Sqr("e4")) is None
    capturer = board.get_piece_at(Sqr("e3"))
    assert capturer is not None
    assert capturer.color == Color.BLACK
    assert capturer.name == Piece.PAWN


def test_board_undo_move_en_passant():
    board = Board()
    board.place_piece(ChessPiece(color=Color.WHITE, name=Piece.PAWN), Sqr("e5"))
    board.place_piece(ChessPiece(color=Color.BLACK, name=Piece.PAWN), Sqr("d7"))
    board.whiteTurn = False
    board.make_move(Move(Sqr("d7"), Sqr("d5")))
    board.make_move(Move(Sqr("e5"), Sqr("d6")))

    board.undo_move()

    assert board.whiteTurn is True
    assert board.get_piece_at(Sqr("d6")) is None
    white_pawn = board.get_piece_at(Sqr("e5"))
    black_pawn = board.get_piece_at(Sqr("d5"))
    assert white_pawn is not None
    assert white_pawn.color == Color.WHITE
    assert black_pawn is not None
    assert black_pawn.color == Color.BLACK


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
