import mysql.connect

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="utku",
    database = "STMS"
)

mycursor = mydb.cursor()

# Load data and initialize variables
names = pd.read_csv("name_surname.csv")
sports_names = ["baseball", "tennis", "basketball", "soccer"]
num_tournaments = 10
num_teams_total = 50
sports_ids = list(range(len(sports_names)))

# Reflect existing tables
tournaments = Table("Tournaments", metadata, autoload_with=engine)
sports = Table("Sports", metadata, autoload_with=engine)
teams = Table("Teams", metadata, autoload_with=engine)

# Populate sports table
sports_rows = []
for i, sport in enumerate(sports_names):
    sports_rows.append({
        "sport_id": i,
        "name": sport,
        "desc": f"Description for {sport}",
        "rules": {"general_rules": f"Rules for {sport}"}
    })
# Insert sports data
for row in sports_rows:
    mycursor.execute(
        "INSERT INTO Sports (sport_id, name, description, rules) VALUES (%s, %s, %s, %s)",
        (row["sport_id"], row["name"], row["desc"], row["rules"])
    )
mydb.commit()
# Populate tournaments table
tournaments_rows = []
for i in range(num_tournaments):
    start_date = datetime.date(rand.randint(1980, 2024), rand.randint(1, 12), rand.randint(1, 28))
    end_date = datetime.date(rand.randint(start_date.year, 2024), rand.randint(1, 12), rand.randint(1, 28))
    sport_id = rand.choice(sports_ids)
    tournaments_rows.append({
        "tournament_id": i,
        "name": f"Tournament {i + 1}",
        "sport_id": sport_id,
        "start_date": start_date,
        "end_date": end_date,
        "location": f"Location {i + 1}"
    })
for row in tournaments_rows:
    mycursor.execute(
    "INSERT INTO Tournaments (tournament_id, name, sport_id, start_date, end_date, location) VALUES (%s, %s, %s, %s, %s, %s)",
    (row["tournament_id"], row["name"], row["sport_id"], row["start_date"], row["end_date"], row["location"])
    )
mydb.commit()

teams_rows = []
team_count = 0
for i, tournament in enumerate(tournaments_rows):
    num_teams = rand.randint(1, 6)  # Teams per tournament
    for _ in range(num_teams):
        if team_count >= num_teams_total:
            break  # Stop when total teams reach the limit
        teams_rows.append({
            "team_id": team_count,
            "name": f"Team {team_count}",
            "coach": rand.randint(1, num_tournaments),  # Assume 1 coach per tournament
            "founded_year": rand.randint(1900, 2024),
            "tournament_id":i
        })
        team_count += 1
# Insert teams data
for row in teams_rows:
    mycursor.execute(
        "INSERT INTO Teams (team_id, name, coach, founded_year, tournament_id) VALUES (%s, %s, %s, %s, %s)",
        (row["team_id"], row["name"], row["coach"], row["founded_year"], row["tournament_id"])
    )
mydb.commit()
# Populate players table
players_rows = []
players_in_teams = []
player_count = 0
for i, team in enumerate(teams_rows):
    num_players = rand.randint(11, 20)  # Teams have 11-20 players
    players_temp = []
    for _ in range(num_players):
        player_count += 1
        dob = datetime.date(rand.randint(1980, 2005), rand.randint(1, 12), rand.randint(1, 28))
        players_rows.append({
            "player_id": player_count,
            "first_name": rand.choice(names["first name"]),
            "last_name": rand.choice(names["last name"]),
            "date_of_birth": dob,
            "matches_played": rand.randint(0, 100),
            "team_id":i
        })
        players_temp.append(player_count)
    players_in_teams.append(players_temp)
# Insert players data
for row in players_rows:
    mycursor.execute(
        "INSERT INTO Players (player_id, first_name, last_name, date_of_birth, matches_played, team_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (row["player_id"], row["first_name"], row["last_name"], row["date_of_birth"], row["matches_played"], row["team_id"])
    )
mydb.commit()
# Populate referees table
referees_rows = []
for ref_id in range(1, 21):  # Assume 20 referees
    referees_rows.append({
        "referee_id": ref_id,
        "first_name": rand.choice(names["first name"]),
        "last_name": rand.choice(names["last name"]),
        "experience_years": rand.randint(1, 30),
        "matches_officiated": rand.randint(10, 200)
    })
