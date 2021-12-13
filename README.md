# LoLAramPredictor
LoLAramPredictor is the ELT process and machine learning modeling processes that power the API that predicts which team will win in a match of League of Legends ARAM game mode. 

## Table of Contents
  * [Extract Load Tansform](#extract-load-transform)
    * [Scripts](#scripts)
    * [ER Diagram](#er-diagram)
  * [Data Analysis](#data-analysis)
  * [Machine Learning](#machine-learning)
  * [LoLAramPredictor-API](#lolarampredictor-api)
  * [Development](#development)
    * [Built With](#built-with)
    * [Setup](#setup)
      * [Python Modules](#python-modules)
      * [Docker](#docker)
      * [Config Files](#config-files)
      * [Database Tables](#database-tables)
  * [Authors](#authors)

## Extract Load Transform
* Extract - Each script extracts relevant game data from each respective Riot API endpoint
* Load - Then the scripts load the data pulled from the API into the Postgres database. 
* Transform - The raw data is then transformed into a flat table, store as a materialized view, made queryable for data analysis.

### Scripts
* [LoLChampionMasteryCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLChampMasteryCrawler) - Crawl all summoners for their champion mastery points of all the champions they have played.
* [LoLGameCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLGameCrawler) - Crawl summoner's match history for a list of ARAM matches.
* [LoLMatchCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLMatchCrawler) - Crawl each ARAM match for it's stats.
* [LoLRankCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLRankCrawler) - Crawl all summoners for their rank in Solo Queue and Flex Queue.
* [LoLSpectator](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLSpectator) - Look up current game for each player's load in information.

### ER Diagram
![LoLMatchesDiagram](https://user-images.githubusercontent.com/60832092/145735304-e551784b-5af7-4838-a5a4-2c296d5ab0e3.png)

## Data Analysis
### Amumu Rune
<details> 
  <summary>Q: What is the win rate of ARAM games if Amumu takes Conqueror vs. Dark Harvest vs. Aftershock as the primary rune?</summary>
   A: 
   
      aftershockAmumuWR: 0.56900 [40426 / 71048]
      darkHarvestAmumuWR: 0.51438 [4399 / 8552]
      conquerorAmumuWR: 0.56547 [3256 / 5758]
</details>

### AP Kaisa vs. Squishies
<details> 
  <summary>Q: Win rate of AP Kaisa when going against an enemy team with X number of squishy champions?</summary>
   A: 
   
      Kaisa overall win rate:
      kaisaWR: 0.48011 [76160 / 158629]

      AD Kaisa overall win rate:
      adKaisaWR: 0.43484 [3153 / 7251]

      AP Kaisa overall win rate:
      apKaisaWR: 0.48228 [73007 / 151378]

      Win rate of  AP Kaisa vs. X squishy champions on enemy team:
      noSquishiesWR: 0.48316 [66380 / 137387]
      oneSquishiesWR: 0.48603 [5130 / 10555]
      twoSquishiesWR: 0.47304 [17168 / 36293]
      threeSquishiesWR: 0.47588 [27067 / 56878]
      fourSquishiesWR: 0.48056 [18739 / 38994]
      fiveSquishiesWR: 0.44848 [4422 / 9860]
   
   (Squishies = ['Ahri', 'Annie', 'Aphelios', 'Ashe', 'Aurelion Sol', 'Azir', 'Bard', 'Caitlyn', 'Cassiopeia', 'Corki', 'Draven', 'Ekko', 'Elise', 'Evelynn', 'Ezreal', 'Fizz', 'Gangplank', 'Heimerdinger', 'Janna', 'Jayce', 'Jhin', 'Jinx', "Kai'Sa", 'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Kayle', 'Kayn', 'Kennen', "Kha'Zix", 'Kindred', "Kog'Maw", 'LeBlanc', 'Lillia', 'Lucian', 'Lulu', 'Lux', 'Miss Fortune', 'Morgana', 'Nami', 'Neeko', 'Nidalee', 'Orianna', 'Pyke', 'Qiyana', 'Quinn', 'Rengar', 'Senna', 'Shaco', 'Sivir', 'Sona', 'Soraka', 'Syndra', 'Taliyah', 'Talon', 'Teemo', 'Tristana', 'Twisted Fate', 'Twitch', 'Varus', 'Vayne', 'Veigar', "Vel'Koz", 'Viktor', 'Xayah', 'Xerath', 'Yasuo', 'Yone', 'Yuumi', 'Zed', 'Ziggs', 'Zilean', 'Zoe', 'Zyra'])
</details>

### Dr. Mundo vs. Low DPS
<details> 
  <summary>Q: What is the win rate of mundo in ARAM games where there are no DPS on the enemy team?</summary>
   A: 
   
      oneLowDPSWR: 0.53736 [11586 / 21561]
      twoLowDPSWR: 0.52092 [18104 / 34754]
      threeLowDPSWR: 0.52355 [12841 / 24527]
      fourLowDPSWR: 0.54263 [4169 / 7683]
      fiveLowDPSWR: 0.58286 [510 / 875]
   
   (Lower 50th Percentile for DPS = ['Ekko', 'Yone', 'Sion', 'Shyvana', 'Kennen', 'Elise', 'Nocturne', 'Malphite', 'Gragas', 'Sett', "Kha'Zix", 'Dr. Mundo', 'Kindred', 'Kassadin', 'Olaf', 'Hecarim', 'Lee Sin', 'Vladimir', 'Vayne', 'Vi', 'Xin Zhao', 'Kayle', 'Maokai', 'Wukong', 'Kayn', 'Bard', 'Pantheon', 'Urgot', 'Gnar', 'Yasuo', 'Volibear', 'Amumu', 'Karma', 'Garen', 'Tryndamere', 'Aatrox', 'Jax', 'Ornn', 'Irelia', 'Renekton', 'Jarvan IV', 'Darius', 'Fiora', 'Yorick', 'Riven', 'Zac', 'Nunu & Willump', 'Sejuani', 'Camille', 'Kled', 'Warwick', 'Blitzcrank', 'Pyke', "Rek'Sai", 'Nautilus', 'Trundle', 'Poppy', 'Shen', 'Nami', 'Rammus', 'Tahm Kench', 'Janna', 'Soraka', 'Udyr', 'Sona', 'Thresh', 'Skarner', 'Leona', 'Alistar', 'Yuumi', 'Ivern', 'Lulu', 'Rakan', 'Braum', 'Taric'])
</details>

### Low DPS Win Rate
<details> 
  <summary>Q: What is the win rate of ARAM games where there are X number of DPS champions on the enemy team?</summary>
   A: 
   
      oneLowDPSWR: 0.49147 [367890 / 748550]
      twoLowDPSWR: 0.48951 [588506 / 1202243]
      threeLowDPSWR: 0.50587 [425354 / 840829]
      fourLowDPSWR: 0.53507 [140386 / 262371]
      fiveLowDPSWR: 0.58177 [17512 / 30101]

   (Lower 50th Percentile for DPS = ['Ekko', 'Yone', 'Sion', 'Shyvana', 'Kennen', 'Elise', 'Nocturne', 'Malphite', 'Gragas', 'Sett', "Kha'Zix", 'Dr. Mundo', 'Kindred', 'Kassadin', 'Olaf', 'Hecarim', 'Lee Sin', 'Vladimir', 'Vayne', 'Vi', 'Xin Zhao', 'Kayle', 'Maokai', 'Wukong', 'Kayn', 'Bard', 'Pantheon', 'Urgot', 'Gnar', 'Yasuo', 'Volibear', 'Amumu', 'Karma', 'Garen', 'Tryndamere', 'Aatrox', 'Jax', 'Ornn', 'Irelia', 'Renekton', 'Jarvan IV', 'Darius', 'Fiora', 'Yorick', 'Riven', 'Zac', 'Nunu & Willump', 'Sejuani', 'Camille', 'Kled', 'Warwick', 'Blitzcrank', 'Pyke', "Rek'Sai", 'Nautilus', 'Trundle', 'Poppy', 'Shen', 'Nami', 'Rammus', 'Tahm Kench', 'Janna', 'Soraka', 'Udyr', 'Sona', 'Thresh', 'Skarner', 'Leona', 'Alistar', 'Yuumi', 'Ivern', 'Lulu', 'Rakan', 'Braum', 'Taric'])
</details>

### Kayle with Peel
<details>
  <summary>Q: What is the win rate of Kayle with champions that can peel for her in ARAM games?</summary>
   A: 
   
      Kayle overall win rate:
      kayleWR: 0.51125 [1038129 / 2030563]

      Win rate of Kayle with X number of peel champions on the same team:
      noPeelWR: 0.52161 [37056 / 71041]
      onePeelWR: 0.51012 [706951 / 1385840]
      twoPeelWR: 0.51550 [255821 / 496254]
      threePeelWR: 0.49835 [36288 / 72817]
      fourPeelWR: 0.43650 [1966 / 4504]
   
   (Vanguard = ['Alistar', 'Amumu', 'Gragas', 'Leona', 'Malphite', 'Maokai', 'Nautilus', 'Nunu', 'Ornn', 'Rammus', 'Sejuani', 'Sion', 'Zac']
Warden = ['Braum', 'Galio', 'Shen', 'Poppy', 'Tahm Kench', 'Taric']
Enchanter = ['Lulu', 'Janna', 'Soraka', 'Sona', 'Nami', 'Taric', 'Yuumi', 'Karma', 'Senna'])
</details>

### Number of ADCs
<details> 
  <summary>Q: What is the relationship between the number of ADCs on your team and win rate in ARAM games?</summary>
   A: 
   
      noADCWR: 0.46122 [358570 / 777436]
      oneADCWR: 0.51703 [775562 / 1500036]
      twoADCWR: 0.51357 [409222 / 796814]
      threeADCWR: 0.47005 [72795 / 154868]
      fourADCWR: 0.38643 [4806 / 12437]
      fiveADCWR: 0.38643 [210 / 737]
      atLeastOneADCWR: 0.51223 [1262595 / 2464892]
      twoOrMoreADCWR: 0.50477 [487033 / 964856]
      threeOrMoreADCWR: 0.46304 [77811 / 168042]
      fourOrMoreADCWR: 0.38075 [5016 / 13174]
   
   (ADCs=['Aphelios', 'Ashe', 'Caitlyn', 'Corki', 'Draven', 'Ezreal', 'Graves', 'Jhin', 'Jinx', "Kai'Sa", 'Kalista', 'Kindred', "Kog'Maw", 'Lucian', 'Miss Fortune', 'Quinn', 'Senna', 'Sivir', 'Tristana', 'Twitch', 'Varus', 'Vayne', 'Xayah'])
</details>

### LeBlanc vs. Squishies
<details> 
  <summary>Q: What is the win rate of LeBlanc vs. team of X number of squishy champions? 
</summary>
   A: 

      LeBlanc overall win rate:
      LeBlancWR: 0.46682 [67222 / 143999]

      Win rate of LeBlanc vs. X squishy champions on enemy team:
      noSquishiesWR: 0.46705 [60722 / 130012]
      oneSquishiesWR: 0.48058 [4814 / 10017]
      twoSquishiesWR: 0.46826 [16052 / 34280]
      threeSquishiesWR: 0.46046 [24948 / 54181]
      fourSquishiesWR: 0.46420 [16862 / 36325]
      fiveSquishiesWR: 0.49243 [3999 / 8121]
   
   (Squishies = ['Ahri', 'Annie', 'Aphelios', 'Ashe', 'Aurelion Sol', 'Azir', 'Bard', 'Caitlyn', 'Cassiopeia', 'Corki', 'Draven', 'Ekko', 'Elise', 'Evelynn', 'Ezreal', 'Fizz', 'Gangplank', 'Heimerdinger', 'Janna', 'Jayce', 'Jhin', 'Jinx', "Kai'Sa", 'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Kayle', 'Kayn', 'Kennen', "Kha'Zix", 'Kindred', "Kog'Maw", 'LeBlanc', 'Lillia', 'Lucian', 'Lulu', 'Lux', 'Miss Fortune', 'Morgana', 'Nami', 'Neeko', 'Nidalee', 'Orianna', 'Pyke', 'Qiyana', 'Quinn', 'Rengar', 'Senna', 'Shaco', 'Sivir', 'Sona', 'Soraka', 'Syndra', 'Taliyah', 'Talon', 'Teemo', 'Tristana', 'Twisted Fate', 'Twitch', 'Varus', 'Vayne', 'Veigar', "Vel'Koz", 'Viktor', 'Xayah', 'Xerath', 'Yasuo', 'Yone', 'Yuumi', 'Zed', 'Ziggs', 'Zilean', 'Zoe', 'Zyra'])
</details>

### Number of Supports
<details> 
  <summary>Q: What is the win rate with X number of supports on your team?
</summary>
   A: noSupWR: 0.48858 [570660 / 1168007]
      oneSupWR: 0.50705 [710253 / 1400748]
      twoSupWR: 0.50826 [289621 / 569828]
      threeSupWR: 0.49196 [47514 / 96581]
      fourSupWR: 0.43973 [3068 / 6977]
      fiveSupWR: 0.43973 [48 / 188]
      atLeastOneSupWR: 0.50643 [1050504 / 2074322]
      twoOrMoreSupWR: 0.50514 [340251 / 673574]
      threeOrMoreSupWR: 0.48802 [50630 / 103746]
      fourOrMoreSupWR: 0.43489 [3116 / 7165]

  (Supports = ['Alistar', 'Bard', 'Blitzcrank', 'Braum', 'Ivern', 'Janna', 'Karma', 'Leona', 'Lulu', 'Lux', 'Morgana', 'Nami', 'Nautilus', 'Pyke', 'Rakan', 'Senna', 'Sona', 'Soraka', 'Tahm Kench', 'Taric', 'Thresh', 'Yuumi', 'Zilean', 'Zyra'])
</details>

### Synergy Pairs
<details> 
  <summary>Q: Which two champions have the highest win rate when they are on the same team?</summary>
   A: 
</details>

## Machine Learning
### Predictor


## LoLAramPredictor-API
[LoLAramPredictor-API](https://github.com/patrickgods1/LoLAramPredictor-API) is an API that serves League of Legends' ARAM game mode win prediction for each team based on a trained machine learning model. 

To use the API:
```
https://lol-aram-predictor.herokuapp.com/api/v1/summoner_name
```
Replace `summoner_name` in the URL with the player's summoner name you would like to look up and make a prediction of their current game.

## Development
These instructions will get you a copy of the project up and running on your local machine for development.

### Built With
* [Python 3.6](https://docs.python.org/3/) - The scripting language used.
* [Pandas](https://pandas.pydata.org/) - Data manipulation tool used.
* [Pantheon](https://github.com/Canisback/pantheon) - Asyncronous Python wrapper to interface with the Riot API.
* [Asyncio](https://docs.python.org/3/library/asyncio.html) - Asynchronous framework used to write concurrent code.
* [Asyncpg](https://magicstack.github.io/asyncpg/current/) - Asynchronous library used to interface with PostgreSQL.
* [CatBoost](https://catboost.ai/en/docs/) - Gradient boosting algorithm and framework used to model the data and make predictions.
* [Jupyter Notebook](https://jupyter.org/) - Interactive development environment/notebook used for data analysis and machine learning development.
* [Docker](https://www.docker.com/) - Container platform used to containerize PostgreSQL and PGAdmin.
* [PostgreSQL](https://www.postgresql.org/) - Relational database used to store extracted data.

### Setup
#### Python Modules
Run the following command to installer all the required Python modules:
```
pip install -r requirements.txt
```

#### Docker
Create a `docker-compose.yml` file under the root directory of the project with the following:
```yaml
version: "3.7"

services:
  db:
    image: postgres:12.4
    shm_size: 1gb 
    restart: always
    environment:
      POSTGRES_DB: LoLMatches
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      PGDATA: /var/lib/postgresql/data
      CONFIGS: "listen_addresses:'*'"
    volumes:
      - db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4:4.25
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: user
      PGADMIN_DEFAULT_PASSWORD: password
      PGADMIN_LISTEN_PORT: 80
    ports:
      - "80:80"
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    links:
      - "db:pgsql-server"

volumes:
  db-data:
  pgadmin-data:
```
Replace usernames and passwords to one of your own. Configurations can be changed to suit your needs.

Run the following command to start the container:
```
docker-compose up
```
Run the following command to stop the container:
```
docker-compose down
```

#### Config Files
Create a `config.py` file under each subdirectory with the following:
```python
dbConfig = {"user": 'user',
            "password": 'password',
            "host": 'host address',
            "port": 'host port',
            "database": 'LoLMatches'
           }
matchlistParams = {"champion": None,
                    "queue": 450,
                    "season": None,
                    "endTime": None,
                    "beginTime": 1605168000000,
                    "endIndex": 100,
                    "beginIndex": None
                  }
riotConfig = {"api_key": "RGAPI-XXXXXXXXXXXXXXXXXXXXXXXX",
               "apiRate": 3,
               "seedSummonerNames": ["seed1", "seed2", 
                                      "seed3", "seed4",
                                      "seed5", "seed6",
                                      "seed7", "seed8"],
                "revisitSummoners": False,
                "server": 'NA1'  
             }
```
* Under `dbConfig`:
    * user is the username to a user to read/write access to the database.
    * password is the password to a user to read/write access to the database.
    * host is address to the host of the database.
    * port is port of the host to the database.
    * database is the name of the database.
* Under `matchlistParams`:
    * champion - Set[int] - Set of champion IDs for filtering the matchlist.
    * queue - Set[int] - Set of queue IDs for filtering the matchlist. 400 - Classic, 420 - Classic, 430 - Classic, 450 - ARAM, 850 - Classic, 1300 - Nexus Blitz
    * season - Set[int]- [DEPRECATED] This field should not be considered reliable for the purposes of filtering matches by season.
    * endTime - long - The end time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
    * beginTime - long - The begin time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
    * endIndex - int - The end index to use for filtering matchlist. If beginIndex is specified, but not endIndex, then endIndex defaults to beginIndex+100. If endIndex is specified, but not beginIndex, then beginIndex defaults to 0. If both are specified, then endIndex must be greater than beginIndex. The maximum range allowed is 100, otherwise a 400 error code is returned.
    * beginIndex - int - The begin index to use for filtering matchlist. If beginIndex is specified, but not endIndex, then endIndex defaults to beginIndex+100. If endIndex is specified, but not beginIndex, then beginIndex defaults to 0. If both are specified, then endIndex must be greater than beginIndex. The maximum range allowed is 100, otherwise a 400 error code is returned.
* Under `riotConfig`:
    * api_key is Riot API key (development, personal, or production). See more [here](https://developer.riotgames.com/docs/portal).
    * apiRate is how many concurrent API calls to make per round.
    * revisitSummoners is a boolean flag for whether to look up all summoners or just those not already in the database.
    * seedSummonerNames is the seed summoner name for to start looking for matches.
    * server is the Riot server endpoint you would like to make API calls to:
        * BR1 - br1.api.riotgames.com
        * EUW1 - euw1.api.riotgames.com
        * JP1 - jp1.api.riotgames.com
        * KR - kr.api.riotgames.com
        * LA1 - la1.api.riotgames.com
        * LA2 - la2.api.riotgames.com
        * NA1 - na1.api.riotgames.com
        * OC1 - oc1.api.riotgames.com
        * TR1 - tr1.api.riotgames.com
        * RU - ru.api.riotgames.com

#### Database Tables
Run the following command to create the database tables:
```
python db-data/createTables.py
```
Run the following command to create the materialized view:
```
python db-data/game_mat_view.py
```
Run the following command to refresh the materialized view:
```
python db-data/refreshMatView.py
```

## Authors
* **Patrick Yu** - *Initial work* - [patrickgods1](https://github.com/patrickgods1)