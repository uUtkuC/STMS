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
    passwd="1234",
    database = "STMS"
)
g_match_id = 1
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
        global g_match_id
        match_date = self.start_date + datetime.timedelta(days=rand.randint(0, (self.end_date - self.start_date).days))

        if self.sport_id != 5 and self.sport_id != 10:  # Fixed logic here (AND condition instead of OR)
            for i in range(len(self.teams)):
                for j in range(i + 1, len(self.teams)):
                    match = Match(
                        match_id=g_match_id,
                        tournament_id=self.tournament_id,
                        team1=self.teams[i],
                        team2=self.teams[j],
                        match_date=match_date,
                        location=self.location
                    )
                    g_match_id += 1
                    self.matches.append(match)
        else:
            for i in range(0, len(self.teams), 4):  # Added missing colon
                match = Match(
                    match_id=g_match_id,
                    tournament_id=self.tournament_id,
                    team1=None,
                    team2=None,
                    match_date=match_date,
                    location=self.location
                )
                for j in range(4 * i, min(len(self.teams), 4 * (i + 1))):  # Fixed parentheses
                    match.teams_mul.append(self.teams[j])

                match.teams_mul = list(set(match.teams_mul))
                for team in match.teams_mul:
                    print(f"{team}, tourn_id:{self.tournament_id}, match_id:{match.match_id}")
                g_match_id += 1
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
    def __init__(self, team_id, name, coach,stype, founded_year):
        self.team_id = team_id
        self.name = name
        self.coach = coach
        self.stype = stype
        self.founded_year = founded_year
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def __str__(self):
        return f"{self.team_id}, sport:{self.stype}"

class Player:
    def __init__(self, player_id, first_name, last_name, date_of_birth,country_of_origin,age,market_value,salary,contract_start_date,contract_end_date,height,weight,team_captain,experience_years,manager_name,total_minutes_played,matches_played
,team_id):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.country_of_origin = country_of_origin
        self.age = age
        self.market_value = market_value
        self.salary = salary
        self.contract_start_date = contract_start_date
        self.contract_end_date = contract_end_date
        self.height  = height
        self.weight = weight
        self.team_captain = False
        self.experience_years = experience_years
        self.manager_name = manager_name
        self.total_minutes_played = total_minutes_played
        self.matches_played = matches_played
        self.team_id = team_id

class Match:
    def __init__(self, match_id, tournament_id, team1, team2, match_date, location):
        self.match_id = match_id
        self.tournament_id = tournament_id
        self.team1 = team1
        self.team2 = team2
        self.teams_mul = []
        self.match_date = match_date
        self.location = location

###############################
    # INITIALIZE DATABASE #
###############################


mycursor = mydb.cursor()
current_pwd = os.getcwd()
file_path = os.path.join(current_pwd, "name_surname.csv")
print(f"Attempting to read file: {file_path}")

def run_sql_script(filename):
    with open(filename, 'r') as file:
        sql_script = file.read()

    for statement in sql_script.split(';'):
        if statement.strip():  
            mycursor.execute(statement)
    mydb.commit()
    print(f"SQL script '{filename}' successfully executed.")

sql_file_path = os.path.join(current_pwd, "revised_init_db.sql")
run_sql_script(sql_file_path)


################################
    # INITIALIZE VARIABLES #
################################

countries = [
    "Argentina", "Brazil", "Canada", "China", "Denmark", "Egypt", "France", "Germany",
    "India", "Indonesia", "Italy", "Japan", "Kenya", "Mexico", "Netherlands", "Norway",
    "Russia", "South Africa", "Spain", "United States"
]

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
names = pd.read_csv(current_pwd+"/name_surname.csv")
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
        "sport_id": i+1,
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
        tournament_id=i+1,
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
tournament_objs[7].name = f"Tournament of Pubg 1"
tournament_objs[13].esport = True
tournament_objs[13].location = "Internet"
tournament_objs[13].sport_type = "pubg E-tournament"
tournament_objs[13].name = f"Tournament of Pubg 2"
tournament_objs[18].esport = True
tournament_objs[18].location = "Internet"
tournament_objs[18].sport_type = "pubg E-tournament"
tournament_objs[18].name = f"Tournament of Pubg 3"
#
#for i in range(num_tournaments):
#    print(tournament_objs[i])
## key autoincrement olunca, pk'yi kendisi artırıyor zaten. ONEMLI 1 'den baslıyor
for tournament in tournament_objs:
    mycursor.execute(
        "INSERT INTO Tournaments (name, start_date, end_date, location, sport_id) VALUES (%s, %s, %s, %s, %s)",
        ( tournament.name, tournament.start_date, tournament.end_date, tournament.location, tournament.sport_id)
    )
