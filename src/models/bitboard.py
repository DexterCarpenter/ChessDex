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

class Move:
    """A lightweight value object describing a chess move.

    Stores both algebraic squares and computed bit indices for convenience.
    """

    def __init__(self, from_sqr: Sqr, to_sqr: Sqr):
        # keep original square strings
        self.from_square = from_sqr
        self.to_square = to_sqr

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

        captured_piece = self.get_piece_at(to_square)
        if captured_piece is not None:
            self.remove_piece(captured_piece, to_square)

        self.remove_piece(moving_piece, from_square)
        self.place_piece(moving_piece, to_square)

        self.whiteTurn = not self.whiteTurn

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