# LoLAramPredictor
LoLAramPredictor is the ELT process and machine learning modeling processes that power the API that predicts which team will win in a match of League of Legends ARAM game mode. 

## Table of Contents
  * [Extract Load Tansform](#extract-load-transform)
    * [Scripts](#scripts)
    * [ER Diagram](#er-diagram)
  * [Data Analysis](#data-analysis)
  * [Machine Learning]($machine-learning)
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
Each script extracts relevant game data from each respective Riot API endpoint, and loads them into the Postgres database. The raw data is then transformed into a flat table, store as a materialized view, made queryable for data analysis.

### Scripts
* [LoLChampionMasteryCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLChampMasteryCrawler) - Crawl all summoners for their champion mastery points of all the champions they have played.
* [LoLGameCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLGameCrawler) - Crawl summoner's match history for a list of ARAM matches.
* [LoLMatchCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLMatchCrawler) - Crawl each ARAM match for it's stats.
* [LoLRankCrawler](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLRankCrawler) - Crawl all summoners for their rank in Solo Queue and Flex Queue.
* [LoLSpectator](https://github.com/patrickgods1/LoLAramPredictor/tree/master/LoLSpectator) - Look up current game for each player's load in information.

### ER Diagram
![LoLMatchesDiagram](https://user-images.githubusercontent.com/60832092/145735304-e551784b-5af7-4838-a5a4-2c296d5ab0e3.png)

## Data Analysis
### AmumuRune

### APKaisa

### DrMundoVsLowDPS

### KaylePeel

### numADCWR

### Squishies

### SupportSynergy

### SynergyPairs

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