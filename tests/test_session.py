import pytest

from game.session import PlayMode, PlaySession
from models.bitboard import Board, Color, Piece
from models.engine import Engine


@pytest.fixture
def session() -> PlaySession:
    return PlaySession(mode=PlayMode.HUMAN_WHITE, engine_depth=2)


def test_new_game_starts_white_to_move(session: PlaySession):
    state = session.to_state()
    assert state["white_turn"] is True
    assert state["outcome"] == "ongoing"
    assert len(state["squares"]) == 64


def test_human_white_engine_replies(session: PlaySession):
    result = session.play_move("e2", "e4")
    assert result["ok"] is True
    assert session.board.moveLog.moves
    # White e4 + engine reply
    assert len(session.board.moveLog.moves) >= 2


def test_engine_hint_when_enabled(session: PlaySession):
    session.show_engine_hint = True
    hint = session.to_state()["engine_hint"]
    assert hint is not None
    assert "from" in hint and "to" in hint and "san" in hint


def test_engine_engine_step(session: PlaySession):
    session.mode = PlayMode.ENGINE_ENGINE
    session.new_game()
    state = session.to_state()
    assert state["can_human_move"] is False
    result = session.engine_step()
    assert result["ok"] is True
    assert len(session.board.moveLog.moves) == 1


def test_undo_human_vs_engine(session: PlaySession):
    session.play_move("e2", "e4")
    n = len(session.board.moveLog.moves)
    session.undo()
    assert len(session.board.moveLog.moves) < n
