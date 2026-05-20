from models.bitboard import (
    Board,
    ChessPiece,
    Color,
    Move,
    Piece,
    Sqr,
)

board = Board()
board.setup_starting_position()

print("ChessDex — enter moves as e2e4 (or 'e2 e4'). Commands: quit, undo")
print(board.render())
print()

while True:
    try:
        line = input("> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if not line:
        continue

    if line in ("quit", "q", "exit"):
        break

    if line in ("undo", "u"):
        board.undo_move()
        turn = "White" if board.whiteTurn else "Black"
        print(f"\n{turn} to move:\n")
        print(board.render())
        print()
        continue

    # crude parsing: e2e4 or e2 e4
    parts = line.replace("-", " ").split()
    if len(parts) == 1 and len(parts[0]) == 4:
        from_alg, to_alg = parts[0][:2], parts[0][2:]
    elif len(parts) == 2:
        from_alg, to_alg = parts[0], parts[1]
    else:
        print("  ? use e2e4 or e2 e4")
        continue

    try:
        move = Move(Sqr(from_alg), Sqr(to_alg))
        board.make_move(move)
    except (ValueError, IndexError) as e:
        print(f"  ! {e}")
        continue

    turn = "White" if board.whiteTurn else "Black"
    print(f"\n{turn} to move:\n")
    print(board.render())
    print()
