dbConfig = {"user": 'dbuser',
            "password": 'DBadminpw2', 
            # "host": '127.0.0.1', 
            "host": '192.168.1.107', 
            "port": '5442', 
            "database": 'LoLMatches'
           }
matchlistParams = {"champion": None,    # Set[int] - Set of champion IDs for filtering the matchlist.
                    "queue": 450,      # Set[int] - Set of queue IDs for filtering the matchlist. 400 - Classic, 420 - Classic, 430 - Classic, 450 - ARAM, 850 - Classic, 1300 - Nexus Blitz
                    "season": None,     # Set[int]- [DEPRECATED] This field should not be considered reliable for the purposes of filtering matches by season.
                    "endTime": None,    # long - The end time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
                    "beginTime": 1606226400000,  # long - The begin time to use for filtering matchlist specified as epoch milliseconds. If beginTime is specified, but not endTime, then endTime defaults to the the current unix timestamp in milliseconds (the maximum time range limitation is not observed in this specific case). If endTime is specified, but not beginTime, then beginTime defaults to the start of the account's match history returning a 400 due to the maximum time range limitation. If both are specified, then endTime should be greater than beginTime. The maximum time range allowed is one week, otherwise a 400 error code is returned.
                    "endIndex": 100,      # int - The end index to use for filtering matchlist. If beginIndex is specified, but not endIndex, then endIndex defaults to beginIndex+100. If endIndex is specified, but not beginIndex, then beginIndex defaults to 0. If both are specified, then endIndex must be greater than beginIndex. The maximum range allowed is 100, otherwise a 400 error code is returned.
                    "beginIndex": None  # int - The begin index to use for filtering matchlist. If beginIndex is specified, but not endIndex, then endIndex defaults to beginIndex+100. If endIndex is specified, but not beginIndex, then beginIndex defaults to 0. If both are specified, then endIndex must be greater than beginIndex. The maximum range allowed is 100, otherwise a 400 error code is returned.
                  }
riotConfig = {"api_key": "RGAPI-98293c3d-fbac-4dee-b1c7-c69fcfcba22e",  # DaiLunChu # Developer API key: https://developer.riotgames.com/
                "apiRate": 1,
                "revisitSummoners": True,                                # Revisit summoner accounts to search for newer games
                "seedSummonerNames": ["Yuumí Abuser", "supercoolisaac", 
                                      "Zrky", "Chaotic Clouds",
                                       "HangZhouFaker"],  # Seed summoner name for to start looking for matches
                "server": 'NA1'                                         # BR1	br1.api.riotgames.com
             }                                                          # EUN1	eun1.api.riotgames.com
                                                                        # EUW1	euw1.api.riotgames.com
                                                                        # JP1	jp1.api.riotgames.com
                                                                        # KR	kr.api.riotgames.com
                                                                        # LA1	la1.api.riotgames.com
                                                                        # LA2	la2.api.riotgames.com
                                                                        # NA1	na1.api.riotgames.com
                                                                        # OC1	oc1.api.riotgames.com
                                                                        # TR1	tr1.api.riotgames.com
                                                                        # RU	ru.api.riotgames.com