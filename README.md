### Sportschau Bundesliga Physical Data

A small package to scrape the physical data for Bundesliga and Bundesliga-2 from https://www.sportschau.de/fussball/bundesliga

### Installation:
```
git clone https://github.com/znstrider/sportschau_bl_data

cd sportschau_bl_data
pip install .
```

### Usage:

```python   
spo = Sportschau()
data = spo.read_seasons()

data["2021/2022"]
```

#### Args:
    competition_id (str, optional):
        competition_id. Available id's are ["GER1", "GER2"]
        Defaults to "GER1".

    data_dir (str, optional):
        Path to save the data to.
        Defaults to home_path/sportschau_bl_data/data.


```python
spo = Sportschau(competition_id="GER2")
```


#### available seasons:
    "2016/2017",
    "2017/2018",
    "2018/2019",
    "2019/2020",
    "2020/2021",
    "2021/2022",
    "2022/2023"

```python
data = spo.read_seasons(seasons=["2021/2022"])
```


#### loading stored data:
Data is stored in Path.home() / "project_data" / "sportschau_bl_data/data"

```python
data = spo.load_data(all_comps: bool = False)
```
if all_comps is True, load data for all (ie. "GER1" and "GER2") competitions.

if you want to combine all DataFrames, use: 
```python
data = pd.concat(spo.data.values())
```


#### Columns:
    'player_name',
    'team_name',
    'games', # n total
    'duels_won', # n total
    'duels_lost', # n total
    'duels', # n total
    'duels_won_pct',
    'topspeed_kmh',
    'km', # n total
    'km_per_game',
    'sprints', # n total
    'season' # YYYY/YYYY
