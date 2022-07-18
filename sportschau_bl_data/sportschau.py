import time
import warnings
from pathlib import Path
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .config import DATA_DIR, DELAY

BASE_URL = "https://www.sportschau.de/live-und-ergebnisse/fussball/"

COMPS = {"GER1": "deutschland-bundesliga", "GER2": "deutschland-2-bundesliga"}
AVAILABLE_SEASONS = [
    "2016/2017",
    "2017/2018",
    "2018/2019",
    "2019/2020",
    "2020/2021",
    "2021/2022",
    "2022/2023",
]

STATS = {
    "zweikaempfe": "statistik-zweikaempfe",
    "topspeed": "statistik-laufleistung-topspeed",
    "laufleistung": "statistik-laufleistung",
    "sprints": "statistik-laufleistung-sprints",
}

COLUMN_NAMES = {
    "Name": "player_name",
    "Mannschaft": "team_name",
    "Spiele": "games",
    "Gew.": "duels_won",
    "Verl.": "duels_lost",
    "Summe": "duels",
    "Quote %": "duels_won_pct",
    "Max. km/h": "topspeed_kmh",
    "km": "km",
    "km/Spiel": "km/game",
    "Sprints": "sprints",
}


class Sportschau:
    """Sportschau Bundesliga Data Reader for physical stats.

    ### Example:
    ------------
    ```
    spo = Sportschau()
    data = spo.read_seasons()

    data["2021/2022"]
    ```

    available competitions:
    ----------------------
    "GER1", "GER2"

    ```
    data = spo.read_seasons(competition_id="GER2")
    ```

    available seasons:
    -----------------
        "2016/2017",
        "2017/2018",
        "2018/2019",
        "2019/2020",
        "2020/2021",
        "2021/2022",
        "2022/2023"

    ```
    data = spo.read_seasons(seasons=["2021/2022"])
    ```


    Columns:
    -------
        'player_name',
        'team_name',
        'games', # n total
        'duels_won', # n total
        'duels_lost', # n total
        'duels', # n total
        'duels_won_pct',
        'topspeed_kmh',
        'km', # n total
        'km/game',
        'sprints', # n total
        'season' # YYYY/YYYY

    """

    def __init__(self, competition_id: str = "GER1", data_dir: str = DATA_DIR) -> None:
        """

        Args:
            competition_id (str, optional):
                competition_id. Available id's are ["GER1", "GER2"]
                Defaults to "GER1".
            data_dir (str, optional):
                Path to save the data to.
                Defaults to home_path/sportschau_bl_data/data.

        Raises:
            KeyError: When choosing an unknown competition name.
        """
        if competition_id not in COMPS.keys():
            raise KeyError(f"Competition not availabe. Choose one of {COMPS.keys()}")
        self.competition_id = competition_id
        self.comp = COMPS.get(competition_id)
        self.data_dir = Path(data_dir)
        self.base_url = f"{BASE_URL}{self.comp}/{STATS.get('topspeed')}"
        self.delay = DELAY

    def get_base_url(self) -> None:
        self.pagetree = requests.get(self.base_url)

    def set_seasons(self) -> Dict[str, str]:
        """Gets the available seasons from the base url in the format
            "YYYY/YYYY": "id/YYYY-YYYY"

        Returns:
            Dict[str, str]: Dict["YYYY/YYYY": "id/YYYY-YYYY"]
        """
        if not hasattr(self, "pagetree"):
            self.get_base_url()

        soup = BeautifulSoup(self.pagetree.content, "html.parser")
        select = soup.find("select", {"class": "navigation season-navigation"})

        self.seasons = {
            opt.text: "/".join(opt["value"].split("/")[4:6])
            for opt in select.find_all("option")
        }
        self.seasons = {
            season_key: v
            for season_key, v in self.seasons.items()
            if season_key in AVAILABLE_SEASONS
        }

    def _init_url_dicts(self) -> None:
        self.urls = {season: {} for season in self.seasons.keys()}

    def _set_urls(self) -> None:
        if not hasattr(self, "seasons"):
            self.set_seasons()

        if not hasattr(self, "urls"):
            self._init_url_dicts()

        for season, season_link in self.seasons.items():
            for stat, stat_link in STATS.items():
                self.urls.get(season)[
                    stat
                ] = f"{BASE_URL}{self.comp}/{season_link}/{stat_link}/"

    def read_data(self, url: str) -> pd.DataFrame:
        """Reads the data from the https://www.sportschau.de/ url.

        Args:
            url (str):
                https://www.sportschau.de/live-und-ergebnisse/fussball/deutschland-bundesliga url

        Raises:
            KeyError:

        Returns:
            pd.DataFrame:
                Bundesliga Physical Data
        """
        dfs = pd.read_html(url, decimal=",", thousands=".")
        if len(dfs) == 0:
            raise KeyError("Couldn't get data from {url}.")
        df = dfs[0]
        if "#" in df.columns:
            df = df.drop("#", axis=1)
        if "Unnamed: 1" in df.columns:
            df = df.drop("Unnamed: 1", axis=1)

        return df

    def _merge_dfs(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        df = dfs[0]
        for _df in dfs[1:]:
            if "Spiele" in _df.columns:
                _df = _df.drop("Spiele", axis=1)
            df = df.merge(_df, on=["Name", "Mannschaft"])

        df = df.rename(columns=COLUMN_NAMES)
        return df

    def save_data(self) -> None:
        """Save data to data_dir."""
        for season, df in self.data.items():
            df.to_csv(
                self.data_dir / f"{self.competition_id}_{season.replace('/', '-')}.csv"
            )

    def read_seasons(
        self, seasons: List[str] = None, save=True
    ) -> dict[str, pd.DataFrame]:
        """Read bundesliga physical data for all `season`s.

        Args:
            seasons (List[str], optional):
                List of Seasons. If None, reads data for all available seasons.
                Defaults to None.
            save (bool, optional):
                whether to save the data to data_dir. Defaults to True.

        Returns:
            dict[str, pd.DataFrame]:
                A dict of DataFrames
        """
        if not hasattr(self, "urls"):
            self._set_urls()

        if seasons is not None:
            seasons = [s for s in seasons if s in AVAILABLE_SEASONS]

        else:
            seasons = self.seasons

        self.data = {}

        for season in seasons:
            _dfs = []

            _dict = self.urls.get(season)
            for stat, url in _dict.items():
                _df = self.read_data(url)

                _dfs.append(_df)
                time.sleep(self.delay)

            try:
                df = self._merge_dfs(_dfs)
                df["season"] = season
                df["competition_id"] = self.competition_id

                self.data[season] = df

            except KeyError:
                warnings.warn(
                    f"Data for {self.competition_id} | {season} could not be read."
                )

        if save:
            self.save_data()

        return self.data

    def load_data(self, all_comps: bool = False) -> Dict[str, pd.DataFrame]:
        """Load stored data.

        Args:
            all_comps (bool, optional):
                Whether to load all stored competition data. Defaults to False.

        Returns:
            Dict[str, pd.DataFrame]:
                A dict of DataFrames
        """
        files = list(self.data_dir.glob("*.csv"))

        if all_comps:
            # KEY: "GER1_2021/2022"
            data = {
                file.stem.replace("-", "/"): pd.read_csv(file, index_col=0)
                for file in files
            }

        else:
            # KEY: "2021/2022"
            data = {
                file.stem.split("_")[1].replace("-", "/"): pd.read_csv(
                    file, index_col=0
                )
                for file in files
                if self.competition_id in file.stem
            }

        self.data = data
        return self.data
