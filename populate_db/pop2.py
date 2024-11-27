import mysql.connector
import pandas as pd
import json
import os
import datetime
import random as rand

rand.seed(42)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="utku",
    database = "STMS"
)

#her bir turnuva içine takımları koy, bu takımlar kendi içnide
#arbitrary maç yapsın
class Tournament:
    def __init__(self, tournament_id, name, start_date, end_date,sport_id, location,sport_type, esport=False):
        self.tournament_id = tournament_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.esport=esport
        self.sport_id = sport_id
        self.sport_type = sport_type
        self.teams = []
        self.matches = []

    def add_team(self, team):
        self.teams.append(team)

    def schedule_matches(self):
        # Ensure each team plays at least one match with every other team
        for i in range(len(self.teams)):
            for j in range(i+1, len(self.teams)):
                match_date = self.start_date + datetime.timedelta(days=rand.randint(0, (self.end_date - self.start_date).days))
                match = Match(
                    match_id=len(self.matches),
                    tournament_id=self.tournament_id,
                    team1=self.teams[i],
                    team2=self.teams[j],
                    match_date=match_date,
                    location=self.location
                )
                self.matches.append(match)

    def generate_matches(self):
        matches = []
        for i in range(len(self.teams)):
            for j in range(i + 1, len(self.teams)):
                matches.append((self.teams[i], self.teams[j]))
        return matches

    def __str__(self):
        teams_str = ', '.join([team.name for team in self.teams])
        return (f"Tournament ID: {self.tournament_id}\n"
                f"Name: {self.name}\n"
                f"Start Date: {self.start_date}\n"
                f"End Date: {self.end_date}\n"
                f"Location: {self.location}\n"
                f"Teams: {teams_str}\n")

class Team:
    def __init__(self, team_id, name, coach, founded_year):
        self.team_id = team_id
        self.name = name
        self.coach = coach
        self.founded_year = founded_year
        self.players = []

    def add_player(self, player):
        self.players.append(player)

class Player:
    def __init__(self, player_id, first_name, last_name, date_of_birth, team_id):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.team_id = team_id

class Match:
    def __init__(self, match_id, tournament_id, team1, team2, match_date, location):
        self.match_id = match_id
        self.tournament_id = tournament_id
        self.team1 = team1
        self.team2 = team2
        self.match_date = match_date
        self.location = location

###############################
    # INITIALIZE DATABASE #
###############################


mycursor = mydb.cursor()
current_pwd = os.getcwd()
file_path = os.path.join(current_pwd, "name_surname.csv")
print(f"Attempting to read file: {file_path}")

################################
    # INITIALIZE VARIABLES #
################################


# locations below
# ensure that the last entry is internet. and no other online location is present
tournament_location_dict = {
    0:"Ankara",
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
    "pubg E-tournament" : "PUBG E-tournament involves players competing solo or in teams on a virtual battleground. Participants must scavenge for weapons and resources while staying within a shrinking safe zone. The objective is to eliminate opponents and be the last player or team standing. Matches are timed, and points are awarded based on survival and kills.",
    "rugby": "Rugby is played by two teams of 15 players each on a rectangular field. Players score points by carrying, passing, or kicking an oval ball to the opponent's end zone. The game involves physical tackles, scrums, and lineouts. Matches are divided into two halves, and the team with the most points wins.",
    "cricket": "Cricket is played by two teams of 11 players each on an oval field with a central pitch. The batting team aims to score runs by hitting the ball and running between wickets, while the bowling team tries to dismiss the batsmen. Matches vary in length, from limited overs to multi-day formats.",
    "hockey": "Hockey is played by two teams of 11 players each on a rectangular field with goals at each end. Players use curved sticks to move a small ball, aiming to score by hitting it into the opponent's goal. Matches consist of two halves, and the team with the most goals wins.",
    "golf" : "Golf is an individual sport played on a course with 18 holes. Players use clubs to hit a ball into each hole with the fewest strokes possible. Courses vary in layout and obstacles. The player with the lowest total strokes at the end of the course wins.",
    "voleyball" : "Volleyball is played by two teams of six players each on a rectangular court divided by a net. Players aim to score points by hitting a ball over the net and landing it in the opponent's court. Matches are played in sets, and the team that wins the majority of sets wins the match.",
    "cycling" : "Cycling is an individual sport where participants race on bicycles over varying terrains, including road, track, and off-road trails. Riders compete to cover the distance in the shortest time or to complete a set number of laps. Key factors include endurance, speed, technique, and strategy for optimal performance."
}

