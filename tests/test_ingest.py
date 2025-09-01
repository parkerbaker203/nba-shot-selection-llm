# tests/test_ingest.py
import pytest
from pipelines import ingest as ing


def test_get_team_id_valid():
    team_id = ing.get_team_id("New York Knicks")
    assert isinstance(team_id, int)
    assert team_id > 0


def test_get_team_id_invalid():
    with pytest.raises(IndexError):
        # Passing a non-existent team should raise an error in current implementation
        ing.get_team_id("Fake Team")
