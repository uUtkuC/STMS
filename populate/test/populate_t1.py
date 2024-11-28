import mysql.connector
from mysql.connector import errorcode
import random
from datetime import date, timedelta

# Connect to the database
try:
    cnx = mysql.connector.connect(user='root', password='utku', host='localhost', database='STMS')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Access denied")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor = cnx.cursor()

# Function to generate a random date between two dates
def random_date(start, end):
    delta = end - start
    int_delta = delta.days
    random_day = random.randrange(int_delta)
    return start + timedelta(days=random_day)

# Define the sports
sports = ["baseball", "tennis", "basketball", "soccer", "pubg", "rugby", "cricket", "hockey", "golf", "volleyball", "cycling"]

# Insert sports into the Sports table
for sport in sports:
    name = sport.capitalize()
    description = f"{name} is a popular sport."
    rules = "{}"  # Empty JSON
    add_sport = ("INSERT INTO Sports (name, description, rules) VALUES (%s, %s, %s)")
    data_sport = (name, description, rules)
    cursor.execute(add_sport, data_sport)
cnx.commit()

# Retrieve sport_ids
cursor.execute("SELECT sport_id, name FROM Sports")
sport_ids = {}
for (sport_id, name) in cursor:
    sport_ids[name.lower()] = sport_id

# Define tournament locations
tournament_location_list = ["Ankara","Dubai","New York","Sivas","Arizona","Berlin","Tokyo","Madrid","Kiev","Paris","Internet"]

# Create tournaments for each sport
for i, sport in enumerate(sports):
    sport_id = sport_ids[sport]
    location = tournament_location_list[i % len(tournament_location_list)]
    for t in range(2):  # Two tournaments per sport
        name = f"{sport.capitalize()} Tournament {t+1}"
        start_date = date(2022, 1, 1)
        end_date = date(2023, 12, 31)
        tournament_start_date = random_date(start_date, end_date)
        tournament_end_date = tournament_start_date + timedelta(days=random.randint(1,14))  # Tournament lasts between 1 to 14 days
        add_tournament = ("INSERT INTO Tournaments (name, sport_id, start_date, end_date, location) VALUES (%s, %s, %s, %s, %s)")
        data_tournament = (name, sport_id, tournament_start_date, tournament_end_date, location)
        cursor.execute(add_tournament, data_tournament)
cnx.commit()

# Retrieve coach_ids
first_names = ['John', 'Michael', 'Sarah', 'Jessica', 'David', 'Emily', 'Daniel', 'Emma', 'Matthew', 'Olivia']
last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']

# Create coaches
for i in range(20):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    experience_years = random.randint(1, 30)
    add_coach = ("INSERT INTO Coaches (first_name, last_name, experience_years) VALUES (%s, %s, %s)")
    data_coach = (first_name, last_name, experience_years)
    cursor.execute(add_coach, data_coach)
cnx.commit()

# Retrieve coach_ids
cursor.execute("SELECT coach_id FROM Coaches")
coach_ids = [row[0] for row in cursor.fetchall()]

# Mapping of sports to team counts in a match
sports_team_count_in_match = {
    'baseball':2,
    'tennis':2,
    'basketball':2,
    'soccer':2,
    'pubg':16,
    'rugby':2,
    'cricket':2,
    'hockey':2,
    'golf':2,
    'volleyball':32,
    'cycling':2  # Assuming default
}

# Create teams and assign coaches
team_id_list = []

for sport in sports:
    sport_id = sport_ids[sport]
    for t in range(5):  # 5 teams per sport
        name = f"{sport.capitalize()} Team {t+1}"
        coach_id = random.choice(coach_ids)
        founded_year = random.randint(1950, 2020)
        add_team = ("INSERT INTO Teams (coach, name, founded_year) VALUES (%s, %s, %s)")
        data_team = (coach_id, name, founded_year)
        cursor.execute(add_team, data_team)
        team_id = cursor.lastrowid
        team_id_list.append((team_id, sport_id))
cnx.commit()

# Build a mapping of sport_id to team_ids
sport_teams = {}
for team_id, sport_id in team_id_list:
    if sport_id in sport_teams:
        sport_teams[sport_id].append(team_id)
    else:
        sport_teams[sport_id] = [team_id]

