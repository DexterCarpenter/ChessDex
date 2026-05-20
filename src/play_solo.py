"""Play a legal game of chess in the terminal."""

from __future__ import annotations

from models.bitboard import Board, Color, Move, Piece, Sqr

PROMO_LETTER: dict[str, Piece] = {
    "q": Piece.QUEEN,
    "r": Piece.ROOK,
    "b": Piece.BISHOP,
    "n": Piece.KNIGHT,
}


def side_to_move(board: Board) -> str:
    return "White" if board.whiteTurn else "Black"


def current_color(board: Board) -> Color:
    return Color.WHITE if board.whiteTurn else Color.BLACK


def game_result(board: Board) -> str | None:
    """Return a game-over message, or None if play continues."""
    color = current_color(board)
    if board.get_all_legal_moves():
        return None
    if board._is_in_check(color):
        winner = "White" if color == Color.BLACK else "Black"
        return f"Checkmate. {winner} wins."
    return "Stalemate. Draw."


def print_help() -> None:
    print("ChessDex — legal moves only")
    print("  Enter moves as e2e4, e2 e4, or e7e8q (promotion: q/r/b/n)")
    print("  Castling: king to g1/c1 (e.g. e1g1 or e1 g1)")
    print("  Commands: moves, undo, quit")


def print_position(board: Board) -> None:
    color = current_color(board)
    status = side_to_move(board) + " to move"
    if board._is_in_check(color):
        status += " (check)"
    print(f"\n{status}\n")
    print(board.render())
    print()


def parse_move_line(line: str) -> tuple[str, str, Piece | None] | str:
    """Parse user input into (from_alg, to_alg, promotion) or an error message."""
    raw = line.strip().lower()
    if not raw:
        return "empty"

    promo: Piece | None = None
    if "=" in raw:
        base, suffix = raw.split("=", 1)
        raw = base.strip()
        letter = suffix.strip()[:1]
        if letter not in PROMO_LETTER:
            return f"unknown promotion piece '{suffix.strip()}' (use q, r, b, or n)"
        promo = PROMO_LETTER[letter]

    token = raw.replace("-", "").replace(" ", "")
    if len(token) >= 5 and token[-1] in PROMO_LETTER:
        promo = PROMO_LETTER[token[-1]]
        token = token[:-1]

    if len(token) == 4:
        return token[:2], token[2:], promo

    parts = raw.replace("-", " ").split()
    if len(parts) == 2 and all(len(p) == 2 for p in parts):
        return parts[0], parts[1], promo

    return "use e2e4, e2 e4, or e7e8q"


def find_legal_move(
    board: Board,
    from_alg: str,
    to_alg: str,
    promotion: Piece | None,
) -> Move | list[Move] | None:
    """Return a unique legal move, a list of promotion choices, or None."""
    legal = board.get_all_legal_moves()
    matches = [
        m
        for m in legal
        if m.from_square.alg == from_alg and m.to_square.alg == to_alg
    ]
    if not matches:
        return None

    promo_moves = [m for m in matches if m.promotion_piece is not None]
    if promo_moves:
        if promotion is not None:
            chosen = [m for m in promo_moves if m.promotion_piece == promotion]
            return chosen[0] if chosen else None
        if len(promo_moves) == 1:
            return promo_moves[0]
        return promo_moves

    non_promo = [m for m in matches if m.promotion_piece is None]
    return non_promo[0] if non_promo else matches[0]


def prompt_promotion(board: Board, choices: list[Move]) -> Move | None:
    while True:
        try:
            answer = input("  Promote to (q/r/b/n)? ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if not answer:
            answer = "q"
        letter = answer[0]
        if letter not in PROMO_LETTER:
            print("  ? use q, r, b, or n")
            continue
        piece = PROMO_LETTER[letter]
        for move in choices:
            if move.promotion_piece == piece:
                return move
        print("  ? that promotion is not legal here")


def apply_user_move(board: Board, line: str) -> bool:
    """Try to parse and play one move. Return True if a move was made."""
    parsed = parse_move_line(line)
    if isinstance(parsed, str):
        print(f"  ? {parsed}")
        return False

    from_alg, to_alg, promotion = parsed
    try:
        Sqr(from_alg)
        Sqr(to_alg)
    except (ValueError, IndexError) as e:
        print(f"  ! {e}")
        return False

    result = find_legal_move(board, from_alg, to_alg, promotion)
    if result is None:
        print(f"  ! illegal move: {from_alg}{to_alg}")
        return False

    if isinstance(result, list):
        move = prompt_promotion(board, result)
        if move is None:
            return False
    else:
        move = result

    san = board.get_san(move)
    board.make_move(move)
    print(f"  {san}")
    return True


def main() -> None:
    board = Board()
    board.setup_starting_position()

    print_help()
    print_position(board)

    while True:
        result = game_result(board)
        if result is not None:
            print(result)
            break

        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        cmd = line.lower()
        if cmd in ("quit", "q", "exit"):
            break

        if cmd in ("undo", "u"):
            if not board.moveLog.moves:
                print("  (no moves to undo)")
                continue
            board.undo_move()
            print_position(board)
            continue

        if cmd in ("moves", "m", "help", "h", "?"):
            legal = board.get_all_legal_moves()
            if not legal:
                print("  (no legal moves)")
            else:
                for move in legal:
                    print(f"  {move.from_square.alg}{move.to_square.alg}", end="")
                    if move.promotion_piece is not None:
                        letter = next(
                            k for k, v in PROMO_LETTER.items() if v == move.promotion_piece
                        )
                        print(letter, end="")
                    print(f"  ({board.get_san(move)})")
            continue

        if apply_user_move(board, line):
            print_position(board)


if __name__ == "__main__":
    main()
