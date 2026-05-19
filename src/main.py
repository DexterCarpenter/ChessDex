import sys
from models.bitboard import (
    Board,
    ChessPiece,
    Color,
    Move,
    Piece,
    Sqr,
)

TestBoard = Board()
print("\nEmpty board:")
print(TestBoard.render())

TestBoard.setup_starting_position()
print("\nStarting position:")
print(TestBoard.render())

print("\nRandom Queen appears at b5!")
TestBoard.place_piece(ChessPiece(Color.WHITE, Piece.QUEEN), Sqr("b5"))
print(TestBoard.render())
