from pathlib import Path

import pytest
from sportschau_bl_data import Sportschau
from sportschau_bl_data.config import DATA_DIR
from sportschau_bl_data.sportschau import AVAILABLE_SEASONS

test_data_dir = Path(__file__).parents[0] / "data"


@pytest.fixture()
def sportschau() -> Sportschau:
    return Sportschau(data_dir=test_data_dir)


def test_sportschau_raises_on_unknown_comp():
    with pytest.raises(KeyError):
        Sportschau("Unknown_Comp")


def test_sportschau_data_dir(sportschau):
    assert sportschau.data_dir == test_data_dir
    sportschau = Sportschau()
    assert sportschau.data_dir == DATA_DIR


def test_sportschau(sportschau):
    assert sportschau.competition_id == "GER1"
    assert sportschau.comp == "deutschland-bundesliga"
    assert (
        sportschau.base_url
        == "https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga/statistik-laufleistung-topspeed"  # noqa
    )


def test_sportschau_data_directory(sportschau):
    sportschau.data_dir.mkdir(parents=True, exist_ok=True)
    assert sportschau.data_dir.exists()


def test_seasons(sportschau):
    sportschau.set_seasons()
    assert sorted(sportschau.seasons.keys()) == AVAILABLE_SEASONS

    season = "2021/2022"
    sportschau.read_seasons([season])

    assert list(sportschau.data.keys()) == [season]
    assert (
        sportschau.data_dir
        / f"{sportschau.competition_id}_{season.replace('/', '-')}.csv"
    ).exists()


def test_load_data(sportschau):
    sportschau.load_data()
    season = "2021/2022"

    assert list(sportschau.data.keys()) == [season]
    assert (
        sportschau.data_dir
        / f"{sportschau.competition_id}_{season.replace('/', '-')}.csv"
    ).exists()