sports_team_count_in_match = [2, 2, 2, 2, 16, 2, 2, 2, 2, 32]
#pubg E tournament and cycling may have varying matches

# Load data and initialize variables
current_pwd = os.getcwd()
names = pd.read_csv(current_pwd+"\\name_surname.csv")
sports_names = ["baseball", "tennis", "basketball", "soccer","pubg E-tournament", "rugby", "cricket", "golf", "voleyball", "cycling"]

num_tournaments = 30
#set tournament 7- 13- 18 as e sport tournaments
num_teams_total = 200
sports_ids = list(range(len(sports_names)))


#############################
    # POPULATE DATABASE #
#############################


# Populate tournaments table
tournaments_rows = []

tournament_objs = []
#add namings like UEFA, a special tennis tournament name, basketball name, soccer name etc

# Populate sports table

    # deleted this from below. why does sport has tournament_id? "tournament_id": rand.randint(0, num_tournaments - 1)
# when sport id is auto-incremented do not push id into database
sports_rows = []
for i, sport in enumerate(sports_names):
    sports_rows.append({
        "sport_id": {i+1},
        "name": sport,
        "desc": f"Description for {sport}",
        "rules": {"general_rules": sport_rules[sport]}
    })
# Insert sports data
for row in sports_rows:
    mycursor.execute(
        "INSERT INTO Sports (name, description, rules) VALUES (%s, %s, %s)",
        (row["name"], row["desc"], json.dumps(row["rules"]))
    )
mydb.commit()

for i in range(num_tournaments):
    start_date = datetime.date(rand.randint(1980, 2024), rand.randint(1, 12), rand.randint(1, 28))
    end_date = start_date + datetime.timedelta(days=rand.randint(1, 365))
    instance_sport_name = sports_names[rand.randint(0, len(sports_names) - 1)]
    tournament = Tournament(
        tournament_id={i+1},
        name=f"Tournament of {instance_sport_name} {i+1}",
        start_date=start_date,
        sport_type=instance_sport_name,
        end_date=end_date,
        sport_id = sports_names.index(instance_sport_name)+1,
        location=tournament_location_dict[rand.randint(0, len(tournament_location_dict) - 2)]
    )
    # setting internet tournaments
    tournament_objs.append(tournament)

tournament_objs[7].esport = True
tournament_objs[7].location = "Internet" 
tournament_objs[7].sport_type = "pubg E-tournament" 
tournament_objs[13].esport = True
tournament_objs[13].location = "Internet"
tournament_objs[13].sport_type = "pubg E-tournament" 
tournament_objs[18].esport = True
tournament_objs[18].location = "Internet"
tournament_objs[18].sport_type = "pubg E-tournament" 

for i in range(num_tournaments):
    print(tournament_objs[i])
# key autoincrement olunca, pk'yi kendisi artırıyor zaten. ONEMLI 1 'den baslıyor
for tournament in tournament_objs:
    mycursor.execute(
        "INSERT INTO Tournaments (name, start_date, end_date, location, sport_id) VALUES (%s, %s, %s, %s, %s)",
        ( tournament.name, tournament.start_date, tournament.end_date, tournament.location, tournament.sport_id)
    )
mydb.commit()