mydb.commit()



# Populate coaches table
coaches_rows = []
for coach_id in range(1, num_teams_total + 1):  # Assume 1 coach per tournament
    coaches_rows.append({
        "coach_id": coach_id,
        "first_name": rand.choice(names["first name"]),
        "last_name": rand.choice(names["last name"]),
        "experience_years": rand.randint(1, 30),
        "matches_coached": rand.randint(20, 200)
    })
# Insert coaches data
for row in coaches_rows:
    mycursor.execute(
        "INSERT INTO Coaches (first_name, last_name, experience_years) VALUES (%s, %s, %s)",
        (row["first_name"], row["last_name"], row["experience_years"])
    )
mydb.commit()

# Populate teams table
teams_rows = []
team_objs = []
team_count = 0

for i in range(num_teams_total):
    team = Team(
        team_id=i + 1,
        name=f"Team {i + 1}",
        coach= i +1,
        founded_year=rand.randint(1900, 2024),
        stype=sports_names[rand.randint(0, len(sports_names) - 1)]
    )
    team_objs.append(team)

# Insert teams data
for team in team_objs:
    mycursor.execute(
        "INSERT INTO Teams (name, coach, founded_year) VALUES (%s, %s, %s)",
        (team.name, team.coach, team.founded_year)
    )
mydb.commit()

# her bir takımı turnuvalara ekle, eğer typeları uyusuyorsa

for tourn in tournament_objs:
    for team in team_objs:
        if team.stype == tourn.sport_type and rand.choice([0, 1]):
            tourn.add_team(team)


for tourn in tournament_objs:
    tourn.schedule_matches()

    # Insert teams into tournaments and schedule matches in the database
for tourn in tournament_objs:
    for t in tourn.teams:
        mycursor.execute(
            "INSERT INTO Team_Tournament_Participation (tournament_id, team_id) VALUES (%s, %s)",
            (tourn.tournament_id, t.team_id)
        )

mydb.commit()

for tourn in tournament_objs:
    for match in tourn.matches:
        if tourn.sport_id != 5 and tourn.sport_id != 10:
            # Generate random integers X and Y
            X = rand.randint(0, 6)
            Y = rand.randint(0, 6)
            data = {
                        f"{match.team1}": X,
                        f"{match.team2}": Y
                    }
        else:
            for match in tourn.matches:
                data = {}
                for team in match.teams_mul:
                    data[f"{team}"] = rand.randint(0, 10)


        mycursor.execute(
            "INSERT INTO Matches (tournament_id, match_date, location, teams_result) VALUES (%s, %s, %s, %s)",
            (tourn.tournament_id,match.match_date, tourn.location,  json.dumps(data))
        )

mydb.commit()

for tourn in tournament_objs:
    for match in tourn.matches:
        mycursor.execute(
            "INSERT INTO Matches (tournament_id, match_date, location, teams_result) VALUES (%s, %s, %s, %s)",
            (tourn.tournament_id,match.match_date, tourn.location,  json.dumps("a"))
        )

mydb.commit()

from datetime import datetime, timedelta

# Generate a random date between two dates
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = rand.randint(0, delta.days)
    return start_date + timedelta(days=random_days)
start_date = datetime(2006, 1, 1)
end_date = datetime(2035, 12, 31)


# Example usage

