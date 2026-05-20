from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TextIO

from gmpy2 import mpz

# ------------------------------------------------
# Constants and Enums
# ------------------------------------------------

MASK_64 = (1 << 64) - 1 # A mask to ensure we only use the lower 64 bits for our bitboard representation

FILES = "abcdefgh" # define the files (columns) of the chessboard
RANKS = "12345678" # define the ranks (rows) of the chessboard

class Color(Enum):
    """An enum to represent the color of a chess piece."""
    WHITE = auto()
    BLACK = auto()

class Piece(Enum):
    """An enum to represent the type of a chess piece."""
    KING     = auto()
    QUEEN    = auto()
    ROOK     = auto()
    BISHOP   = auto()
    KNIGHT   = auto()
    PAWN     = auto()

COLOR_LIST = list(Color) # A list of all colors for easy iteration when initializing the bitboards
PIECE_LIST = list(Piece) # A list of all piece types for easy iteration when initializing the bitboards
PROMOTION_PIECES = (Piece.QUEEN, Piece.ROOK, Piece.BISHOP, Piece.KNIGHT)

PIECE_SAN_LETTER = {
    Piece.KING: "K",
    Piece.QUEEN: "Q",
    Piece.ROOK: "R",
    Piece.BISHOP: "B",
    Piece.KNIGHT: "N",
}

PIECE_SYMBOL = {
    (Color.WHITE, Piece.KING):   "♔",
    (Color.WHITE, Piece.QUEEN):  "♕",
    (Color.WHITE, Piece.ROOK):   "♖",
    (Color.WHITE, Piece.BISHOP): "♗",
    (Color.WHITE, Piece.KNIGHT): "♘",
    (Color.WHITE, Piece.PAWN):   "♙",

    (Color.BLACK, Piece.KING):   "♚",
    (Color.BLACK, Piece.QUEEN):  "♛",
    (Color.BLACK, Piece.ROOK):   "♜",
    (Color.BLACK, Piece.BISHOP): "♝",
    (Color.BLACK, Piece.KNIGHT): "♞",
    (Color.BLACK, Piece.PAWN):   "♟",
}

SQUARE_SYMBOL = {
    Color.WHITE: "◻",
    Color.BLACK: "◼"
}

@dataclass(slots=True)
class ChessPiece:
    """A lightweight value object describing a chess piece with its color and type."""
    color: Color
    name: Piece

    @property
    def symbol(self) -> str:
        return PIECE_SYMBOL[(self.color, self.name)]