# # Populate teams table
# teams_rows = []
# team_count = 0
# for i, tournament in enumerate(tournaments_rows):
#     num_teams = rand.randint(1, 6)  # Tournaments attended by each team
#     for _ in range(num_teams):
#         if team_count >= num_teams_total:
#             break  # Stop when total teams reach the limit
#         teams_rows.append({
#             "team_id": team_count,
#             "name": f"Team {team_count}",
#             "coach": rand.randint(1, num_tournaments),  # Assume 1 coach per tournament
#             "founded_year": rand.randint(1900, 2024)
#         })
#         team_count += 1
# # Insert teams data
# for row in teams_rows:
#     mycursor.execute(
#         "INSERT INTO Teams (team_id, name, coach, founded_year) VALUES (%s, %s, %s, %s)",
#         (row["team_id"], row["name"], row["coach"], row["founded_year"])
#     )
# mydb.commit()


# # Populate players table
# players_rows = []
# players_in_teams = []
# player_count = 0
# for i, team in enumerate(teams_rows):
#     num_players = rand.randint(11, 20)  # Teams have 11-20 players
#     players_temp = []
#     for _ in range(num_players):
#         player_count += 1
#         dob = datetime.date(rand.randint(1980, 2005), rand.randint(1, 12), rand.randint(1, 28))
#         players_rows.append({
#             "player_id": player_count,
#             "first_name": rand.choice(names["first name"]),
#             "last_name": rand.choice(names["last name"]),
#             "date_of_birth": dob,
#             "matches_played": rand.randint(0, 100),
#             "team_id":i
#         })
#         players_temp.append(player_count)
#     players_in_teams.append(players_temp)
# # Insert players data
# for row in players_rows:
#     mycursor.execute(
#         "INSERT INTO Players (player_id, first_name, last_name, date_of_birth, team_id) VALUES (%s, %s, %s, %s, %s)",
#         (row["player_id"], row["first_name"], row["last_name"], row["date_of_birth"], row["team_id"])
#     )
# mydb.commit()


# # Populate referees table
# referees_rows = []
# for ref_id in range(1, 21):  # Assume 20 referees
#     referees_rows.append({
#         "referee_id": ref_id,
#         "first_name": rand.choice(names["first name"]),
#         "last_name": rand.choice(names["last name"]),
#         "experience_years": rand.randint(1, 30)
#     })
# # Insert referees data
# for row in referees_rows:
#     mycursor.execute(
#         "INSERT INTO Referees (referee_id, first_name, last_name, experience_years) VALUES (%s, %s, %s, %s)",
#         (row["referee_id"], row["first_name"], row["last_name"], row["experience_years"])
#     )
# mydb.commit()


# # Populate coaches table
# coaches_rows = []
# for coach_id in range(1, num_tournaments + 1):  # Assume 1 coach per tournament
#     coaches_rows.append({
#         "coach_id": coach_id,
#         "first_name": rand.choice(names["first name"]),
#         "last_name": rand.choice(names["last name"]),
#         "experience_years": rand.randint(1, 30),
#         "matches_coached": rand.randint(20, 200)
#     })
# # Insert coaches data
# for row in coaches_rows:
#     mycursor.execute(
#         "INSERT INTO Coaches (coach_id, first_name, last_name, experience_years) VALUES (%s, %s, %s, %s)",
#         (row["coach_id"], row["first_name"], row["last_name"], row["experience_years"])
#     )
# mydb.commit()


# # Populate matches table
# matches_rows = []
# teams_in_matches = []
# match_count = 0
# for i, tournament in enumerate(tournaments_rows):
#     num_matches = rand.randint(5, 15)  # Each tournament has 5-15 matches
#     for _ in range(num_matches):
#         matches_rows.append({
#             "match_id": match_count,
#             "tournament_id": i,
#             "referee_id": rand.randint(1, len(referees_rows)),
#             "match_date": datetime.date(rand.randint(1980, 2024), rand.randint(1, 12), rand.randint(1, 28)),#make sure teams arent founded after this date
#             "location": f"Stadium {match_count}"
#         })
#         match_count += 1
# # Insert matches data
# for row in matches_rows:
#     mycursor.execute(
#         "INSERT INTO Matches (match_id, tournament_id, referee_id, match_date, location) VALUES (%s, %s, %s, %s, %s)",
#         (row["match_id"], row["tournament_id"], row["referee_id"], row["match_date"], row["location"])
#     )
# mydb.commit()


