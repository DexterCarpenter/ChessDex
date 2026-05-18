from dataclasses import dataclass
from gmpy2 import mpz

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
    # Basic bit operations
    # ------------------------

    def set_piece_bit(self, piece: str, index: int) -> None:
        """Set the given piece bitboard at the given index to 1."""
        if not 0 <= index < 64:
            raise IndexError(f"Bit index out of bounds: {index}")

        if not hasattr(self, piece):
            raise AttributeError(f"Unknown piece bitboard: {piece}")

        value = getattr(self, piece)
        setattr(self, piece, mpz(value | (mpz(1) << index)) & MASK_64)


def square_to_bit(square: str) -> int:
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