from dataclasses import dataclass
from gmpy2 import mpz
from enum import Enum

MASK_64 = (1 << 64) - 1 # A mask to ensure we only use the lower 64 bits for our bitboard representation

FILES = "abcdefgh" # define the files (columns) of the chessboard
RANKS = "12345678" # define the ranks (rows) of the chessboard

@dataclass(slots=True)
class Board:
    """
    A class to represent the chess board using bitboards.

    Each piece type for both colors is represented by a separate 64-bit integer (bitboard).
    """
    whitePawns:     mpz = mpz(0)
    whiteKnights:   mpz = mpz(0)
    whiteBishops:   mpz = mpz(0)
    whiteRooks:     mpz = mpz(0)
    whiteQueens:    mpz = mpz(0)
    whiteKing:      mpz = mpz(0)

    blackPawns:     mpz = mpz(0)
    blackKnights:   mpz = mpz(0)
    blackBishops:   mpz = mpz(0)
    blackRooks:     mpz = mpz(0)
    blackQueens:    mpz = mpz(0)
    blackKing:      mpz = mpz(0)

    whiteTurn: bool = True

    def __post_init__(self):
        self.whitePawns     &= MASK_64
        self.whiteKnights   &= MASK_64
        self.whiteBishops   &= MASK_64
        self.whiteRooks     &= MASK_64
        self.whiteQueens    &= MASK_64
        self.whiteKing      &= MASK_64

        self.blackPawns     &= MASK_64
        self.blackKnights   &= MASK_64
        self.blackBishops   &= MASK_64
        self.blackRooks     &= MASK_64
        self.blackQueens    &= MASK_64
        self.blackKing      &= MASK_64

    # ------------------------
    # Basic piece operations
    # ------------------------

    def place_piece(self, piece: str, square: str) -> None:
        """Set the given piece bitboard at the given index to 1."""
        index = sqr2idx(square)
        if not 0 <= index < 64:
            raise IndexError(f"Bit index out of bounds: {index}")

        if not hasattr(self, piece):
            raise AttributeError(f"Unknown piece bitboard: {piece}")

        value = getattr(self, piece)
        setattr(self, piece, mpz(value | (mpz(1) << index)) & MASK_64)
    
    def remove_piece(self, piece: str, square: str) -> None:
        """Set the given piece bitboard at the given index to 0."""
        index = sqr2idx(square)
        if not 0 <= index < 64:
            raise IndexError(f"Bit index out of bounds: {index}")

        if not hasattr(self, piece):
            raise AttributeError(f"Unknown piece bitboard: {piece}")

        value = getattr(self, piece)
        setattr(self, piece, mpz(value & ~(mpz(1) << index)) & MASK_64)
    
    def remove_all_pieces(self, piece: str) -> None:
        """Set all bits in the given piece bitboard to 0."""
        if not hasattr(self, piece):
            raise AttributeError(f"Unknown piece bitboard: {piece}")

        setattr(self, piece, mpz(0))

    def clear_board(self) -> None:
        """Set all bits in all piece bitboards to 0."""
        for piece in [
            "whitePawns", "whiteKnights", "whiteBishops", "whiteRooks", "whiteQueens", "whiteKing",
            "blackPawns", "blackKnights", "blackBishops", "blackRooks", "blackQueens", "blackKing"
        ]:
            self.remove_all_pieces(piece)

    # ------------------------
    # Board Initialization
    # ------------------------

    def setup_starting_position(self) -> None:
        """Set up the board with the standard starting position."""
        self.clear_board()

        self.whitePawns     = mpz(0x000000000000FF00)
        self.whiteKnights   = mpz(0x0000000000000042)
        self.whiteBishops   = mpz(0x0000000000000024)
        self.whiteRooks     = mpz(0x0000000000000081)
        self.whiteQueens    = mpz(0x0000000000000008)
        self.whiteKing      = mpz(0x0000000000000010)

        self.blackPawns     = mpz(0x00FF000000000000)
        self.blackKnights   = mpz(0x4200000000000000)
        self.blackBishops   = mpz(0x2400000000000000)
        self.blackRooks     = mpz(0x8100000000000000)
        self.blackQueens    = mpz(0x0800000000000000)
        self.blackKing      = mpz(0x1000000000000000)
    
    # ------------------------
    # Display
    # ------------------------

    def render(self) -> str:
        """Return a string representation of the board.

        Raises:
            ValueError: if multiple pieces occupy the same square.
        """
        piece_boards = [
            (self.whitePawns, PIECE_SYMBOL[(Color.WHITE, Piece.PAWN)]),
            (self.whiteKnights, PIECE_SYMBOL[(Color.WHITE, Piece.KNIGHT)]),
            (self.whiteBishops, PIECE_SYMBOL[(Color.WHITE, Piece.BISHOP)]),
            (self.whiteRooks, PIECE_SYMBOL[(Color.WHITE, Piece.ROOK)]),
            (self.whiteQueens, PIECE_SYMBOL[(Color.WHITE, Piece.QUEEN)]),
            (self.whiteKing, PIECE_SYMBOL[(Color.WHITE, Piece.KING)]),
            (self.blackPawns, PIECE_SYMBOL[(Color.BLACK, Piece.PAWN)]),
            (self.blackKnights, PIECE_SYMBOL[(Color.BLACK, Piece.KNIGHT)]),
            (self.blackBishops, PIECE_SYMBOL[(Color.BLACK, Piece.BISHOP)]),
            (self.blackRooks, PIECE_SYMBOL[(Color.BLACK, Piece.ROOK)]),
            (self.blackQueens, PIECE_SYMBOL[(Color.BLACK, Piece.QUEEN)]),
            (self.blackKing, PIECE_SYMBOL[(Color.BLACK, Piece.KING)]),
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
                    row_chars.append("◼" if (file_index + rank) % 2 == 0 else "◻")
            rows.append(space.join(row_chars))

        return "\n".join(rows)

    # ------------------------
    # Validation
    # ------------------------

    @staticmethod
    def _validate_index(index: int) -> None:
        if not (0 <= index < 64):
            raise IndexError("Bit index must be in range 0-63")


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


class Color(Enum):
    WHITE = 0
    BLACK = 1

class Piece(Enum):
    KING = "k"
    QUEEN = "q"
    ROOK = "r"
    BISHOP = "b"
    KNIGHT = "n"
    PAWN = "p"

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

@dataclass(slots=True)
class ChessPiece:
    color: Color
    kind: Piece

    @property
    def symbol(self) -> str:
        return PIECE_SYMBOL[(self.color, self.kind)]