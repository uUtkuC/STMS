import random as rand
from sqlalchemy import text, create_engine, Table, MetaData
import datetime
import pandas as pd

# Define database connection string and table names
database = "mysql+pymysql://username:password@localhost:utku/bil372"
engine = create_engine(database)
metadata = MetaData()

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

# Insert data into tables
with engine.connect() as connection:
    # Insert sports
    connection.execute(sports.insert(), sports_rows)

    # Insert tournaments
    connection.execute(tournaments.insert(), tournaments_rows)

    # Insert teams
    connection.execute(teams.insert(), teams_rows)

    # Insert players
    connection.execute(Table("Players", metadata, autoload_with=engine).insert(), players_rows)

    # Insert referees
    connection.execute(Table("Referees", metadata, autoload_with=engine).insert(), referees_rows)

    # Insert coaches
    connection.execute(Table("Coaches", metadata, autoload_with=engine).insert(), coaches_rows)

    connection.execute(text("""ALTER TABLE Teams ADD CONSTRAINT fk_coach_id FOREIGN KEY (coach) REFERENCES Coaches(coach_id) ON DELETE SET NULL;"""))

    # Insert matches
    connection.execute(Table("Matches", metadata, autoload_with=engine).insert(), matches_rows)

    # Insert player stats
    connection.execute(Table("Player_Stats", metadata, autoload_with=engine).insert(), player_stats_rows)

    connection.execute(Table("Match_Results", metadata, autoload_with=engine).insert(), match_results_rows)

print("Data populated successfully!")