# Insert referees data
for row in referees_rows:
    mycursor.execute(
        "INSERT INTO Referees (referee_id, first_name, last_name, experience_years, matches_officiated) VALUES (%s, %s, %s, %s, %s)",
        (row["referee_id"], row["first_name"], row["last_name"], row["experience_years"], row["matches_officiated"])
    )
mydb.commit()
# Populate coaches table
coaches_rows = []
for coach_id in range(1, num_tournaments + 1):  # Assume 1 coach per tournament
    coaches_rows.append({
        "coach_id": coach_id,
        "first_name": rand.choice(names["first name"]),
        "last_name": rand.choice(names["last name"]),
        "experience_years": rand.randint(1, 30),
        "currently_associated_team": rand.randint(0, team_count - 1),
        "matches_coached": rand.randint(20, 200)
    })
# Insert coaches data
for row in coaches_rows:
    mycursor.execute(
        "INSERT INTO Coaches (coach_id, first_name, last_name, experience_years, currently_associated_team, matches_coached) VALUES (%s, %s, %s, %s, %s, %s)",
        (row["coach_id"], row["first_name"], row["last_name"], row["experience_years"], row["currently_associated_team"], row["matches_coached"])
    )
mydb.commit()
# Populate matches table
matches_rows = []
teams_in_matches = []
match_count = 0
for i, tournament in enumerate(tournaments_rows):
    num_matches = rand.randint(5, 15)  # Each tournament has 5-15 matches
    for _ in range(num_matches):
        matches_rows.append({
            "match_id": match_count,
            "tournament_id": i,
            "participating_team_id": rand.choice([k for k in range(len(teams_rows))]),
            "referee_id": rand.randint(1, len(referees_rows)),
            "match_date": datetime.date(rand.randint(1980, 2024), rand.randint(1, 12), rand.randint(1, 28)),#make sure teams arent founded after this date
            "location": f"Stadium {match_count}"
        })
        teams_in_matches.append(matches_rows[-1]["participating_team_id"]);
        match_count += 1
# Insert matches data
for row in matches_rows:
    mycursor.execute(
        "INSERT INTO Matches (match_id, tournament_id, participating_team_id, referee_id, match_date, location) VALUES (%s, %s, %s, %s, %s, %s)",
        (row["match_id"], row["tournament_id"], row["participating_team_id"], row["referee_id"], row["match_date"], row["location"])
    )
mydb.commit()
# Populate player_stats table
#this is all wrong this table should be match results. player stats should go under this part
match_results_rows = []
result_count = 0
for i, matches in enumerate(matches_rows):
    for _ in range(2):  # Assume 2 player stats entries per match
        result_count += 1
        match_results_rows.append({
            "result_id": result_count,
            "match_id": i,
            "team_results": {"goals": rand.randint(0, 5), "assists": rand.randint(0, 3)},
            "winner_team_id": rand.choice([k for k in range(len(teams_rows))])#missing info should be match->tournament->team->player holding extra arrays would work
        })

# Insert match results data
for row in match_results_rows:
    mycursor.execute(
        "INSERT INTO Match_Results (result_id, match_id, team_results, winner_team_id) VALUES (%s, %s, %s, %s)",
        (row["result_id"], row["match_id"], row["team_results"], row["winner_team_id"])
    )
mydb.commit()
player_stats_rows = []
stat_count = 0
for i, matches in enumerate(matches_rows):
    for _ in range(2):  # Assume 2 player stats entries per match
        stat_count += 1
        player_stats_rows.append({
            "stat_id": stat_count,
            "match_id": i,
            "player_id": rand.choice([k for k in range(len(players_rows))]),#add list of players
            "score": rand.randint(0, 100)#missing info should be match->tournament->team->player holding extra arrays would work
        })

# Insert player stats data
for row in player_stats_rows:
    mycursor.execute(
        "INSERT INTO Player_Stats (stat_id, match_id, player_id, score) VALUES (%s, %s, %s, %s)",
        (row["stat_id"], row["match_id"], row["player_id"], row["score"])
    )
mydb.commit()

print("Data populated successfully!")