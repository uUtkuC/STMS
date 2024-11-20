CREATE TABLE Sports (
    sport_id INT  PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rules JSON
);

CREATE TABLE Tournaments (
    tournament_id INT  PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sport_id INT,
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    FOREIGN KEY (sport_id) REFERENCES Sports(sport_id)  ON DELETE SET NULL
);

CREATE TABLE Coaches (
    coach_id INT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    experience_years INT
);

CREATE TABLE Teams (
    team_id INT  PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    coach INT,  -- Temporarily remove NOT NULL to break the cycle
    founded_year INT,
    tournament_id INT,
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id) ON DELETE SET NULL
);

CREATE TABLE Players (
    player_id INT  PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    team_id INT,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE SET NULL
);

CREATE TABLE Matches (
    match_id INT  PRIMARY KEY,
    tournament_id INT,
    participating_team_id INT,
    referee_id INT,
    match_date DATE,
    location VARCHAR(255),
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id) ON DELETE SET NULL,
    FOREIGN KEY (participating_team_id) REFERENCES Teams(team_id) ON DELETE SET NULL
);

CREATE TABLE Player_Stats (
    stat_id INT  PRIMARY KEY,
    match_id INT,
    player_id INT,
    score INT,
    FOREIGN KEY (match_id) REFERENCES Matches(match_id) ON DELETE SET NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE SET NULL
);

CREATE TABLE Match_Results (
    result_id INT  PRIMARY KEY,
    match_id INT,
    teams_results JSON,
    winner_team_id INT,
    FOREIGN KEY (match_id) REFERENCES Matches(match_id) ON DELETE SET NULL,
    FOREIGN KEY (winner_team_id) REFERENCES Teams(team_id) ON DELETE SET NULL
);

CREATE TABLE Referees (
    referee_id INT  PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    experience_years INT
);

-- Add the foreign key for currently_associated_team after tables are created
ALTER TABLE Coaches
ADD COLUMN currently_associated_team INT;

ALTER TABLE Coaches
ADD CONSTRAINT fk_coach_team FOREIGN KEY (currently_associated_team) REFERENCES Teams(team_id)  ON DELETE SET NULL;

