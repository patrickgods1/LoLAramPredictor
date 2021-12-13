import asyncpg
import asyncio
from config import dbConfig


async def run():
    connection = await asyncpg.connect(user=dbConfig['user'],
                                password=dbConfig['password'],
                                host=dbConfig['host'],
                                port=dbConfig['port'],
                                database=dbConfig['database'])
    async with connection.transaction():
        refreshQuery = f'''CREATE TABLE "Matches" (
                        "gameId" bigint   NOT NULL,
                        "platformId" TEXT   NOT NULL,
                        "gameCreation" bigint   NOT NULL,
                        "gameDuration" bigint   NOT NULL,
                        "queueId" integer   NOT NULL,
                        "mapId" integer   NOT NULL,
                        "seasonId" integer   NOT NULL,
                        -- Patch version
                        "gameVersion" TEXT   NOT NULL,
                        "gameMode" TEXT   NOT NULL,
                        "gameType" TEXT   NOT NULL,
                        CONSTRAINT "pk_Matches" PRIMARY KEY (
                            "gameId"
                        )
                    );

                    CREATE TABLE "Champion_Mastery" (
                        -- Champion ID for this entry.
                        "championId" integer   NOT NULL,
                        -- Champion level for specified player and champion combination.
                        "championLevel" integer   NOT NULL,
                        -- Total number of champion points for this player and champion combination - they are used to determine championLevel.
                        "championPoints" integer   NOT NULL,
                        -- Last time this champion was played by this player - in Unix milliseconds time format.
                        "lastPlayTime" bigint   NOT NULL,
                        -- Number of points earned since current level has been achieved.
                        "championPointsSinceLastLevel" bigint   NOT NULL,
                        -- Number of points needed to achieve next level. Zero if player reached maximum champion level for this champion.
                        "championPointsUntilNextLevel" bigint   NOT NULL,
                        -- Is chest granted for this champion or not in current season.
                        "chestGranted" boolean   NOT NULL,
                        -- The token earned for this champion to levelup.
                        "tokensEarned" integer   NOT NULL,
                        -- Summoner ID for this entry. (Encrypted) FK >- Participant_Stats.summonerId
                        -- "summonerId" TEXT   NOT NULL,
                        "summonerName" TEXT   NOT NULL,
                        CONSTRAINT "pk_Champion_Mastery" PRIMARY KEY (
                            "championId","summonerName"
                        )
                    );

                    CREATE TABLE "Team_Stats" (
                        "gameId" bigint   NOT NULL,
                        "win" TEXT   NOT NULL,
                        -- Blue or Red side
                        "teamColor" TEXT   NOT NULL,
                        "firstBlood" boolean   NOT NULL,
                        "firstTower" boolean   NOT NULL,
                        "firstInhibitor" boolean   NOT NULL,
                        "firstBaron" boolean   NOT NULL,
                        "firstDragon" boolean   NOT NULL,
                        "firstRiftHerald" boolean   NOT NULL,
                        "towerKills" integer   NOT NULL,
                        "inhibitorKills" integer   NOT NULL,
                        "baronKills" integer   NOT NULL,
                        "dragonKills" integer   NOT NULL,
                        "vilemawKills" integer   NOT NULL,
                        "riftHeraldKills" integer   NOT NULL,
                        "dominionVictoryScore" integer   NOT NULL,
                        CONSTRAINT "pk_Team_Stats" PRIMARY KEY (
                            "gameId","teamColor"
                        )
                    );

                    -- SoloQ Stats
                    CREATE TABLE "Rank" (
                        "leagueId" TEXT   NOT NULL,
                        "queueType" TEXT   NOT NULL,
                        "tier" TEXT   NOT NULL,
                        "rank" TEXT   NOT NULL,
                        -- "summonerId" TEXT   NOT NULL,
                        "summonerName" TEXT   NOT NULL,
                        "leaguePoints" integer   NOT NULL,
                        "wins" integer   NOT NULL,
                        "losses" integer   NOT NULL,
                        "veteran" boolean   NOT NULL,
                        "inactive" boolean   NOT NULL,
                        "freshBlood" boolean   NOT NULL,
                        "hotStreak" boolean   NOT NULL,
                        CONSTRAINT "pk_Rank" PRIMARY KEY (
                            "queueType","summonerName"
                        )
                    );

                    CREATE TABLE "Participant_Stats" (
                        "gameId" bigint   NOT NULL,
                        "summonerName" TEXT   NOT NULL,
                        -- "accountId" TEXT   NOT NULL,
                        -- "summonerId" TEXT   NOT NULL,
                        "championId" integer   NOT NULL,
                        "spell1Id" integer   NOT NULL,
                        "spell2Id" integer   NOT NULL,
                        "highestAchievedSeasonTier" TEXT,
                        "win" boolean   NOT NULL,
                        -- Blue or Red side
                        "teamColor" TEXT   NOT NULL,
                        "item0" integer   NOT NULL,
                        "item1" integer   NOT NULL,
                        "item2" integer   NOT NULL,
                        "item3" integer   NOT NULL,
                        "item4" integer   NOT NULL,
                        "item5" integer   NOT NULL,
                        "item6" integer   NOT NULL,
                        "kills" integer   NOT NULL,
                        "deaths" integer   NOT NULL,
                        "assists" integer   NOT NULL,
                        "largestKillingSpree" integer   NOT NULL,
                        "largestMultiKill" integer   NOT NULL,
                        "killingSprees" integer   NOT NULL,
                        "longestTimeSpentLiving" integer   NOT NULL,
                        "doubleKills" integer   NOT NULL,
                        "tripleKills" integer   NOT NULL,
                        "quadraKills" integer   NOT NULL,
                        "pentaKills" integer   NOT NULL,
                        "unrealKills" integer   NOT NULL,
                        "totalDamageDealt" bigint   NOT NULL,
                        "magicDamageDealt" bigint   NOT NULL,
                        "physicalDamageDealt" bigint   NOT NULL,
                        "trueDamageDealt" bigint   NOT NULL,
                        "largestCriticalStrike" integer   NOT NULL,
                        "totalDamageDealtToChampions" bigint   NOT NULL,
                        "magicDamageDealtToChampions" bigint   NOT NULL,
                        "physicalDamageDealtToChampions" bigint   NOT NULL,
                        "trueDamageDealtToChampions" bigint   NOT NULL,
                        "totalHeal" bigint   NOT NULL,
                        "totalUnitsHealed" integer   NOT NULL,
                        "damageSelfMitigated" bigint   NOT NULL,
                        "damageDealtToObjectives" bigint   NOT NULL,
                        "damageDealtToTurrets" bigint   NOT NULL,
                        "visionScore" bigint   NOT NULL,
                        "timeCCingOthers" bigint   NOT NULL,
                        "totalDamageTaken" bigint   NOT NULL,
                        "magicalDamageTaken" bigint   NOT NULL,
                        "physicalDamageTaken" bigint   NOT NULL,
                        "trueDamageTaken" bigint   NOT NULL,
                        "goldEarned" integer   NOT NULL,
                        "goldSpent" integer   NOT NULL,
                        "turretKills" integer   NOT NULL,
                        "inhibitorKills" integer   NOT NULL,
                        "totalMinionsKilled" integer   NOT NULL,
                        "neutralMinionsKilled" integer   NOT NULL,
                        "neutralMinionsKilledTeamJungle" integer,
                        "neutralMinionsKilledEnemyJungle" integer,
                        "totalTimeCrowdControlDealt" integer   NOT NULL,
                        "champLevel" integer   NOT NULL,
                        "visionWardsBoughtInGame" integer   NOT NULL,
                        "sightWardsBoughtInGame" integer   NOT NULL,
                        "wardsPlaced" integer,
                        "wardsKilled" integer,
                        "firstBloodKill" boolean,
                        "firstBloodAssist" boolean,
                        "firstTowerKill" boolean,
                        "firstTowerAssist" boolean,
                        "firstInhibitorKill" boolean,
                        "firstInhibitorAssist" boolean,
                        "combatPlayerScore" integer   NOT NULL,
                        "objectivePlayerScore" integer   NOT NULL,
                        "totalPlayerScore" integer   NOT NULL,
                        "totalScoreRank" integer   NOT NULL,
                        "playerScore0" integer   NOT NULL,
                        "playerScore1" integer   NOT NULL,
                        "playerScore2" integer   NOT NULL,
                        "playerScore3" integer   NOT NULL,
                        "playerScore4" integer   NOT NULL,
                        "playerScore5" integer   NOT NULL,
                        "playerScore6" integer   NOT NULL,
                        "playerScore7" integer   NOT NULL,
                        "playerScore8" integer   NOT NULL,
                        "playerScore9" integer   NOT NULL,
                        -- Primary path keystone rune.
                        "perk0" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk0Var1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk0Var2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk0Var3" integer   NOT NULL,
                        -- Primary path rune.
                        "perk1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk1Var1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk1Var2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk1Var3" integer   NOT NULL,
                        -- Primary path rune.
                        "perk2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk2Var1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk2Var2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk2Var3" integer   NOT NULL,
                        -- Primary path rune.
                        "perk3" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk3Var1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk3Var2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk3Var3" integer   NOT NULL,
                        -- Secondary path rune.
                        "perk4" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk4Var1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk4Var2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk4Var3" integer   NOT NULL,
                        -- Secondary path rune.
                        "perk5" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk5Var1" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk5Var2" integer   NOT NULL,
                        -- Post game rune stats.
                        "perk5Var3" integer   NOT NULL,
                        -- Primary rune path
                        "perkPrimaryStyle" integer   NOT NULL,
                        -- Secondary rune path
                        "perkSubStyle" integer,
                        "statPerk0" integer,
                        "statPerk1" integer,
                        "statPerk2" integer,
                        -- Creeps for a specified period.
                        "creepsPerMinDeltas0-10" double precision,
                        "creepsPerMinDeltas10-20" double precision,
                        "creepsPerMinDeltas20-30" double precision,
                        "creepsPerMinDeltas30-end" double precision,
                        -- Experience change for a specified period.
                        "xpPerMinDeltas0-10" double precision,
                        "xpPerMinDeltas10-20" double precision,
                        "xpPerMinDeltas20-30" double precision,
                        "xpPerMinDeltas30-end" double precision,
                        -- Gold for a specified period.
                        "goldPerMinDeltas0-10" double precision,
                        "goldPerMinDeltas10-20" double precision,
                        "goldPerMinDeltas20-30" double precision,
                        "goldPerMinDeltas30-end" double precision,
                        -- Creep score difference versus the calculated lane opponent(s) for a specified period.
                        "csDiffPerMinDeltas0-10" double precision,
                        "csDiffPerMinDeltas10-20" double precision,
                        "csDiffPerMinDeltas20-30" double precision,
                        "csDiffPerMinDeltas30-end" double precision,
                        -- Experience difference versus the calculated lane opponent(s) for a specified period.
                        "xpDiffPerMinDeltas0-10" double precision,
                        "xpDiffPerMinDeltas10-20" double precision,
                        "xpDiffPerMinDeltas20-30" double precision,
                        "xpDiffPerMinDeltas30-end" double precision,
                        -- Damage taken for a specified period.
                        "damageTakenPerMinDeltas0-10" double precision,
                        "damageTakenPerMinDeltas10-20" double precision,
                        "damageTakenPerMinDeltas20-30" double precision,
                        "damageTakenPerMinDeltas30-end" double precision,
                        -- Damage taken difference versus the calculated lane opponent(s) for a specified period.
                        "damageTakenDiffPerMinDeltas0-10" double precision,
                        "damageTakenDiffPerMinDeltas10-20" double precision,
                        "damageTakenDiffPerMinDeltas20-30" double precision,
                        "damageTakenDiffPerMinDeltas30-end" double precision,
                        "role" TEXT   NOT NULL,
                        "lane" TEXT   NOT NULL,
                        CONSTRAINT "pk_Participant_Stats" PRIMARY KEY (
                            "gameId","summonerName"
                        )
                    );

                    -- ALTER TABLE "Champion_Mastery" ADD CONSTRAINT "fk_Champion_Mastery_championId" FOREIGN KEY("championId", "summonerId")
                    -- REFERENCES "Participant_Stats" ("championId");

                    ALTER TABLE "Participant_Stats" ADD CONSTRAINT "fk_Participant_Stats_championId" FOREIGN KEY("championId", "summonerName")
                    REFERENCES "Champion_Mastery" ("championId", "summonerName");

                    ALTER TABLE "Team_Stats" ADD CONSTRAINT "fk_Team_Stats_gameId" FOREIGN KEY("gameId")
                    REFERENCES "Matches" ("gameId");

                    ALTER TABLE "Participant_Stats" ADD CONSTRAINT "fk_Participant_Stats_gameId" FOREIGN KEY("gameId")
                    REFERENCES "Matches" ("gameId");

                    -- ALTER TABLE "Participant_Stats" ADD CONSTRAINT "fk_Participant_Stats_summonerName" FOREIGN KEY("summonerName")
                    -- REFERENCES "Rank" ("summonerName");

                    CREATE INDEX ON "Matches" ("gameId");
                    CREATE INDEX ON "Rank" ("summonerName", "queueType");
                    CREATE INDEX ON "Champion_Mastery" ("championId", "summonerName");
                    CREATE INDEX ON "Participant_Stats" ("gameId", "teamColor", "summonerName", "championId");'''
        status = await connection.execute(refreshQuery)
    return status

loop = asyncio.get_event_loop()
status = loop.run_until_complete(run())
print(status)