# # Populate match_results table
# #this is all wrong this table should be match results. player stats should go under this part
# match_results_rows = []
# result_count = 0
# for i, matches in enumerate(matches_rows):
#     for _ in range(2):  # Assume 2 player stats entries per match
#         result_count += 1
#         match_results_rows.append({
#             "result_id": result_count,
#             "match_id": i,
#             "team_results": {"goals": rand.randint(0, 5), "assists": rand.randint(0, 3)},
#             "winner_team_id": rand.choice([k for k in range(len(teams_rows))])#missing info should be match->tournament->team->player holding extra arrays would work
#         })
# # Insert match results data
# for row in match_results_rows:
#     mycursor.execute(
#         "INSERT INTO Match_Results (result_id, match_id, team_results, winner_team_id) VALUES (%s, %s, %s, %s)",
#         (row["result_id"], row["match_id"], json.dumps(row["team_results"]), row["winner_team_id"])
#     )
# mydb.commit()


# # Populate player_stats table
# player_stats_rows = []
# stat_count = 0
# for i, matches in enumerate(matches_rows):
#     for _ in range(2):  # Assume 2 player stats entries per match
#         stat_count += 1
#         player_stats_rows.append({
#             "stat_id": stat_count,
#             "match_id": i,
#             "player_id": rand.choice(players_rows)["player_id"],
#             "score": rand.randint(0, 100)#missing info should be match->tournament->team->player holding extra arrays would work
#         })

# # Insert player stats data
# for row in player_stats_rows:
#     mycursor.execute(
#         "INSERT INTO Player_Stats (stat_id, match_id, player_id, score) VALUES (%s, %s, %s, %s)",
#         (row["stat_id"], row["match_id"], row["player_id"], row["score"])
#     )
# mydb.commit()


# # Populate participated table
# participated_rows = []
# for match in matches_rows:
#     # Select 2 random teams to participate in each match
#     participating_teams = rand.sample(teams_rows, 2)  # Randomly select 2 teams

#     for team in participating_teams:
#         participated_rows.append({
#             "match_id": match["match_id"],
#             "team_id": team["team_id"]
#         })
# # Insert participated data
# for row in participated_rows:
#     mycursor.execute(
#         "INSERT INTO PARTICIPATED (match_id, team_id) VALUES (%s, %s)",
#         (row["match_id"], row["team_id"])
#     )
# mydb.commit()


# # Populate have_referees table
# have_referees_rows = []
# for match in matches_rows:
#     have_referees_rows.append({
#         "match_id": match["match_id"],
#         "referee_id": rand.choice(referees_rows)["referee_id"]
#     })
# # Insert have referees data
# for row in have_referees_rows:
#     mycursor.execute(
#         "INSERT INTO HAVE_REFEREES (match_id, referee_id) VALUES (%s, %s)",
#         (row["match_id"], row["referee_id"])
#     )
# mydb.commit()

    
# # Populate attend table
# have_attended_rows = []
# for match in matches_rows:
#     have_attended_rows.append({
#         "team_id": team["team_id"],
#         "tournament_id": rand.choice(tournaments_rows)["tournament_id"]
#     })
# # Insert have attended data
# for row in have_attended_rows:
#     mycursor.execute(
#         "INSERT INTO ATTEND (team_id, tournament_id) VALUES (%s, %s)",
#         (row["team_id"], row["tournament_id"])
#     )
# mydb.commit()


# # Populate have_match_results table
# have_match_results_rows = []
# for match in matches_rows:
#     have_match_results_rows.append({
#         "team_id": team["team_id"],
#         "result_id": rand.choice(match_results_rows)["result_id"]
#     })
# # Insert have match results data
# for row in have_match_results_rows:
#     mycursor.execute(
#         "INSERT INTO HAVE_MATCH_RESULTS (team_id, result_id) VALUES (%s, %s)",
#         (row["team_id"], row["result_id"])
#     )
# mydb.commit()

print("Data populated successfully!")