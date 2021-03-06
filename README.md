# LoLAramPredictor
LoLAramPredictor is the ELT process and machine learning modeling processes that power the API that predicts which team will win in a match of League of Legends ARAM game mode. 

## Table of Contents
  * [Extract Load Tansform](#extract-load-transform)
    * [Scripts](#scripts)
    * [ER Diagram](#er-diagram)
  * [Data Analysis](#data-analysis)
  * [Machine Learning](#machine-learning)
    * [Preprocessing](#preprocessing)
    * [Models](#models)
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
### [Amumu Rune](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/AmumuRune.ipynb)
<details> 
  <summary>Q: What is the win rate of ARAM games if Amumu takes Conqueror vs. Dark Harvest vs. Aftershock as the primary rune?</summary>
   A: 
   
      Rune          Win Rate  [Wins / Total]
      Aftershock    0.56900   [40426 / 71048]
      Dark Harvest  0.51438   [4399 / 8552]
      Conqueror     0.56547   [3256 / 5758]
</details>

### [AP Kaisa vs. Squishies](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/APKaisa.ipynb)
<details> 
  <summary>Q: Win rate of AP Kaisa when going against an enemy team with X number of squishy champions?</summary>
   A: 
   
      Kaisa overall win rate:     0.48011 [76160 / 158629]

      AD Kaisa overall win rate:  0.43484 [3153 / 7251]

      AP Kaisa overall win rate:  0.48228 [73007 / 151378]

      Win rate of  AP Kaisa vs. X squishy champions on enemy team:
      Number of Squishies   Win Rate  [Wins / Total]
      Zero                  0.48316   [66380 / 137387]
      One                   0.48603   [5130 / 10555]
      Two                   0.47304   [17168 / 36293]
      Three                 0.47588   [27067 / 56878]
      Four                  0.48056   [18739 / 38994]
      Five                  0.44848   [4422 / 9860]
   
   (Squishies = ['Ahri', 'Annie', 'Aphelios', 'Ashe', 'Aurelion Sol', 'Azir', 'Bard', 'Caitlyn', 'Cassiopeia', 'Corki', 'Draven', 'Ekko', 'Elise', 'Evelynn', 'Ezreal', 'Fizz', 'Gangplank', 'Heimerdinger', 'Janna', 'Jayce', 'Jhin', 'Jinx', "Kai'Sa", 'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Kayle', 'Kayn', 'Kennen', "Kha'Zix", 'Kindred', "Kog'Maw", 'LeBlanc', 'Lillia', 'Lucian', 'Lulu', 'Lux', 'Miss Fortune', 'Morgana', 'Nami', 'Neeko', 'Nidalee', 'Orianna', 'Pyke', 'Qiyana', 'Quinn', 'Rengar', 'Senna', 'Shaco', 'Sivir', 'Sona', 'Soraka', 'Syndra', 'Taliyah', 'Talon', 'Teemo', 'Tristana', 'Twisted Fate', 'Twitch', 'Varus', 'Vayne', 'Veigar', "Vel'Koz", 'Viktor', 'Xayah', 'Xerath', 'Yasuo', 'Yone', 'Yuumi', 'Zed', 'Ziggs', 'Zilean', 'Zoe', 'Zyra'])
</details>

### [Dr. Mundo vs. Low DPS](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/DrMundoVsLowDPS.ipynb)
<details> 
  <summary>Q: What is the win rate of mundo in ARAM games where there are no DPS on the enemy team?</summary>
   A: 
   
      Number of Low DPS Champs   Win Rate   [Wins / Total]
      One                         0.53736   [11586 / 21561]
      Two                         0.52092   [18104 / 34754]
      Three                       0.52355   [12841 / 24527]
      Four                        0.54263   [4169 / 7683]
      Five                        0.58286   [510 / 875]
   
   (Lower 50th Percentile for DPS = ['Ekko', 'Yone', 'Sion', 'Shyvana', 'Kennen', 'Elise', 'Nocturne', 'Malphite', 'Gragas', 'Sett', "Kha'Zix", 'Dr. Mundo', 'Kindred', 'Kassadin', 'Olaf', 'Hecarim', 'Lee Sin', 'Vladimir', 'Vayne', 'Vi', 'Xin Zhao', 'Kayle', 'Maokai', 'Wukong', 'Kayn', 'Bard', 'Pantheon', 'Urgot', 'Gnar', 'Yasuo', 'Volibear', 'Amumu', 'Karma', 'Garen', 'Tryndamere', 'Aatrox', 'Jax', 'Ornn', 'Irelia', 'Renekton', 'Jarvan IV', 'Darius', 'Fiora', 'Yorick', 'Riven', 'Zac', 'Nunu & Willump', 'Sejuani', 'Camille', 'Kled', 'Warwick', 'Blitzcrank', 'Pyke', "Rek'Sai", 'Nautilus', 'Trundle', 'Poppy', 'Shen', 'Nami', 'Rammus', 'Tahm Kench', 'Janna', 'Soraka', 'Udyr', 'Sona', 'Thresh', 'Skarner', 'Leona', 'Alistar', 'Yuumi', 'Ivern', 'Lulu', 'Rakan', 'Braum', 'Taric'])
</details>

### [Low DPS Win Rate](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/DataAnalysis.ipynb)
<details> 
  <summary>Q: What is the win rate of ARAM games where there are X number of DPS champions on the enemy team?</summary>
   A: 

      Number of Low DPS Champs   Win Rate   [Wins / Total]
      One                         0.49147   [367890 / 748550]
      Two                         0.48951   [588506 / 1202243]
      Three                       0.50587   [425354 / 840829]
      Four                        0.53507   [140386 / 262371]
      Five                        0.58177   [17512 / 30101]

   (Lower 50th Percentile for DPS = ['Ekko', 'Yone', 'Sion', 'Shyvana', 'Kennen', 'Elise', 'Nocturne', 'Malphite', 'Gragas', 'Sett', "Kha'Zix", 'Dr. Mundo', 'Kindred', 'Kassadin', 'Olaf', 'Hecarim', 'Lee Sin', 'Vladimir', 'Vayne', 'Vi', 'Xin Zhao', 'Kayle', 'Maokai', 'Wukong', 'Kayn', 'Bard', 'Pantheon', 'Urgot', 'Gnar', 'Yasuo', 'Volibear', 'Amumu', 'Karma', 'Garen', 'Tryndamere', 'Aatrox', 'Jax', 'Ornn', 'Irelia', 'Renekton', 'Jarvan IV', 'Darius', 'Fiora', 'Yorick', 'Riven', 'Zac', 'Nunu & Willump', 'Sejuani', 'Camille', 'Kled', 'Warwick', 'Blitzcrank', 'Pyke', "Rek'Sai", 'Nautilus', 'Trundle', 'Poppy', 'Shen', 'Nami', 'Rammus', 'Tahm Kench', 'Janna', 'Soraka', 'Udyr', 'Sona', 'Thresh', 'Skarner', 'Leona', 'Alistar', 'Yuumi', 'Ivern', 'Lulu', 'Rakan', 'Braum', 'Taric'])
</details>

### [Kayle with Peel](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/KaylePeel.ipynb)
<details>
  <summary>Q: What is the win rate of Kayle with champions that can peel for her in ARAM games?</summary>
   A: 
   
      Kayle overall win rate: 0.51125 [1038129 / 2030563]

      Win rate of Kayle with X number of peel champions on the same team:
      Number of Peeling Champs   Win Rate   [Wins / Total]
      Zero                        0.52161   [37056 / 71041]
      One                         0.51012   [706951 / 1385840]
      Two                         0.51550   [255821 / 496254]
      Three                       0.49835   [36288 / 72817]
      Four                        0.43650   [1966 / 4504]
   
   (Vanguard = ['Alistar', 'Amumu', 'Gragas', 'Leona', 'Malphite', 'Maokai', 'Nautilus', 'Nunu', 'Ornn', 'Rammus', 'Sejuani', 'Sion', 'Zac']
Warden = ['Braum', 'Galio', 'Shen', 'Poppy', 'Tahm Kench', 'Taric']
Enchanter = ['Lulu', 'Janna', 'Soraka', 'Sona', 'Nami', 'Taric', 'Yuumi', 'Karma', 'Senna'])
</details>

### [Number of ADCs](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/numADCWR.ipynb)
<details> 
  <summary>Q: What is the relationship between the number of ADCs on your team and win rate in ARAM games?</summary>
   A: 
   
      Number of ADCs   Win Rate   [Wins / Total]
      Zero              0.46122   [358570 / 777436]
      One               0.51703   [775562 / 1500036]
      Two               0.51357   [409222 / 796814]
      Three             0.47005   [72795 / 154868]
      Four              0.38643   [4806 / 12437]
      Five              0.38643   [210 / 737]
      At Least One      0.51223   [1262595 / 2464892]
      Two Or More       0.50477   [487033 / 964856]
      Three Or More     0.46304   [77811 / 168042]
      Four Or More      0.38075   [5016 / 13174]
   
   (ADCs=['Aphelios', 'Ashe', 'Caitlyn', 'Corki', 'Draven', 'Ezreal', 'Graves', 'Jhin', 'Jinx', "Kai'Sa", 'Kalista', 'Kindred', "Kog'Maw", 'Lucian', 'Miss Fortune', 'Quinn', 'Senna', 'Sivir', 'Tristana', 'Twitch', 'Varus', 'Vayne', 'Xayah'])
</details>

### [LeBlanc vs. Squishies](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/Squishies.ipynb)
<details> 
  <summary>Q: What is the win rate of LeBlanc vs. team of X number of squishy champions? 
</summary>
   A: 

      LeBlanc overall win rate: 0.46682 [67222 / 143999]

      Win rate of LeBlanc vs. X squishy champions on enemy team:
      Number of Squishies   Win Rate    [Wins / Total]
      Zero                  0.46705     [60722 / 130012]
      One                   0.48058     [4814 / 10017]
      Two                   0.46826     [16052 / 34280]
      Three                 0.46046     [24948 / 54181]
      Four                  0.46420     [16862 / 36325]
      Five                  0.49243     [3999 / 8121]
   
   (Squishies = ['Ahri', 'Annie', 'Aphelios', 'Ashe', 'Aurelion Sol', 'Azir', 'Bard', 'Caitlyn', 'Cassiopeia', 'Corki', 'Draven', 'Ekko', 'Elise', 'Evelynn', 'Ezreal', 'Fizz', 'Gangplank', 'Heimerdinger', 'Janna', 'Jayce', 'Jhin', 'Jinx', "Kai'Sa", 'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Kayle', 'Kayn', 'Kennen', "Kha'Zix", 'Kindred', "Kog'Maw", 'LeBlanc', 'Lillia', 'Lucian', 'Lulu', 'Lux', 'Miss Fortune', 'Morgana', 'Nami', 'Neeko', 'Nidalee', 'Orianna', 'Pyke', 'Qiyana', 'Quinn', 'Rengar', 'Senna', 'Shaco', 'Sivir', 'Sona', 'Soraka', 'Syndra', 'Taliyah', 'Talon', 'Teemo', 'Tristana', 'Twisted Fate', 'Twitch', 'Varus', 'Vayne', 'Veigar', "Vel'Koz", 'Viktor', 'Xayah', 'Xerath', 'Yasuo', 'Yone', 'Yuumi', 'Zed', 'Ziggs', 'Zilean', 'Zoe', 'Zyra'])
</details>

### [Number of Supports](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/SupportSynergy.ipynb)
<details> 
  <summary>Q: What is the win rate with X number of supports on your team?
</summary>
   A: 
   
      Number of Supports  Win Rate   [Wins / Total]
      Zero                0.48858    [570660 / 1168007]
      One                 0.50705    [710253 / 1400748]
      Two                 0.50826    [289621 / 569828]
      Three               0.49196    [47514 / 96581]
      Four                0.43973    [3068 / 6977]
      Five                0.43973    [48 / 188]
      At Least One        0.50643    [1050504 / 2074322]
      Two Or More         0.50514    [340251 / 673574]
      Three Or More       0.48802    [50630 / 103746]
      Four Or More        0.43489    [3116 / 7165]

  (Supports = ['Alistar', 'Bard', 'Blitzcrank', 'Braum', 'Ivern', 'Janna', 'Karma', 'Leona', 'Lulu', 'Lux', 'Morgana', 'Nami', 'Nautilus', 'Pyke', 'Rakan', 'Senna', 'Sona', 'Soraka', 'Tahm Kench', 'Taric', 'Thresh', 'Yuumi', 'Zilean', 'Zyra'])
</details>

### [Synergy Pairs](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/SynergyPairs.ipynb)
<details> 
  <summary>Q: Which two champions have the highest win rate when they are on the same team?</summary>
   A: 

      Top 50 Synergistic Champion Pairs:
      Champion 1      Champion 2  Win Rate 	[Wins / Total]
      Sivir           Teemo       0.627537	[4453 / 7096]
      Nunu & Willump  Shaco       0.627537	[4453 / 7096]
      Yorick          Ziggs       0.625138	[567 / 907]
      Amumu           Sivir       0.624978	[3523 / 5637]
      Sivir           Sona        0.622899	[4151 / 6664]
      Alistar         Caitlyn     0.620167	[2743 / 4423]
      Caitlyn         Teemo       0.619139	[5493 / 8872]
      Lux             Zoe         0.617823	[3314 / 5364]
      Leona           Sivir       0.617823	[3314 / 5364]
      Alistar         Jinx        0.617787	[2591 / 4194]
      Caitlyn         Zyra        0.616553	[3531 / 5727]
      Dr. Mundo       Lux         0.615070  [3159 / 5136]
      Amumu           Kayle       0.614861	[3070 / 4993]
      Sona            Ziggs       0.614609	[2743 / 4463]
      Caitlyn         Lux         0.614245	[7339 / 11948]
      Sona            Zyra        0.613424  [2166 / 3531]
      Trundle         Ziggs       0.612147  [1018 / 1663]
      Ashe            Swain       0.612041  [3548 / 5797]
      Jinx            Teemo       0.611962  [4993 / 8159]
      Maokai          Sivir       0.611439  [3731 / 6102]
      Maokai          Ziggs       0.610689  [2491 / 4079]
      LeBlanc         Yorick      0.610525  [4223 / 6917]
      Jinx            Maokai      0.610525  [4223 / 6917]
      Kennen          Qiyana      0.610525  [4223 / 6917]
      Heimerdinger    Yorick      0.61025   [512 / 839]
      Caitlyn         Maokai      0.60935   [4575 / 7508]
      Karthus         Trundle     0.609331  [1084 / 1779]
      Caitlyn         Janna       0.608993  [4808 / 7895]
      Caitlyn         Morgana     0.608988  [6803 / 11171]
      Amumu           Ziggs       0.608937  [2412 / 3961]
      Cho'Gath        Qiyana      0.608937  [2412 / 3961]
      Alistar         Sivir       0.608622  [2160 / 3549]
      Aatrox          Maokai      0.608622  [2160 / 3549]
      Cassiopeia      Jinx        0.608622  [2160 / 3549]
      Brand           Nocturne    0.608622  [2160 / 3549]
      Amumu           Caitlyn     0.60781   [4358 / 7170]
      Jinx            Shaco       0.607788  [3231 / 5316]
      Dr. Mundo       Ziggs       0.6077    [1910 / 3143]
      Kog'Maw         Maokai      0.607548  [2463 / 4054]
      Rakan           Sejuani     0.607444  [2595 / 4272]
      Ornn            Swain       0.606642  [1169 / 1927]
      Amumu           Ashe        0.606483  [4303 / 7095]
      Amumu           Ornn        0.606406  [1117 / 1842]
      Caitlyn         Ziggs       0.606154  [4314 / 7117]
      Alistar         Ziggs       0.605508  [1561 / 2578]
      Wukong          Xayah       0.605186  [1237 / 2044]
      Alistar         Kayle       0.605004  [1717 / 2838]
      Annie           Zoe         0.604875  [1067 / 1764]
      Swain           Trundle     0.604632  [731 / 1209]

  [See here for full list.](https://github.com/patrickgods1/LoLAramPredictor/blob/master/Notebooks/twoSynergy.csv)
</details>

## Machine Learning
Mission: Predict each team's probability of winning the ARAM match.
Data set contains game data collected in patches 10.23, 10.24, and 10.25 only.
Data Set Size:
```
Train: 873,508
Test: 54,000
Validation: 10,000
```

### Preprocessing
#### Missing data
* Drop row if no:
  * champion ID
  * spell ID
  * perk ID
  * game version
  * blue team win
* Fill no rank data as UNRANKED
* Verify no missing value

#### Feature Engineering
Add the following features to the dataset:
* Primary class role of each champion
* Secondary class role of each champion
* Win rate of each champion (from LoLAlytics)
* Average champion win rate of each team
* Each player's ranked game win ratio
* Average rank of each team
* Average ranked game win ratio of each team
* Average champion mastery points of each team
* Champion mastery points multiplied by ranking of each player

### Models
Accuracy Summary:
```
Algorithm         Train     Test      Validation
Random Forest     1.0000    0.7444    0.7090
Neural Network    0.6125    0.6196    0.6054
Catboost          0.8016    0.7755    0.7331
```
#### Random Forest
* Number of Trees: 100
* Criterion: Entropy

Accuracy:
```
Train     Test      Validation
1.0000    0.7444    0.7090
```

ROC and AUC:

![RFCROC](https://user-images.githubusercontent.com/60832092/146857505-0b18fe22-4033-471a-8717-c4e4b92b1f11.jpg)

Predicted Probability Count:
![RFCBlueWinCount](https://user-images.githubusercontent.com/60832092/146857496-1cc298c5-75cb-4d0e-8b24-fb6bd51a9cde.jpg)
![RFCBlueLoseCount](https://user-images.githubusercontent.com/60832092/146857506-edf990f1-fcd9-4f13-b579-948d1025db9d.jpg)
![RFCCount](https://user-images.githubusercontent.com/60832092/146857501-356b2644-6591-4139-a37f-c7a93eddc367.jpg)

Predicted vs Actual Probability:
![RFCBlueWinProbability](https://user-images.githubusercontent.com/60832092/146857500-da779341-70b0-4296-86ae-abd3d9e27748.jpg)
![RFCBlueLoseProbability](https://user-images.githubusercontent.com/60832092/146857508-6cfa899f-071f-49be-a610-cbca025366e5.jpg)

Feature Importance:

![RFCFeatureImportance](https://user-images.githubusercontent.com/60832092/146857503-680af0a0-81d5-4b19-b557-5fb4f03e5acc.jpg)

#### Neural Network
Layers:
```
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
dense_1 (Dense)              (None, 64)                12160     
_________________________________________________________________
batch_normalization_1 (Batch (None, 64)                256       
_________________________________________________________________
dropout_1 (Dropout)          (None, 64)                0         
_________________________________________________________________
dense_2 (Dense)              (None, 32)                2080      
_________________________________________________________________
dropout_2 (Dropout)          (None, 32)                0         
_________________________________________________________________
dense_3 (Dense)              (None, 16)                528       
_________________________________________________________________
dropout_3 (Dropout)          (None, 16)                0         
_________________________________________________________________
dense_4 (Dense)              (None, 1)                 17        
=================================================================
Total params: 15,041
Trainable params: 14,913
Non-trainable params: 128
_________________________________________________________________
```

Accuracy:
```
Train     Test      Validation
0.6002    0.6098    0.6016
```

ROC and AUC:

![NNROC](https://user-images.githubusercontent.com/60832092/146869218-13ab03b4-7218-4672-8b80-2c05a8f70cf7.jpg)

Predicted Probability Count:
![NNBlueWinCount](https://user-images.githubusercontent.com/60832092/146869210-a5ec28a4-b29f-4dab-bc55-d4db09b19e3a.jpg)
![NNCount](https://user-images.githubusercontent.com/60832092/146869216-a24f51f9-d70d-4921-9b25-6317261401e3.jpg)

Predicted vs Actual Probability:
![NNBlueWinProbability](https://user-images.githubusercontent.com/60832092/146869214-f34e2a9b-6404-4fa0-a492-255aa3117ec1.jpg)

Feature Importance:
![NNFeatureImportance](https://user-images.githubusercontent.com/60832092/146874845-8a1cc84f-c6e0-4d05-a177-b369cafc5a73.jpg)

#### Catboost
  * Loss function: Log loss
  * Evaluation metric: Brier Score

Accuracy:
```
Train     Test      Validation
0.8016    0.7755    0.7331
```

ROC and AUC:

![CatBoostROC](https://user-images.githubusercontent.com/60832092/146851450-aacd4af5-900b-402c-bade-d974c4eef7eb.jpg)

Predicted Probability Count:
![CatBoostBlueWinCount](https://user-images.githubusercontent.com/60832092/146851444-db5dbf06-c14d-486a-bee5-abde4e4a8fae.jpg)
![CatBoostBlueLoseCount](https://user-images.githubusercontent.com/60832092/146851436-ffa18c31-3a82-45bb-b30b-661198e06c71.jpg)
![CatBoostCount](https://user-images.githubusercontent.com/60832092/146851446-67744349-a561-4ce7-a6b4-27f384c854a2.jpg)

Predicted vs Actual Probability:
![CatBoostBlueWinProbability](https://user-images.githubusercontent.com/60832092/146851445-f92f86be-fd26-4c7a-ac25-5227b117db2c.jpg)
![CatBoostBlueLoseProbability](https://user-images.githubusercontent.com/60832092/146851442-d72b69bd-07b1-466f-b82f-0db8a782bc5f.jpg)

Feature Importance:
![CatBoostFeatureImportance](https://user-images.githubusercontent.com/60832092/146851448-cf0861fb-29a7-4681-a5f9-dbdc7df7f68f.jpg)

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
* [Matplotlib](https://matplotlib.org/) - Plotting library used to create graphs and charts.

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