@dataclass(slots=True, init=False)
class Sqr:
    """A lightweight value object describing a chess square.

    Supports initialization from either an algebraic square string or a bit index.
    """
    alg: str
    idx: int
    color: Color

    def __init__(self, square: str | int):
        if isinstance(square, int):
            valid_index(square)
            self.idx = square
            self.alg = idx2sqr(square)
        else:
            self.alg = square
            self.idx = sqr2idx(square)

        self.color = Color.BLACK if ((self.idx % 8) + (self.idx // 8)) % 2 == 0 else Color.WHITE

    @property
    def file(self) -> str:
        return FILES[self.idx % 8]

    @property
    def rank(self) -> int:
        return self.idx // 8 + 1

    @property
    def symbol(self) -> str:
        return SQUARE_SYMBOL[self.color]

class MoveType(Enum):
    """An enum to represent the type of a chess move."""
    NORMAL = auto()
    CASTLE = auto()
    EN_PASSANT = auto()
    PROMOTION = auto()

class Move:
    """A lightweight value object describing a chess move.

    Stores both algebraic squares and computed bit indices for convenience.
    """

    def __init__(
        self,
        from_sqr: Sqr,
        to_sqr: Sqr,
        promotion_piece: Piece | None = None,
    ):
        self.from_square = from_sqr
        self.to_square = to_sqr
        self.moved_piece: ChessPiece | None = None
        self.captured_piece: ChessPiece | None = None
        self.promotion_piece: Piece | None = None
        self.type: MoveType = MoveType.NORMAL
        self.isLegal: bool = True

        if promotion_piece is not None:
            if promotion_piece not in PROMOTION_PIECES:
                raise ValueError(
                    f"Invalid promotion piece: {promotion_piece!r}. "
                    f"Must be one of {PROMOTION_PIECES}"
                )
            self.promotion_piece = promotion_piece
            self.type = MoveType.PROMOTION

_WHITE_KING_START = 4
_BLACK_KING_START = 60
_WHITE_ROOK_QUEENSIDE_START = 0
_WHITE_ROOK_KINGSIDE_START = 7
_BLACK_ROOK_QUEENSIDE_START = 56
_BLACK_ROOK_KINGSIDE_START = 63


def _king_start_index(color: Color) -> int:
    return _WHITE_KING_START if color == Color.WHITE else _BLACK_KING_START


def _rook_castle_start_indices(color: Color) -> tuple[int, int]:
    if color == Color.WHITE:
        return _WHITE_ROOK_QUEENSIDE_START, _WHITE_ROOK_KINGSIDE_START
    return _BLACK_ROOK_QUEENSIDE_START, _BLACK_ROOK_KINGSIDE_START


def _castle_color_for_move(move: Move) -> Color | None:
    """Return the color if the move is a king two-square slide on the back rank."""
    from_idx = move.from_square.idx
    to_idx = move.to_square.idx
    if from_idx == _WHITE_KING_START and to_idx in (6, 2):
        return Color.WHITE
    if from_idx == _BLACK_KING_START and to_idx in (62, 58):
        return Color.BLACK
    return None


@dataclass(slots=True)
class MoveLog:
    """A log of half-moves (single-side turns) played on the board."""

    moves: list[Move] = field(default_factory=list)

    def append(self, move: Move) -> None:
        self.moves.append(move)

    def undo_move(self) -> Move | None:
        if not self.moves:
            return None
        return self.moves.pop()

    def clear(self) -> None:
        self.moves.clear()

    def san_moves(self, board: Board) -> list[str]:
        """Return SAN for each half-move in this log (restores board position afterward)."""
        return board.move_history_san()

    def has_castling_rights(self, color: Color) -> bool:
        """Return True if this color has not yet moved its king or either castle rook."""
        king_start = _king_start_index(color)
        queenside_rook, kingside_rook = _rook_castle_start_indices(color)

        for move in self.moves:
            if _castle_color_for_move(move) == color:
                return False
            from_idx = move.from_square.idx
            if from_idx == king_start:
                return False
            if from_idx in (queenside_rook, kingside_rook):
                return False

        return True

@dataclass(slots=True)
class Board:
    """
    A class to represent the chess board using bitboards.

    Each piece type for both colors is represented by a separate 64-bit integer (bitboard).
    """
    bitboards: dict[tuple[Color, Piece], mpz] = field(
        default_factory=lambda: {
            (color, piece): mpz(0)
            for color in COLOR_LIST
            for piece in PIECE_LIST
        }
    )

    whiteTurn: bool = True
    moveLog: MoveLog = field(default_factory=MoveLog)
    castling_rights: frozenset[str] | None = None
    ep_square: Sqr | None = None

    def __post_init__(self):
        for key in self.bitboards:
            self.bitboards[key] &= MASK_64

    # ------------------------
    # Basic piece operations
    # ------------------------

    def place_piece(self, piece: ChessPiece, square: Sqr) -> None:
        """Set the given piece bitboard at the given index to 1."""
        valid_index(square.idx)

        key = (piece.color, piece.name)
        value = self.bitboards[key]
        self.bitboards[key] = mpz(value | (mpz(1) << square.idx)) & MASK_64
    
    def remove_piece(self, piece: ChessPiece, square: Sqr) -> None:
        """Set the given piece bitboard at the given index to 0."""
        valid_index(square.idx)

        key = (piece.color, piece.name)
        value = self.bitboards[key]
        self.bitboards[key] = mpz(value & ~(mpz(1) << square.idx)) & MASK_64

    def clear_pieces(self, piece: ChessPiece) -> None:
        """Set all bits in the given colored piece bitboard to 0."""
        key = (piece.color, piece.name)
        if key in self.bitboards:
            self.bitboards[key] = mpz(0)

    def clear_board(self) -> None:
        """Set all bits in all piece bitboards to 0."""
        for key in self.bitboards:
            self.bitboards[key] = mpz(0)
        self.moveLog.clear()
        self.castling_rights = None
        self.ep_square = None

    def get_piece_at(self, square: Sqr) -> ChessPiece | None:
        """Return the piece at the given square, or None if the square is empty."""
        index = square.idx

        for color in COLOR_LIST:
            for piece in PIECE_LIST:
                bitboard = self.bitboards[(color, piece)]
                if (bitboard >> index) & 1:
                    return ChessPiece(color=color, name=piece)

        return None

    # ------------------------
    # Board Initialization
    # ------------------------

    def setup_starting_position(self) -> None:
        """Set up the board with the standard starting position."""
        self.clear_board()

        self.bitboards[(Color.WHITE, Piece.PAWN)]   = mpz(0x000000000000FF00)
        self.bitboards[(Color.WHITE, Piece.KNIGHT)] = mpz(0x0000000000000042)
        self.bitboards[(Color.WHITE, Piece.BISHOP)] = mpz(0x0000000000000024)
        self.bitboards[(Color.WHITE, Piece.ROOK)]   = mpz(0x0000000000000081)
        self.bitboards[(Color.WHITE, Piece.QUEEN)]  = mpz(0x0000000000000008)
        self.bitboards[(Color.WHITE, Piece.KING)]   = mpz(0x0000000000000010)
        self.bitboards[(Color.BLACK, Piece.PAWN)]   = mpz(0x00FF000000000000)
        self.bitboards[(Color.BLACK, Piece.KNIGHT)] = mpz(0x4200000000000000)
        self.bitboards[(Color.BLACK, Piece.BISHOP)] = mpz(0x2400000000000000)
        self.bitboards[(Color.BLACK, Piece.ROOK)]   = mpz(0x8100000000000000)
        self.bitboards[(Color.BLACK, Piece.QUEEN)]  = mpz(0x0800000000000000)
        self.bitboards[(Color.BLACK, Piece.KING)]   = mpz(0x1000000000000000)

        self.whiteTurn = True
        self.castling_rights = None
        self.ep_square = None

    # ------------------------
    # Moves
    # ------------------------

    def make_move(self, move: Move) -> None:
        """Make a move on the board. This is a very basic implementation that does not handle special moves or validation."""
        from_square = move.from_square
        to_square = move.to_square

        moving_piece = self.get_piece_at(from_square)
        if moving_piece is None:
            raise ValueError(f"No piece to move from {from_square.alg}")
        move.moved_piece = moving_piece

        ep_target = self._en_passant_target_index(moving_piece.color)
        is_en_passant = (
            moving_piece.name == Piece.PAWN
            and ep_target is not None
            and ep_target == to_square.idx
            and abs(from_square.idx % 8 - to_square.idx % 8) == 1
        )

        is_promotion = (
            moving_piece.name == Piece.PAWN
            and (
                move.promotion_piece is not None
                or self._is_promotion_rank(moving_piece.color, to_square)
            )
        )

        is_castle = (
            moving_piece.name == Piece.KING
            and from_square.idx // 8 == to_square.idx // 8
            and abs(to_square.idx - from_square.idx) == 2
        )

        if is_en_passant:
            last = self.moveLog.moves[-1]
            capture_square = last.to_square
            captured_piece = self.get_piece_at(capture_square)
            move.captured_piece = captured_piece
            if captured_piece is not None:
                self.remove_piece(captured_piece, capture_square)
            if not is_promotion:
                move.type = MoveType.EN_PASSANT
        else:
            captured_piece = self.get_piece_at(to_square)
            move.captured_piece = captured_piece
            if captured_piece is not None:
                self.remove_piece(captured_piece, to_square)

        self.remove_piece(moving_piece, from_square)

        if is_promotion:
            move.type = MoveType.PROMOTION
            promo_piece = move.promotion_piece or Piece.QUEEN
            move.promotion_piece = promo_piece
            promoted = ChessPiece(color=moving_piece.color, name=promo_piece)
            self.place_piece(promoted, to_square)
        else:
            self.place_piece(moving_piece, to_square)

        if is_castle:
            move.type = MoveType.CASTLE
            kingside = to_square.idx > from_square.idx
            rook_from, rook_to = self._castle_rook_squares(moving_piece.color, kingside)
            rook = self.get_piece_at(rook_from)
            if rook is None or rook.name != Piece.ROOK or rook.color != moving_piece.color:
                raise ValueError(f"No rook to castle from {rook_from.alg}")
            self.remove_piece(rook, rook_from)
            self.place_piece(rook, rook_to)

        self.whiteTurn = not self.whiteTurn
        self.moveLog.append(move)

    def undo_move(self) -> None:
        """Undo the last move on the board."""
        move = self.moveLog.undo_move()
        if move is None:
            return

        from_square = move.from_square
        to_square = move.to_square

        if move.type == MoveType.CASTLE:
            if move.moved_piece is None:
                raise ValueError("Cannot undo castle without moved_piece on move")
            kingside = to_square.idx > from_square.idx
            rook_from, rook_to = self._castle_rook_squares(move.moved_piece.color, kingside)
            rook = self.get_piece_at(rook_to)
            if rook is None:
                raise ValueError(f"No rook to undo castle from {rook_to.alg}")
            self.remove_piece(rook, rook_to)
            self.place_piece(rook, rook_from)

        if move.type == MoveType.PROMOTION:
            promoted = self.get_piece_at(to_square)
            if promoted is None or move.moved_piece is None:
                raise ValueError(f"No promoted piece to undo from {to_square.alg}")
            self.remove_piece(promoted, to_square)
            pawn = ChessPiece(color=move.moved_piece.color, name=Piece.PAWN)
            self.place_piece(pawn, from_square)
        else:
            moving_piece = self.get_piece_at(to_square)
            if moving_piece is None:
                raise ValueError(f"No piece to undo from {to_square.alg}")

            self.remove_piece(moving_piece, to_square)
            self.place_piece(moving_piece, from_square)

        if move.captured_piece is not None:
            if move.type == MoveType.EN_PASSANT:
                cap_idx = (
                    to_square.idx - 8
                    if move.moved_piece is not None and move.moved_piece.color == Color.WHITE
                    else to_square.idx + 8
                )
                self.place_piece(move.captured_piece, Sqr(cap_idx))
            else:
                self.place_piece(move.captured_piece, to_square)

        self.whiteTurn = not self.whiteTurn

    def _opponent(self, color: Color) -> Color:
        """Return the opponent color."""
        return Color.BLACK if color == Color.WHITE else Color.WHITE
    
    # ------------------------
    # Pawn moves
    # ------------------------

    def _has_castling_rights(self, color: Color, *, kingside: bool) -> bool:
        """Return True if the given color may castle on the given side."""
        if self.castling_rights is not None:
            flag = ("K" if kingside else "Q") if color == Color.WHITE else ("k" if kingside else "q")
            return flag in self.castling_rights
        return self.moveLog.has_castling_rights(color)

    def _en_passant_target_index_from_log(self, color: Color) -> int | None:
        """Return the passed-over square index if the opponent just double-pushed a pawn."""
        if not self.moveLog.moves:
            return None

        last = self.moveLog.moves[-1]
        from_idx = last.from_square.idx
        to_idx = last.to_square.idx
        if from_idx % 8 != to_idx % 8 or abs(from_idx - to_idx) != 16:
            return None

        mover = self.get_piece_at(last.to_square)
        if mover is None or mover.name != Piece.PAWN or mover.color != self._opponent(color):
            return None

        return (from_idx + to_idx) // 2

    def _en_passant_target_index(self, color: Color) -> int | None:
        """Return the en passant capture target square index, if any."""
        if self.ep_square is not None:
            return self.ep_square.idx
        return self._en_passant_target_index_from_log(color)

    def _is_promotion_rank(self, color: Color, square: Sqr) -> bool:
        """Return True if the square is the back rank where a pawn promotes."""
        rank_idx = square.idx // 8
        return rank_idx == 7 if color == Color.WHITE else rank_idx == 0

    def _pawn_moves_to_square(
        self,
        color: Color,
        from_sq: Sqr,
        to_sq: Sqr,
        *,
        en_passant: bool = False,
    ) -> list[Move]:
        """Return one move, or four promotion moves, for a pawn reaching to_sq."""
        if self._is_promotion_rank(color, to_sq):
            return [Move(from_sq, to_sq, promotion_piece=p) for p in PROMOTION_PIECES]

        move = Move(from_sq, to_sq)
        if en_passant:
            move.type = MoveType.EN_PASSANT
        return [move]

    def _pawn_moves_from_square(self, color: Color, square: Sqr) -> list[Move]:
        moves: list[Move] = []
        idx = square.idx
        file_idx = idx % 8
        rank_idx = idx // 8
        opponent = self._opponent(color)

        if color == Color.WHITE:
            forward_one = idx + 8
            forward_two = idx + 16
            start_rank = 1
            capture_deltas = (7, 9)
            rank_step = 1
        else:
            forward_one = idx - 8
            forward_two = idx - 16
            start_rank = 6
            capture_deltas = (-9, -7)
            rank_step = -1

        one_ahead_rank = rank_idx + rank_step
        if 0 <= one_ahead_rank <= 7:
            one_sq = Sqr(forward_one)
            if self.get_piece_at(one_sq) is None:
                moves.extend(self._pawn_moves_to_square(color, square, one_sq))

                if rank_idx == start_rank:
                    two_sq = Sqr(forward_two)
                    if self.get_piece_at(two_sq) is None:
                        moves.append(Move(square, two_sq))

        for delta in capture_deltas:
            cap_idx = idx + delta
            if 0 <= cap_idx < 64 and abs(cap_idx % 8 - file_idx) == 1:
                cap_sq = Sqr(cap_idx)
                target = self.get_piece_at(cap_sq)
                if target is not None and target.color == opponent:
                    moves.extend(self._pawn_moves_to_square(color, square, cap_sq))

        passed_idx = self._en_passant_target_index(color)
        if passed_idx is not None:
            passed_file = passed_idx % 8
            if abs(passed_file - file_idx) == 1:
                capturer_rank = passed_idx // 8 - rank_step
                if capturer_rank == rank_idx:
                    moves.extend(
                        self._pawn_moves_to_square(
                            color, square, Sqr(passed_idx), en_passant=True
                        )
                    )

        return moves

    def get_pawn_moves(self) -> list[Move]:
        """Get all possible moves for all pawns of the color of the current turn."""
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        moves: list[Move] = []
        pawn_bb = int(self.bitboards[(color, Piece.PAWN)])

        for index in range(64):
            if (pawn_bb >> index) & 1:
                moves.extend(self._pawn_moves_from_square(color, Sqr(index)))

        return moves

    # ------------------------
    # Knight moves
    # ------------------------

    def _knight_moves_from_square(self, square: Sqr) -> list[Move]:
        """Return pseudo-legal knight moves from the given square (empty or capture targets)."""
        moves: list[Move] = []
        idx = square.idx
        file_idx = idx % 8
        rank_idx = idx // 8

        knight = self.get_piece_at(square)
        if knight is None:
            return moves

        for delta in (-17, -15, -10, -6, 6, 10, 15, 17):
            target_idx = idx + delta
            if not 0 <= target_idx < 64:
                continue

            target_file = target_idx % 8
            target_rank = target_idx // 8
            if (abs(target_file - file_idx), abs(target_rank - rank_idx)) not in (
                (1, 2),
                (2, 1),
            ):
                continue

            target_sq = Sqr(target_idx)
            target_piece = self.get_piece_at(target_sq)
            if target_piece is not None and target_piece.color == knight.color:
                continue

            moves.append(Move(square, target_sq))

        return moves

    def get_knight_moves(self) -> list[Move]:
        """Get all possible moves for all knights of the color of the current turn."""
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        moves: list[Move] = []
        knight_bb = int(self.bitboards[(color, Piece.KNIGHT)])

        for index in range(64):
            if (knight_bb >> index) & 1:
                moves.extend(self._knight_moves_from_square(Sqr(index)))

        return moves

    # ------------------------
    # Bishop moves
    # ------------------------

    def _bishop_moves_from_square(self, square: Sqr) -> list[Move]:
        """Return pseudo-legal bishop moves from the given square (empty or capture targets)."""
        moves: list[Move] = []
        bishop = self.get_piece_at(square)
        if bishop is None:
            return moves

        file_idx = square.idx % 8
        rank_idx = square.idx // 8

        for file_step, rank_step in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            f = file_idx + file_step
            r = rank_idx + rank_step
            while 0 <= f < 8 and 0 <= r < 8:
                target_sq = Sqr(r * 8 + f)
                target_piece = self.get_piece_at(target_sq)
                if target_piece is None:
                    moves.append(Move(square, target_sq))
                elif target_piece.color == bishop.color:
                    break
                else:
                    moves.append(Move(square, target_sq))
                    break
                f += file_step
                r += rank_step

        return moves

    def get_bishop_moves(self) -> list[Move]:
        """Get all possible moves for all bishops of the color of the current turn."""
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        moves: list[Move] = []
        bishop_bb = int(self.bitboards[(color, Piece.BISHOP)])

        for index in range(64):
            if (bishop_bb >> index) & 1:
                moves.extend(self._bishop_moves_from_square(Sqr(index)))

        return moves

    # ------------------------
    # Rook moves
    # ------------------------

    def _rook_moves_from_square(self, square: Sqr) -> list[Move]:
        """Return pseudo-legal rook moves from the given square (empty or capture targets)."""
        moves: list[Move] = []
        rook = self.get_piece_at(square)
        if rook is None:
            return moves

        file_idx = square.idx % 8
        rank_idx = square.idx // 8

        for file_step, rank_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            f = file_idx + file_step
            r = rank_idx + rank_step
            while 0 <= f < 8 and 0 <= r < 8:
                target_sq = Sqr(r * 8 + f)
                target_piece = self.get_piece_at(target_sq)
                if target_piece is None:
                    moves.append(Move(square, target_sq))
                elif target_piece.color == rook.color:
                    break
                else:
                    moves.append(Move(square, target_sq))
                    break
                f += file_step
                r += rank_step

        return moves

    def get_rook_moves(self) -> list[Move]:
        """Get all possible moves for all rooks of the color of the current turn."""
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        moves: list[Move] = []
        rook_bb = int(self.bitboards[(color, Piece.ROOK)])

        for index in range(64):
            if (rook_bb >> index) & 1:
                moves.extend(self._rook_moves_from_square(Sqr(index)))
        
        return moves
    
    # ------------------------
    # Queen moves
    # ------------------------

    def _queen_moves_from_square(self, square: Sqr) -> list[Move]:
        """Return pseudo-legal queen moves from the given square (bishop + rook rays)."""
        if self.get_piece_at(square) is None:
            return []
        return self._bishop_moves_from_square(square) + self._rook_moves_from_square(square)

    def get_queen_moves(self) -> list[Move]:
        """Get all possible moves for all queens of the color of the current turn."""
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        moves: list[Move] = []
        queen_bb = int(self.bitboards[(color, Piece.QUEEN)])

        for index in range(64):
            if (queen_bb >> index) & 1:
                moves.extend(self._queen_moves_from_square(Sqr(index)))

        return moves
    
    # ------------------------
    # King moves
    # ------------------------

    def _castle_rook_squares(self, color: Color, kingside: bool) -> tuple[Sqr, Sqr]:
        """Return (rook_from, rook_to) squares for a castling side."""
        if color == Color.WHITE:
            if kingside:
                return Sqr(_WHITE_ROOK_KINGSIDE_START), Sqr(5)
            return Sqr(_WHITE_ROOK_QUEENSIDE_START), Sqr(3)
        if kingside:
            return Sqr(_BLACK_ROOK_KINGSIDE_START), Sqr(61)
        return Sqr(_BLACK_ROOK_QUEENSIDE_START), Sqr(59)

    def _attacked_square_indices(self, by_color: Color) -> set[int]:
        """Return all squares attacked by the given color (excludes king moves)."""
        was_white = self.whiteTurn
        self.whiteTurn = by_color == Color.WHITE
        try:
            attacked: set[int] = set()
            for move in self.get_pawn_moves():
                attacked.add(move.to_square.idx)
            for move in self.get_knight_moves():
                attacked.add(move.to_square.idx)
            for move in self.get_bishop_moves():
                attacked.add(move.to_square.idx)
            for move in self.get_rook_moves():
                attacked.add(move.to_square.idx)
            for move in self.get_queen_moves():
                attacked.add(move.to_square.idx)
            return attacked
        finally:
            self.whiteTurn = was_white

    def _is_square_attacked(self, square: Sqr, by_color: Color) -> bool:
        return square.idx in self._attacked_square_indices(by_color)

    def _king_on_start_square(self, color: Color) -> bool:
        king_sq = Sqr(_king_start_index(color))
        piece = self.get_piece_at(king_sq)
        return piece is not None and piece.color == color and piece.name == Piece.KING

    def _castling_rook_in_place(self, color: Color, kingside: bool) -> bool:
        queenside, kingside_start = _rook_castle_start_indices(color)
        rook_idx = kingside_start if kingside else queenside
        piece = self.get_piece_at(Sqr(rook_idx))
        return piece is not None and piece.color == color and piece.name == Piece.ROOK

    def _squares_empty(self, indices: tuple[int, ...]) -> bool:
        return all(self.get_piece_at(Sqr(idx)) is None for idx in indices)

    def _castle_path_safe(
        self, color: Color, *, kingside: bool
    ) -> bool:
        """King not in check and does not pass through or land on attacked squares."""
        opponent = self._opponent(color)
        if kingside:
            if color == Color.WHITE:
                safe_indices = (_WHITE_KING_START, 5, 6)
            else:
                safe_indices = (_BLACK_KING_START, 61, 62)
        elif color == Color.WHITE:
            safe_indices = (_WHITE_KING_START, 3, 2)
        else:
            safe_indices = (_BLACK_KING_START, 59, 58)

        return all(
            not self._is_square_attacked(Sqr(idx), opponent) for idx in safe_indices
        )

    def _can_castle_kingside(self, color: Color) -> bool:
        if not self._has_castling_rights(color, kingside=True):
            return False
        if not self._king_on_start_square(color):
            return False
        if not self._castling_rook_in_place(color, kingside=True):
            return False
        if color == Color.WHITE:
            if not self._squares_empty((5, 6)):
                return False
        elif not self._squares_empty((61, 62)):
            return False
        return self._castle_path_safe(color, kingside=True)

    def _can_castle_queenside(self, color: Color) -> bool:
        if not self._has_castling_rights(color, kingside=False):
            return False
        if not self._king_on_start_square(color):
            return False
        if not self._castling_rook_in_place(color, kingside=False):
            return False
        if color == Color.WHITE:
            if not self._squares_empty((1, 2, 3)):
                return False
        elif not self._squares_empty((57, 58, 59)):
            return False
        return self._castle_path_safe(color, kingside=False)

    def _king_moves_from_square(self, square: Sqr) -> list[Move]:
        """Return pseudo-legal king moves (one step and castling) from the given square."""
        moves: list[Move] = []
        king = self.get_piece_at(square)
        if king is None or king.name != Piece.KING:
            return moves

        color = king.color
        opponent = self._opponent(color)
        file_idx = square.idx % 8
        rank_idx = square.idx // 8

        for file_step, rank_step in (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ):
            f = file_idx + file_step
            r = rank_idx + rank_step
            if not 0 <= f < 8 or not 0 <= r < 8:
                continue
            target_sq = Sqr(r * 8 + f)
            target_piece = self.get_piece_at(target_sq)
            if target_piece is not None and target_piece.color == color:
                continue
            if self._is_square_attacked(target_sq, opponent):
                continue
            moves.append(Move(square, target_sq))

        if square.idx == _king_start_index(color):
            if self._can_castle_kingside(color):
                move = Move(square, Sqr(6 if color == Color.WHITE else 62))
                move.type = MoveType.CASTLE
                moves.append(move)
            if self._can_castle_queenside(color):
                move = Move(square, Sqr(2 if color == Color.WHITE else 58))
                move.type = MoveType.CASTLE
                moves.append(move)

        return moves

    def get_king_moves(self) -> list[Move]:
        """Get all possible moves for the king of the color of the current turn."""
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        moves: list[Move] = []
        king_bb = int(self.bitboards[(color, Piece.KING)])

        for index in range(64):
            if (king_bb >> index) & 1:
                moves.extend(self._king_moves_from_square(Sqr(index)))

        return moves

    # ------------------------
    # Get all Legal Moves
    # ------------------------

    def _find_king_square(self, color: Color) -> Sqr | None:
        """Return the square of the given color's king, or None if absent."""
        king_bb = int(self.bitboards[(color, Piece.KING)])
        for index in range(64):
            if (king_bb >> index) & 1:
                return Sqr(index)
        return None

    def _is_in_check(self, color: Color) -> bool:
        """Return True if the given color's king is attacked by the opponent."""
        king_sq = self._find_king_square(color)
        if king_sq is None:
            return False
        return self._is_square_attacked(king_sq, self._opponent(color))

    def _get_all_moves(self) -> list[Move]:
        """Get all pseudo-legal moves for all pieces of the color of the current turn."""
        moves: list[Move] = []
        moves.extend(self.get_pawn_moves())
        moves.extend(self.get_knight_moves())
        moves.extend(self.get_bishop_moves())
        moves.extend(self.get_rook_moves())
        moves.extend(self.get_queen_moves())
        moves.extend(self.get_king_moves())
        return moves

    def get_all_legal_moves(self) -> list[Move]:
        """Get all legal moves for all pieces of the color of the current turn.

        Filters pseudo-legal moves by making each move and rejecting any that leave
        the moving side's king in check (pinned pieces, moving into check, etc.).
        """
        color = Color.WHITE if self.whiteTurn else Color.BLACK
        legal: list[Move] = []

        for move in self._get_all_moves():
            self.make_move(move)
            if not self._is_in_check(color):
                move.isLegal = True
                legal.append(move)
            else:
                move.isLegal = False
            self.undo_move()

        return legal

    # ------------------------
    # Serialization
    # ------------------------

    def load_from_pgn(self, source: str | Path | TextIO) -> None:
        """Load the position from the first game in a PGN file or stream."""
        from chess_io.pgn import load_into_board

        load_into_board(self, source)

    @classmethod
    def from_pgn(cls, source: str | Path | TextIO) -> Board:
        """Create a board from the position in a PGN file or stream."""
        board = cls()
        board.load_from_pgn(source)
        return board

    def save_to_pgn(
        self,
        dest: str | Path | TextIO,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Write the current position as a one-node PGN."""
        from chess_io.pgn import save_board

        save_board(self, dest, headers=headers)

    # ------------------------
    # Display
    # ------------------------

    def render(self) -> str:
        """Return a string representation of the board.

        Raises:
            ValueError: if multiple pieces occupy the same square.
        """
        piece_boards = [
            (self.bitboards[(Color.WHITE, Piece.PAWN)],   PIECE_SYMBOL[(Color.WHITE, Piece.PAWN)]),
            (self.bitboards[(Color.WHITE, Piece.KNIGHT)], PIECE_SYMBOL[(Color.WHITE, Piece.KNIGHT)]),
            (self.bitboards[(Color.WHITE, Piece.BISHOP)], PIECE_SYMBOL[(Color.WHITE, Piece.BISHOP)]),
            (self.bitboards[(Color.WHITE, Piece.ROOK)],   PIECE_SYMBOL[(Color.WHITE, Piece.ROOK)]),
            (self.bitboards[(Color.WHITE, Piece.QUEEN)],  PIECE_SYMBOL[(Color.WHITE, Piece.QUEEN)]),
            (self.bitboards[(Color.WHITE, Piece.KING)],   PIECE_SYMBOL[(Color.WHITE, Piece.KING)]),
            (self.bitboards[(Color.BLACK, Piece.PAWN)],   PIECE_SYMBOL[(Color.BLACK, Piece.PAWN)]),
            (self.bitboards[(Color.BLACK, Piece.KNIGHT)], PIECE_SYMBOL[(Color.BLACK, Piece.KNIGHT)]),
            (self.bitboards[(Color.BLACK, Piece.BISHOP)], PIECE_SYMBOL[(Color.BLACK, Piece.BISHOP)]),
            (self.bitboards[(Color.BLACK, Piece.ROOK)],   PIECE_SYMBOL[(Color.BLACK, Piece.ROOK)]),
            (self.bitboards[(Color.BLACK, Piece.QUEEN)],  PIECE_SYMBOL[(Color.BLACK, Piece.QUEEN)]),
            (self.bitboards[(Color.BLACK, Piece.KING)],   PIECE_SYMBOL[(Color.BLACK, Piece.KING)])
        ]

        square_symbols: dict[int, str] = {}
        for bitboard, symbol in piece_boards:
            for index in range(64):
                if (bitboard >> index) & 1:
                    if index in square_symbols:
                        raise ValueError(
                            f"Multiple pieces occupy square {FILES[index % 8]}{RANKS[index // 8]}"
                        )
                    square_symbols[index] = symbol

        rows: list[str] = []
        space = " "

        for rank in range(7, -1, -1):
            row_chars: list[str] = []
            for file_index in range(8):
                index = rank * 8 + file_index
                if index in square_symbols:
                    row_chars.append(square_symbols[index])
                else:
                    row_chars.append(SQUARE_SYMBOL[Color.BLACK] if (file_index + rank) % 2 == 0 else SQUARE_SYMBOL[Color.WHITE])
            rows.append(space.join(row_chars))

        return "\n".join(rows)

    def get_san(self, move: Move, *, suffix: bool = True) -> str:
        """Return Standard Algebraic Notation for a move in the current position."""
        piece = self.get_piece_at(move.from_square)
        if piece is None:
            raise ValueError(f"No piece on {move.from_square.alg}")

        moving_color = piece.color

        if piece.name == Piece.KING and abs(move.to_square.idx - move.from_square.idx) == 2:
            san = "O-O" if move.to_square.idx > move.from_square.idx else "O-O-O"
        elif piece.name == Piece.PAWN:
            san = self._san_pawn(move, piece)
        else:
            san = self._san_piece(move, piece)

        if suffix:
            san += self._san_check_suffix(move, moving_color)
        return san

    def _san_pawn(self, move: Move, piece: ChessPiece) -> str:
        to_alg = move.to_square.alg
        ep_target = self._en_passant_target_index(piece.color)
        is_en_passant = (
            move.type == MoveType.EN_PASSANT
            or (
                ep_target is not None
                and ep_target == move.to_square.idx
                and abs(move.from_square.idx % 8 - move.to_square.idx % 8) == 1
                and self.get_piece_at(move.to_square) is None
            )
        )
        captured = self.get_piece_at(move.to_square)
        is_capture = is_en_passant or (
            captured is not None and captured.color != piece.color
        )

        if is_capture:
            san = f"{move.from_square.file}x{to_alg}"
        else:
            san = to_alg

        if (
            move.type == MoveType.PROMOTION
            or move.promotion_piece is not None
            or self._is_promotion_rank(piece.color, move.to_square)
        ):
            promo = move.promotion_piece or Piece.QUEEN
            san += f"={PIECE_SAN_LETTER[promo]}"
        return san

    def _san_piece(self, move: Move, piece: ChessPiece) -> str:
        letter = PIECE_SAN_LETTER[piece.name]
        disambig = self._san_disambiguation(move, piece.name)
        captured = self.get_piece_at(move.to_square)
        is_capture = captured is not None and captured.color != piece.color

        san = letter + disambig
        if is_capture:
            san += "x"
        san += move.to_square.alg
        return san

    def _san_disambiguation(self, move: Move, piece_name: Piece) -> str:
        """File and/or rank when multiple pieces of the same type reach the same square."""
        candidates: list[Move] = []
        for candidate in self.get_all_legal_moves():
            mover = self.get_piece_at(candidate.from_square)
            if (
                mover is not None
                and mover.name == piece_name
                and candidate.to_square.idx == move.to_square.idx
            ):
                candidates.append(candidate)

        if len(candidates) <= 1:
            return ""

        files = {c.from_square.file for c in candidates}
        ranks = {c.from_square.rank for c in candidates}

        if len(files) == 1:
            return str(move.from_square.rank)
        if len(ranks) == 1:
            return move.from_square.file
        return move.from_square.alg

    def _san_check_suffix(self, move: Move, moving_color: Color) -> str:
        self.make_move(move)
        try:
            opponent = self._opponent(moving_color)
            if not self._is_in_check(opponent):
                return ""
            if not self.get_all_legal_moves():
                return "#"
            return "+"
        finally:
            self.undo_move()

    def move_history_san(self) -> list[str]:
        """Return SAN for each half-move in moveLog (board ends in the same position)."""
        moves = list(self.moveLog.moves)
        for _ in moves:
            self.undo_move()
        sans: list[str] = []
        for move in moves:
            sans.append(self.get_san(move))
            self.make_move(move)
        return sans

    def print_all_legal_moves(self) -> None:
        """Print all legal moves for the color of the current turn in SAN."""
        for move in self.get_all_legal_moves():
            print(self.get_san(move))

    def print_move_history_san(self) -> None:
        """Print moveLog half-moves as SAN, one per line."""
        for san in self.move_history_san():
            print(san)

# ------------------------------------------------
# Utility Functions
# ------------------------------------------------

def valid_index(index: int) -> bool:
    """Check if a bit index is valid (0-63)."""
    valid = True
    if not(0 <= index < 64):
        valid = False
        raise IndexError("Bit index must be in range 0-63")
    return valid

def sqr2idx(square: str) -> int:
    """
    Convert chess square notation to bit index.

    a1 -> 0
    b1 -> 1
    ...
    h8 -> 63
    """
    if len(square) != 2:
        raise ValueError(f"Invalid square: {square}")

    file_char, rank_char = square

    if file_char not in FILES:
        raise ValueError(f"Invalid file: {file_char}")

    if rank_char not in RANKS:
        raise ValueError(f"Invalid rank: {rank_char}")

    file_index = FILES.index(file_char)
    rank_index = int(rank_char) - 1

    return rank_index * 8 + file_index


def idx2sqr(index: int) -> str:
    """Convert a bit index to algebraic square notation.

    0 -> a1
    1 -> b1
    ...
    63 -> h8
    """
    valid_index(index)

    file_char = FILES[index % 8]
    rank_char = RANKS[index // 8]
    return f"{file_char}{rank_char}"


def decomp_sqr(square: str) -> list[int]:
    """Decompose a square string into file and rank indies."""
    if len(square) != 2:
        raise ValueError(f"Invalid square: {square}")

    file_char, rank_char = square

    if file_char not in FILES:
        raise ValueError(f"Invalid file: {file_char}")

    if rank_char not in RANKS:
        raise ValueError(f"Invalid rank: {rank_char}")

    file_index = FILES.index(file_char)
    rank_index = int(rank_char) - 1

    return [file_index, rank_index]


def get_san(board: Board, move: Move, *, suffix: bool = True) -> str:
    """Return Standard Algebraic Notation for a move in the given board position."""
    return board.get_san(move, suffix=suffix)