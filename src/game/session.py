"""Interactive play session: modes, engine moves, and UI-facing state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from game.moves import PROMO_PIECE_LETTER, try_apply_move
from game.serialize import (
    board_squares,
    engine_hint,
    move_to_api,
    outcome_message,
)
from models.bitboard import Board, Color, GameOutcome, Move, Piece
from models.engine import Engine


class PlayMode(str, Enum):
    HUMAN_HUMAN = "human_human"
    HUMAN_WHITE = "human_white"
    HUMAN_BLACK = "human_black"
    ENGINE_ENGINE = "engine_engine"


@dataclass
class PlaySession:
    """One game instance for the play UI."""

    mode: PlayMode = PlayMode.HUMAN_WHITE
    engine_depth: int = 3
    show_engine_hint: bool = False
    board: Board = field(default_factory=Board)
    engine: Engine = field(default_factory=Engine)
    last_move: Move | None = None

    def __post_init__(self) -> None:
        if not self.board.moveLog.moves:
            self.board.setup_starting_position()
        self._run_engine_moves()

    def new_game(
        self,
        *,
        mode: PlayMode | None = None,
        engine_depth: int | None = None,
        show_engine_hint: bool | None = None,
    ) -> None:
        if mode is not None:
            self.mode = mode
        if engine_depth is not None:
            self.engine_depth = max(1, min(engine_depth, 8))
        if show_engine_hint is not None:
            self.show_engine_hint = show_engine_hint
        self.board = Board()
        self.board.setup_starting_position()
        self.last_move = None
        self._run_engine_moves()

    def _human_colors(self) -> set[Color]:
        if self.mode == PlayMode.HUMAN_HUMAN:
            return {Color.WHITE, Color.BLACK}
        if self.mode == PlayMode.HUMAN_WHITE:
            return {Color.WHITE}
        if self.mode == PlayMode.HUMAN_BLACK:
            return {Color.BLACK}
        return set()

    def _is_human_turn(self) -> bool:
        if self.board.is_game_over():
            return False
        color = Color.WHITE if self.board.whiteTurn else Color.BLACK
        return color in self._human_colors()

    def _is_engine_turn(self) -> bool:
        if self.board.is_game_over():
            return False
        return not self._is_human_turn()

    def _run_engine_moves(self) -> Move | None:
        """Play engine moves until a human must move or the game ends."""
        if self.mode == PlayMode.ENGINE_ENGINE:
            return None
        played: Move | None = None
        while self._is_engine_turn():
            move = self.engine.get_best_move(self.board, self.engine_depth)
            if move is None:
                break
            self.board.make_move(move)
            self.last_move = move
            played = move
        return played

    def play_move(
        self,
        from_alg: str,
        to_alg: str,
        promotion: str | None = None,
    ) -> dict[str, object]:
        if not self._is_human_turn():
            return {"ok": False, "error": "Not your turn"}

        promo_piece: Piece | None = None
        if promotion:
            letter = promotion.strip().lower()[:1]
            from game.moves import PROMO_LETTER

            promo_piece = PROMO_LETTER.get(letter)

        move, choices, error = try_apply_move(
            self.board, from_alg, to_alg, promo_piece
        )
        if error:
            return {"ok": False, "error": error}
        if choices is not None:
            return {
                "ok": False,
                "needs_promotion": True,
                "from": from_alg,
                "to": to_alg,
                "promotions": [
                    PROMO_PIECE_LETTER[m.promotion_piece]
                    for m in choices
                    if m.promotion_piece is not None
                ],
            }

        assert move is not None
        self.last_move = move
        history = self.board.move_history_san()
        san = history[-1]
        engine_move = self._run_engine_moves()
        engine_payload = None
        if engine_move is not None:
            history = self.board.move_history_san()
            engine_payload = move_to_api(
                engine_move, self.board, san=history[-1]
            )
        return {
            "ok": True,
            "move": move_to_api(move, self.board, san=san),
            "engine_move": engine_payload,
        }

    def undo(self) -> bool:
        if not self.board.moveLog.moves:
            return False
        self.board.undo_move()
        if self.mode != PlayMode.HUMAN_HUMAN and self._is_engine_turn():
            self.board.undo_move()
        self.last_move = self.board.moveLog.moves[-1] if self.board.moveLog.moves else None
        return True

    def engine_step(self) -> dict[str, object]:
        """Advance one engine half-move (for engine vs engine)."""
        if self.mode != PlayMode.ENGINE_ENGINE:
            return {"ok": False, "error": "Engine step only in engine vs engine mode"}
        if not self._is_engine_turn():
            return {"ok": False, "error": "Game over or not an engine turn"}
        move = self.engine.get_best_move(self.board, self.engine_depth)
        if move is None:
            return {"ok": False, "error": "No legal moves"}
        self.board.make_move(move)
        self.last_move = move
        history = self.board.move_history_san()
        return {
            "ok": True,
            "move": move_to_api(move, self.board, san=history[-1]),
        }

    def _last_move_api(self) -> dict[str, str] | None:
        if self.last_move is None:
            return None
        history = self.board.move_history_san()
        san = history[-1] if history else ""
        return move_to_api(self.last_move, self.board, san=san)

    def legal_moves_from(self, sq_alg: str) -> list[dict[str, str]]:
        legal = self.board.get_all_legal_moves()
        return [
            move_to_api(m, self.board)
            for m in legal
            if m.from_square.alg == sq_alg
        ]

    def to_state(self, *, include_hint: bool = True) -> dict[str, object]:
        color = Color.WHITE if self.board.whiteTurn else Color.BLACK
        in_check = self.board._is_in_check(color)
        hint = None
        if include_hint:
            hint = engine_hint(
                self.board,
                self.engine,
                depth=self.engine_depth,
                enabled=self.show_engine_hint,
            )
        return {
            "mode": self.mode.value,
            "engine_depth": self.engine_depth,
            "show_engine_hint": self.show_engine_hint,
            "white_turn": self.board.whiteTurn,
            "side_to_move": "white" if self.board.whiteTurn else "black",
            "in_check": in_check,
            "outcome": self.board.game_outcome().name.lower(),
            "status": outcome_message(self.board),
            "can_human_move": self._is_human_turn(),
            "is_engine_turn": self._is_engine_turn(),
            "squares": board_squares(self.board),
            "move_history": self.board.move_history_san(),
            "last_move": self._last_move_api(),
            "engine_hint": hint,
            "flip_board": self.mode == PlayMode.HUMAN_BLACK,
        }
