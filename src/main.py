import sys
from models.bitboard import Board, ChessPiece, Color, Piece

TestBoard = Board()

TestBoard.setup_starting_position()

print(TestBoard.render())

