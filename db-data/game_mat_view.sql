CREATE MATERIALIZED VIEW game_mat_view
AS
    SELECT p1."gameId"
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."championId" END) AS champ_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."championId" END) AS champ_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."championId" END) AS champ_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."championId" END) AS champ_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."championId" END) AS champ_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."championId" END) AS champ_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."championId" END) AS champ_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."championId" END) AS champ_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."championId" END) AS champ_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."championId" END) AS champ_10
            , MAX(CASE p2.Ranking WHEN 1 THEN p1."tier" END) AS "tier_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p1."tier" END) AS "tier_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p1."tier" END) AS "tier_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p1."tier" END) AS "tier_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p1."tier" END) AS "tier_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p1."tier" END) AS "tier_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p1."tier" END) AS "tier_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p1."tier" END) AS "tier_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p1."tier" END) AS "tier_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p1."tier" END) AS "tier_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p1."rank" END) AS "rank_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p1."rank" END) AS "rank_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p1."rank" END) AS "rank_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p1."rank" END) AS "rank_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p1."rank" END) AS "rank_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p1."rank" END) AS "rank_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p1."rank" END) AS "rank_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p1."rank" END) AS "rank_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p1."rank" END) AS "rank_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p1."rank" END) AS "rank_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p1."rankWins" END) AS "rankWins_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p1."rankWins" END) AS "rankWins_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p1."rankWins" END) AS "rankWins_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p1."rankWins" END) AS "rankWins_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p1."rankWins" END) AS "rankWins_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p1."rankWins" END) AS "rankWins_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p1."rankWins" END) AS "rankWins_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p1."rankWins" END) AS "rankWins_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p1."rankWins" END) AS "rankWins_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p1."rankWins" END) AS "rankWins_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p1."rankLosses" END) AS "rankLosses_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p1."rankLosses" END) AS "rankLosses_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p1."rankLosses" END) AS "rankLosses_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p1."rankLosses" END) AS "rankLosses_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p1."rankLosses" END) AS "rankLosses_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p1."rankLosses" END) AS "rankLosses_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p1."rankLosses" END) AS "rankLosses_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p1."rankLosses" END) AS "rankLosses_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p1."rankLosses" END) AS "rankLosses_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p1."rankLosses" END) AS "rankLosses_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p1."championPoints" END) AS "champPts_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p1."championPoints" END) AS "champPts_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p1."championPoints" END) AS "champPts_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p1."championPoints" END) AS "champPts_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p1."championPoints" END) AS "champPts_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p1."championPoints" END) AS "champPts_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p1."championPoints" END) AS "champPts_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p1."championPoints" END) AS "champPts_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p1."championPoints" END) AS "champPts_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p1."championPoints" END) AS "champPts_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."spell1Id" END) AS "spell1Id_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."spell1Id" END) AS "spell1Id_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."spell1Id" END) AS "spell1Id_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."spell1Id" END) AS "spell1Id_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."spell1Id" END) AS "spell1Id_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."spell1Id" END) AS "spell1Id_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."spell1Id" END) AS "spell1Id_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."spell1Id" END) AS "spell1Id_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."spell1Id" END) AS "spell1Id_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."spell1Id" END) AS "spell1Id_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."spell2Id" END) AS "spell2Id_1"
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."spell2Id" END) AS "spell2Id_2"
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."spell2Id" END) AS "spell2Id_3"
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."spell2Id" END) AS "spell2Id_4"
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."spell2Id" END) AS "spell2Id_5"
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."spell2Id" END) AS "spell2Id_6"
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."spell2Id" END) AS "spell2Id_7"
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."spell2Id" END) AS "spell2Id_8"
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."spell2Id" END) AS "spell2Id_9"
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."spell2Id" END) AS "spell2Id_10"
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."perk0" END) AS perk0_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."perk0" END) AS perk0_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."perk0" END) AS perk0_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."perk0" END) AS perk0_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."perk0" END) AS perk0_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."perk0" END) AS perk0_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."perk0" END) AS perk0_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."perk0" END) AS perk0_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."perk0" END) AS perk0_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."perk0" END) AS perk0_10
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."perk1" END) AS perk1_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."perk1" END) AS perk1_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."perk1" END) AS perk1_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."perk1" END) AS perk1_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."perk1" END) AS perk1_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."perk1" END) AS perk1_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."perk1" END) AS perk1_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."perk1" END) AS perk1_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."perk1" END) AS perk1_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."perk1" END) AS perk1_10
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."perk2" END) AS perk2_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."perk2" END) AS perk2_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."perk2" END) AS perk2_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."perk2" END) AS perk2_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."perk2" END) AS perk2_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."perk2" END) AS perk2_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."perk2" END) AS perk2_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."perk2" END) AS perk2_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."perk2" END) AS perk2_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."perk2" END) AS perk2_10
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."perk3" END) AS perk3_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."perk3" END) AS perk3_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."perk3" END) AS perk3_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."perk3" END) AS perk3_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."perk3" END) AS perk3_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."perk3" END) AS perk3_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."perk3" END) AS perk3_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."perk3" END) AS perk3_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."perk3" END) AS perk3_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."perk3" END) AS perk3_10
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."perk4" END) AS perk4_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."perk4" END) AS perk4_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."perk4" END) AS perk4_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."perk4" END) AS perk4_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."perk4" END) AS perk4_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."perk4" END) AS perk4_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."perk4" END) AS perk4_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."perk4" END) AS perk4_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."perk4" END) AS perk4_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."perk4" END) AS perk4_10
            , MAX(CASE p2.Ranking WHEN 1 THEN p2."perk5" END) AS perk5_1
            , MAX(CASE p2.Ranking WHEN 2 THEN p2."perk5" END) AS perk5_2
            , MAX(CASE p2.Ranking WHEN 3 THEN p2."perk5" END) AS perk5_3
            , MAX(CASE p2.Ranking WHEN 4 THEN p2."perk5" END) AS perk5_4
            , MAX(CASE p2.Ranking WHEN 5 THEN p2."perk5" END) AS perk5_5
            , MAX(CASE p2.Ranking WHEN 6 THEN p2."perk5" END) AS perk5_6
            , MAX(CASE p2.Ranking WHEN 7 THEN p2."perk5" END) AS perk5_7
            , MAX(CASE p2.Ranking WHEN 8 THEN p2."perk5" END) AS perk5_8
            , MAX(CASE p2.Ranking WHEN 9 THEN p2."perk5" END) AS perk5_9
            , MAX(CASE p2.Ranking WHEN 10 THEN p2."perk5" END) AS perk5_10
            , MAX(p1."gameMode") AS "gameMode"
            , MAX(p1."gameVersion") AS "gameVersion"
            , BOOL_OR(CASE p2.Ranking WHEN 1 THEN p2."win" END) AS "blueTeamWin"
        FROM (SELECT p."gameId", p."teamColor", p."championId", c."championPoints", r."tier", r."rank", r."wins" AS "rankWins", r."losses" AS "rankLosses", p."spell1Id", p."spell2Id", p."perk0", p."perk1", p."perk2", p."perk3", p."perk4", p."perk5", m."gameMode", m."gameVersion", p."win"
                            FROM "Participant_Stats" AS p
                            LEFT JOIN "Matches" AS m
                            ON p."gameId" = m."gameId"
                            LEFT JOIN "Champion_Mastery" AS c
                            ON p."summonerName" = c."summonerName" AND p."championId" = c."championId"
                            LEFT JOIN (SELECT "summonerName", "queueType", "tier", "rank", "wins", losses
                                FROM "Rank"
                                WHERE "queueType" = \'RANKED_SOLO_5x5\') AS r
                            ON p."summonerName" = r."summonerName") AS p1
        LEFT JOIN (
            SELECT *, ROW_NUMBER() OVER (PARTITION by "gameId" ORDER BY "teamColor", "championId") AS Ranking
            FROM "Participant_Stats"
        ) AS p2 ON p2."gameId"= p1."gameId" AND p2."championId" = p1."championId"
        WHERE "gameMode" = \'ARAM\'
        GROUP BY p1."gameId";