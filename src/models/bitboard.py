from dataclasses import dataclass, field
from gmpy2 import mpz
from enum import Enum, auto

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

def _castle_color_for_move(move: Move) -> Color | None:
    """Return the castling side if the move is a king two-square slide on the back rank."""
    from_idx = move.from_square.idx
    to_idx = move.to_square.idx
    if from_idx == 4 and to_idx in (6, 2):
        return Color.WHITE
    if from_idx == 60 and to_idx in (62, 58):
        return Color.BLACK
    return None

@dataclass(slots=True)
class MoveLog:
    """A log of half-moves (single-side turns) played on the board."""

    moves: list[Move] = field(default_factory=list)
    white_castled: bool = False
    black_castled: bool = False

    def append(self, move: Move) -> None:
        self.moves.append(move)
        self._recompute_castle_flags()

    def undo_move(self) -> Move | None:
        if not self.moves:
            return None
        move = self.moves.pop()
        self._recompute_castle_flags()
        return move

    def clear(self) -> None:
        self.moves.clear()
        self.white_castled = False
        self.black_castled = False

    def _recompute_castle_flags(self) -> None:
        self.white_castled = False
        self.black_castled = False
        for move in self.moves:
            color = _castle_color_for_move(move)
            if color == Color.WHITE:
                self.white_castled = True
            elif color == Color.BLACK:
                self.black_castled = True

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

        self.whiteTurn = not self.whiteTurn
        self.moveLog.append(move)

    def undo_move(self) -> None:
        """Undo the last move on the board."""
        move = self.moveLog.undo_move()
        if move is None:
            return

        from_square = move.from_square
        to_square = move.to_square

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

    def _en_passant_target_index(self, color: Color) -> int | None:
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