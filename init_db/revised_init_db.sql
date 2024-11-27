CREATE DATABASE STMS;
USE STMS;
-- Sports Table
CREATE TABLE Sports (
    sport_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rules JSON
);

-- Tournaments Table
CREATE TABLE Tournaments (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sport_id INT,
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    FOREIGN KEY (sport_id) REFERENCES Sports(sport_id)
);

-- Coaches Table
CREATE TABLE Coaches (
    coach_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    experience_years INT
);

-- Teams Table
CREATE TABLE Teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    coach INT,
    name VARCHAR(255) NOT NULL,
    founded_year YEAR,
    FOREIGN KEY (coach) REFERENCES Coaches(coach_id)
);

-- Players Table
CREATE TABLE Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    country_of_origin VARCHAR(255),
    age INT,
    market_value DECIMAL(15, 2),
    salary DECIMAL(15, 2),
    contract_start_date DATE,
    contract_end_date DATE,
    height DECIMAL(5, 2),
    weight DECIMAL(5, 2),
    team_captain BOOLEAN,
    experience_years INT,
    manager_name VARCHAR(255),
    total_minutes_played INT,
    matches_played INT,
    team_id INT,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

-- Matches Table
CREATE TABLE Matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT,
    match_date DATE,
    location VARCHAR(255),
    teams_result JSON,
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id)
);

-- Referees Table
CREATE TABLE Referees (
    referee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    experience_years INT
);

-- Team_Coached Table
CREATE TABLE Team_Coached (
    coach_id INT,
    team_id INT,
    coaching_begin_date DATE,
    coaching_end_date DATE,
    PRIMARY KEY (coach_id, team_id),
    FOREIGN KEY (coach_id) REFERENCES Coaches(coach_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

-- Team_Tournament_Participation Table
CREATE TABLE Team_Tournament_Participation (
    team_id INT,
    tournament_id INT,
    PRIMARY KEY (team_id, tournament_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id)
);

-- Team_Match_Participation Table
CREATE TABLE Team_Match_Participation (
    team_id INT,
    match_id INT,
    PRIMARY KEY (team_id, match_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);

-- Referees_in_Match Table
CREATE TABLE Referees_in_Match (
    referee_id INT,
    match_id INT,
    PRIMARY KEY (referee_id, match_id),
    FOREIGN KEY (referee_id) REFERENCES Referees(referee_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
