import mysql.connector
import pandas as pd
import json
import os
import datetime
import random as rand

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="utku",
    database = "STMS"
)

# locations below
tournament_location_dict = {0:"Ankara",
                   1:"Dubai",
                   2:"New York",
                   3:"Sivas",
                   4:"Arizona",
                   5:"Berlin",
                   6:"Tokyo",
                   7:"Madrid",
                   8:"Kiev",
                   9:"Paris",
                   10:"Internet"
                   }


# sport rules below
sport_rules = {
    "baseball": "Basketball is played by two teams of five players each on a rectangular court. The objective is to score by shooting a ball through the opponent's hoop. Players dribble to move the ball and pass to teammates. The game consists of four quarters, and the team with the most points wins.",
    "tennis" : "Tennis is played by two players (singles) or four (doubles) on a rectangular court. Players use racquets to hit a ball over a net, aiming to score points by landing the ball in the opponent's court. Matches are divided into sets, and the first to win a specified number of sets wins.",
    "basketball" : "Baseball is played by two teams of nine players each on a diamond-shaped field. Teams alternate between batting and fielding. The batting team aims to score runs by hitting the ball and running to bases, while the fielding team tries to get batters out. The team with the most runs after nine innings wins.",
    "soccer" : "Soccer is played by two teams of eleven players on a rectangular field with goals at each end. Players use their feet to move a ball and score by getting it into the opponent's goal. Matches consist of two 45-minute halves, and the team with the most goals wins.",
    "pubg E-tournament" : "PUBG E-tournament involves players competing solo or in teams on a virtual battleground. Participants must scavenge for weapons and resources while staying within a shrinking safe zone. The objective is to eliminate opponents and be the last player or team standing. Matches are timed, and points are awarded based on survival and kills."


}
# tournament names


current_pwd = os.getcwd()
file_path = os.path.join(current_pwd, "name_surname.csv")
print(f"Attempting to read file: {file_path}")

mycursor = mydb.cursor()


current_pwd = os.getcwd()

# Load data and initialize variables
names = pd.read_csv(current_pwd+"\\name_surname.csv")
sports_names = ["baseball", "tennis", "basketball", "soccer","pubg E-tournament"]
num_tournaments = 10
num_teams_total = 50
sports_ids = list(range(len(sports_names)))


# Populate sports table
sports_rows = []
for i, sport in enumerate(sports_names):
    sports_rows.append({
        "sport_id": i,
        "name": sport,
        "desc": f"Description for {sport}",
        "rules": {"general_rules": sport_rules[sport]}
    })
# Insert sports data
for row in sports_rows:
    mycursor.execute(
        "INSERT INTO Sports (sport_id, name, description, rules) VALUES (%s, %s, %s, %s)",
        (row["sport_id"], row["name"], row["desc"], json.dumps(row["rules"]))
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
        "name": f"Tournament {i+1}",
        "sport_id": sport_id,
        "start_date": start_date,
        "end_date": end_date,
        "location": tournament_location_dict[i+1]
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
        "INSERT INTO Players (player_id, first_name, last_name, date_of_birth, team_id) VALUES (%s, %s, %s, %s, %s)",
        (row["player_id"], row["first_name"], row["last_name"], row["date_of_birth"], row["team_id"])
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
        "INSERT INTO Referees (referee_id, first_name, last_name, experience_years) VALUES (%s, %s, %s, %s)",
        (row["referee_id"], row["first_name"], row["last_name"], row["experience_years"],)
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
        "INSERT INTO Coaches (coach_id, first_name, last_name, experience_years, currently_associated_team) VALUES (%s, %s, %s, %s, %s)",
        (row["coach_id"], row["first_name"], row["last_name"], row["experience_years"], row["currently_associated_team"],)
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
        (row["result_id"], row["match_id"], json.dumps(row["team_results"]), row["winner_team_id"])
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