# Create players and assign to teams
countries = ['USA', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Spain', 'Italy', 'Brazil', 'Japan']

for team_id, sport_id in team_id_list:
    for p in range(15):  # 15 players per team
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        date_of_birth = date(1980, 1, 1) + timedelta(days=random.randint(0, 15000))  # Random DOB between 1980 and 2021
        country_of_origin = random.choice(countries)
        age = (date.today() - date_of_birth).days // 365
        market_value = round(random.uniform(10000, 1000000), 2)
        salary = round(random.uniform(5000, 500000), 2)
        contract_start_date = date(2019, 1, 1) + timedelta(days=random.randint(0, 1000))
        contract_end_date = contract_start_date + timedelta(days=random.randint(365, 1095))  # 1 to 3 years
        height = round(random.uniform(1.5, 2.1), 2)
        weight = round(random.uniform(60, 100), 2)
        team_captain = random.choice([True, False])
        experience_years = random.randint(1, 20)
        manager_name = random.choice(first_names) + " " + random.choice(last_names)
        total_minutes_played = random.randint(0, 5000)
        matches_played = random.randint(0, 200)
        add_player = ("INSERT INTO Players (first_name, last_name, date_of_birth, country_of_origin, age, market_value, "
                      "salary, contract_start_date, contract_end_date, height, weight, team_captain, experience_years, "
                      "manager_name, total_minutes_played, matches_played, team_id) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        data_player = (first_name, last_name, date_of_birth, country_of_origin, age, market_value, salary, contract_start_date,
                       contract_end_date, height, weight, team_captain, experience_years, manager_name, total_minutes_played,
                       matches_played, team_id)
        cursor.execute(add_player, data_player)
cnx.commit()

# Retrieve tournaments with their dates
cursor.execute("SELECT tournament_id, sport_id, start_date, end_date, location FROM Tournaments")
tournaments = cursor.fetchall()  # List of (tournament_id, sport_id, start_date, end_date, location)

# Build a reverse mapping of sport_id to sport name
sport_id_to_name = {v: k for k, v in sport_ids.items()}

# Build a mapping from sport_id to team count per match
sport_team_count_per_match = {}
for sport_id in sport_id_to_name:
    sport_name = sport_id_to_name[sport_id]
    team_count = sports_team_count_in_match.get(sport_name, 2)  # Default to 2
    sport_team_count_per_match[sport_id] = team_count

# Insert into Team_Tournament_Participation
for tournament_id, sport_id, start_date, end_date, location in tournaments:
    teams = sport_teams[sport_id]
    for team_id in teams:
        add_participation = ("INSERT INTO Team_Tournament_Participation (team_id, tournament_id) VALUES (%s, %s)")
        data_participation = (team_id, tournament_id)
        cursor.execute(add_participation, data_participation)
cnx.commit()

# Create matches and assign teams
match_id_list = []

for tournament_id, sport_id, start_date, end_date, location in tournaments:
    team_count_per_match = sport_team_count_per_match[sport_id]
    teams = sport_teams[sport_id]
    for m in range(5):  # 5 matches per tournament
        match_date = random_date(start_date, end_date)
        teams_in_match = random.sample(teams, team_count_per_match)
        teams_result = '{}'  # Empty JSON
        add_match = ("INSERT INTO Matches (tournament_id, match_date, location, teams_result) VALUES (%s, %s, %s, %s)")
        data_match = (tournament_id, match_date, location, teams_result)
        cursor.execute(add_match, data_match)
        match_id = cursor.lastrowid
        match_id_list.append((match_id, sport_id))
        # Insert into Team_Match_Participation
        for team_id in teams_in_match:
            add_team_match = ("INSERT INTO Team_Match_Participation (team_id, match_id) VALUES (%s, %s)")
            data_team_match = (team_id, match_id)
            cursor.execute(add_team_match, data_team_match)
cnx.commit()

# Create referees
for i in range(15):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    experience_years = random.randint(1, 20)
    add_referee = ("INSERT INTO Referees (first_name, last_name, experience_years) VALUES (%s, %s, %s)")
    data_referee = (first_name, last_name, experience_years)
    cursor.execute(add_referee, data_referee)
cnx.commit()

# Retrieve referees
cursor.execute("SELECT referee_id FROM Referees")
referee_ids = [row[0] for row in cursor.fetchall()]

# Assign each referee to a sport
referee_sports = {}
for referee_id in referee_ids:
    sport_id = random.choice(list(sport_ids.values()))
    referee_sports[referee_id] = sport_id

# Assign referees to matches
for match_id, sport_id in match_id_list:
    # Find referees who have experience in sport_id
    eligible_referees = [referee_id for referee_id, ref_sport_id in referee_sports.items() if ref_sport_id == sport_id]
    if not eligible_referees:
        # If no eligible referees, skip assigning
        continue
    referee_id = random.choice(eligible_referees)
    add_referee_match = ("INSERT INTO Referees_in_Match (referee_id, match_id) VALUES (%s, %s)")
    data_referee_match = (referee_id, match_id)
    cursor.execute(add_referee_match)
cnx.commit()

# Insert into Team_Coached
cursor.execute("SELECT team_id, coach FROM Teams")
teams_coaches = cursor.fetchall()  # List of (team_id, coach_id)

for team_id, coach_id in teams_coaches:
    coaching_begin_date = date(2015, 1, 1) + timedelta(days=random.randint(0, 2000))
    coaching_end_date = None  # Assume current coach
    add_team_coached = ("INSERT INTO Team_Coached (coach_id, team_id, coaching_begin_date, coaching_end_date) VALUES (%s, %s, %s, %s)")
    data_team_coached = (coach_id, team_id, coaching_begin_date, coaching_end_date)
    cursor.execute(add_team_coached, data_team_coached)
cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()