# Populate players table
players_rows = []
players_in_teams = []
player_count = 1
for tourn in tournament_objs:
    for t in tourn.teams:
        # Get the team-specific player count based on the sport type
        if t.stype == "pubg E-tournament":
            num_players = 1  # PUBG can have 1 player per team
        elif t.stype == "cycling":
            num_players = 1  # Cycling can have 1 player per team
        else:
            # For traditional sports, teams will have 11-20 players
            num_players = rand.randint(11, 20)

        players_temp = []
        #add the choice of captains index here
        # her takımın ilk oyuncusu kaptan olacak
        temp = 0
        for i in range(num_players):

            player_count += 1
            dob = datetime(rand.randint(1980, 2005), rand.randint(1, 12), rand.randint(1, 28))
            start_date_player = random_date(start_date, end_date)
            experience_years = rand.randint(5, 30)
            players_rows.append({
                    "player_id": player_count,
                    "first_name": rand.choice(names["first name"]),
                    "last_name": rand.choice(names["last name"]),
                    "date_of_birth": dob,
                    "country_of_origin":rand.choice(countries),
                    "age":rand.randint(18,35),
                    "market_value":rand.random()*100000,
                    "salary":rand.random()*10000,
                    "contract_start_date":start_date_player,
                    "contract_end_date":random_date(start_date_player, end_date),
                    "height":rand.randint(170, 220),
                    "weight":rand.randint(65, 100),
                    "team_captain": False,
                    "experience_years":experience_years,
                    "manager_name":rand.choice(names['first name']) + rand.choice(names['last name']),
                    "total_minutes_played":experience_years*120*12,#yes this person practices for 12 hours every day for 120 days I dont care if it makes sense
                    "matches_played": rand.randint(0, 100),
                    "team_id":t.team_id
                })
            # Create a Player object from the dictionary
            new_player = Player(
                player_id=player_count,
                first_name=rand.choice(names["first name"]),
                last_name=rand.choice(names["last name"]),
                date_of_birth=dob,
                country_of_origin=rand.choice(countries),
                age=rand.randint(18, 35),
                market_value=rand.random() * 100000,
                salary=rand.random() * 10000,
                contract_start_date=start_date_player,
                contract_end_date=random_date(start_date_player, end_date),
                height=rand.randint(170, 220),
                weight=rand.randint(65, 100),
                team_captain=False, # if temp = 0, make captain
                experience_years=experience_years,
                manager_name=rand.choice(names['first name']) + rand.choice(names['last name']),
                total_minutes_played=experience_years * 120 * 12,  # Yes, intense training
                matches_played=rand.randint(0, 100),
                team_id=t.team_id
            )
            if temp == 0:
                new_player.team_captain = True
            temp = temp+1
            t.add_player(new_player)
            players_temp.append(player_count)
        players_in_teams.append(players_temp)

# Insert players data
for tourn in tournament_objs:
    for t in tourn.teams:
        for p in t.players:
              mycursor.execute(
                "INSERT INTO Players (first_name, last_name, date_of_birth, team_id, country_of_origin, "
                "age, market_value, salary, contract_start_date, contract_end_date, height, weight, "
                "team_captain, experience_years, manager_name, total_minutes_played, matches_played) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    p.first_name, p.last_name, p.date_of_birth, t.team_id, p.country_of_origin,
                    p.age, p.market_value, p.salary, p.contract_start_date, p.contract_end_date, p.height,
                    p.weight, p.team_captain, p.experience_years, p.manager_name, p.total_minutes_played,
                    p.matches_played
                )
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
        "sport_type" : rand.randint(1, 10)
    })
# Insert referees data
for row in referees_rows:
    mycursor.execute(
        "INSERT INTO Referees (first_name, last_name, experience_years) VALUES (%s, %s, %s)",
        (row["first_name"], row["last_name"], row["experience_years"])
    )
mydb.commit()




# Populate team_match_participation table
participated_rows = []

for tourn in tournament_objs:
    for match in tourn.matches:
        # Insert both teams of the match into the team_match_participation table
        if tourn.sport_id != 5 and tourn.sport_id != 10:
            participated_rows.append({
                "match_id": match.match_id,
                "team_id": match.team1.team_id
            })
            participated_rows.append({
                "match_id": match.match_id,
                "team_id": match.team2.team_id
            })


#or here
for tourn in tournament_objs:
    if tourn.sport_id == 5 or tourn.sport_id == 10:
        for match in tourn.matches:
            for team in set(match.teams_mul):
                participated_rows.append({
                "match_id": match.match_id,
                "team_id": team.team_id
                })




# Insert participation data without duplicates
for row in participated_rows:
    # Check if the combination of match_id and team_id already exists
    mycursor.execute(
        "SELECT 1 FROM Team_Match_Participation WHERE match_id = %s AND team_id = %s",
        (row["match_id"], row["team_id"])
    )
    if mycursor.fetchone() is None:  # Only insert if not already present
        mycursor.execute(
            "INSERT INTO Team_Match_Participation (match_id, team_id) VALUES (%s, %s)",
            (row["match_id"], row["team_id"])
        )
mydb.commit()

# Populate have_referees table
have_referees_rows = []


for tourn in tournament_objs:
    for match in tourn.matches:
        # Select a random referee
        referee_id = rand.choice(referees_rows)["referee_id"]

        # Check if the referee is already assigned to this match
        mycursor.execute(
            "SELECT 1 FROM Referees_in_Match WHERE match_id = %s AND referee_id = %s",
            (match.match_id, referee_id)
        )
        if mycursor.fetchone() is None:
            # If no result is found, insert the new entry
            mycursor.execute(
                "INSERT INTO Referees_in_Match (match_id, referee_id) VALUES (%s, %s)",
                (match.match_id, referee_id)
            )
            have_referees_rows.append({
            "match_id": match.match_id,
            "referee_id": rand.choice(referees_rows)["referee_id"]
        })

mydb.commit()

# needed tables:
# referees_in_match

#team_match participation -> bugfix probably
#add caoches to teams.

referee_count_dict = {
    "baseball": 4,            # 4 referees (umpires) in a typical baseball game (plate umpire + 3 base umpires)
    "tennis": 1,              # 1 referee (chair umpire), though there may be line judges
    "basketball": 3,          # 3 referees in a standard basketball game (1 lead, 2 trail)
    "soccer": 4,              # 1 center referee, 2 assistant referees, 1 fourth official
    "pubg E-tournament": 1,   # 1 referee
    "rugby": 3,               # 1 referee and 2 touch judges (assistants)
    "cricket": 3,             # 2 on-field umpires, 1 third umpire (for technology assistance)
    "hockey": 2,              # 2 referees in field hockey (1 umpire per half)
    "golf": 1,                # 1 referee (often an official who oversees the game, particularly for disputes)
    "volleyball": 2,          # 1 first referee, 1 second referee (sometimes with line judges)
    "cycling": 1              # 1 referee (official race director or commissaire)
}

# referees in match
# refereelerin type'ları belirlendi üstte. referee.sport kullanarak,
#uyumlu sport tournamentları için eşlememiz lazım. referee_count_dict,
# maç bası hakem sayisini gösteriyor.

have_referee_rows = []
for tourn in tournament_objs:
    for match in tourn.matches:
        required_referees = referee_count_dict.get(tourn.sport_type)
        assigned_referees = []
        for referee in referees_rows:
            if referee.get('sport_type') == tourn.sport_type and len(assigned_referees) < required_referees:
                assigned_referees.append(referee)
          # Check if the required number of referees are assigned
        if len(assigned_referees) == required_referees:
            for referee in assigned_referees:
                have_referee_rows.append({
                    "match_id": match.id,
                    "referee_id": referee["referee_id"]
                })

# Insert have attended data
for row in have_referee_rows:
    mycursor.execute(
        "INSERT INTO Referees_in_Match (referee_id, match_id) VALUES (%s, %s)",
        (row["referee_id"], row["match_id"])
    )
mydb.commit()


# team_coached
# Function to generate coaching assignment date range
def generate_coaching_dates(founded_year):
    coaching_begin_date = datetime(founded_year+3, rand.randint(1, 12), rand.randint(1, 28))
    coaching_end_date = coaching_begin_date + timedelta(days=rand.randint(365, 365*5))  # Between 1 and 5 years
    return coaching_begin_date.strftime('%Y-%m-%d'), coaching_end_date.strftime('%Y-%m-%d')

# List to store the rows to be inserted into Team_Coached table
team_coached_rows = []

# Generate the coaching assignments
for team in team_objs:
    coach_id = team.coach
    team_id = team.team_id
    coaching_begin_date, coaching_end_date = generate_coaching_dates(team.founded_year)

    team_coached_rows.append({
        "coach_id": coach_id,
        "team_id": team_id,
        "coaching_begin_date": coaching_begin_date,
        "coaching_end_date": coaching_end_date
    })

for team in team_objs[i:num_teams_total//2]:

    coach_id = rand.randint(1,num_teams_total//2)
    while coach_id == team.coach:
        coach_id = rand.randint(1,num_teams_total//2) #we want different coaches

    team_id = team.team_id
    coaching_begin_date, coaching_end_date = generate_coaching_dates(team.founded_year-3) #to make it applicable to another frunction

    team_coached_rows.append({
        "coach_id": coach_id,
        "team_id": team_id,
        "coaching_begin_date": coaching_begin_date,
        "coaching_end_date": coaching_end_date
    })

for team in team_objs[i:num_teams_total//4]:

    coach_id = rand.randint(1,num_teams_total//4)
    while coach_id == team.coach:
        coach_id = rand.randint(1,num_teams_total//4) #we want different coaches

    team_id = team.team_id
    coaching_begin_date, coaching_end_date = generate_coaching_dates(team.founded_year-3) #to make it applicable to another frunction

    team_coached_rows.append({
        "coach_id": coach_id,
        "team_id": team_id,
        "coaching_begin_date": coaching_begin_date,
        "coaching_end_date": coaching_end_date
    })

# Insert into Team_Coached table
for row in team_coached_rows:
    mycursor.execute(
        "INSERT INTO Team_Coached (coach_id, team_id, coaching_begin_date, coaching_end_date) "
        "VALUES (%s, %s, %s, %s)",
        (row["coach_id"], row["team_id"], row["coaching_begin_date"], row["coaching_end_date"])
    )

# Commit the changes
mydb.commit()

print("Data populated successfully!")
