import mysql.connector
from mysql.connector import Error
import time

def create_connection():
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='utku',
            database='STMS'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def create_times_table(connection):
    """Create a table to store query execution times."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS QueryTimes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        query VARCHAR(255) NOT NULL,
        execution_time DOUBLE NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()

def log_query_time(connection, query, execution_time):
    """Log the execution time of a query."""
    insert_query = """
    INSERT INTO QueryTimes (query, execution_time)
    VALUES (%s, %s);
    """
    cursor = connection.cursor()
    cursor.execute(insert_query, (query, execution_time))
    connection.commit()

def execute_query_with_timing(connection, query):
    """Execute a query and log its execution time."""
    start_time = time.perf_counter()
    cursor = connection.cursor()
    cursor.execute(query)
    
    # Fetch all results if the query is a SELECT query
    if query.strip().lower().startswith('select'):
        cursor.fetchall()
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    log_query_time(connection, query, execution_time)
    return execution_time

# List of queries to test
queries = [
    "SELECT * FROM Players;",
    "SELECT DISTINCT name FROM Sports;",
    "SELECT name FROM Tournaments WHERE sport_id = (SELECT sport_id FROM Sports WHERE name = 'basketball');",
    "SELECT * FROM Coaches;",
    "SELECT * FROM Sports WHERE name = 'basketball';",
    "SELECT team_id, COUNT(*) AS num_players FROM Players GROUP BY team_id;",
    "SELECT sport_id, COUNT(*) AS num_tournaments FROM Tournaments GROUP BY sport_id;",
    "SELECT first_name, last_name FROM Players WHERE date_of_birth < '1993-01-01';",
    "SELECT first_name, last_name FROM Players WHERE team_id = (SELECT team_id FROM Teams WHERE team_id = '3');",
    "SELECT match_id FROM Matches as m WHERE m.tournament_id = (SELECT tournament_id FROM Tournaments as t WHERE t.name = 'Tournament 2');",
    "SELECT name FROM Tournaments WHERE location = 'Sivas';",
    "SELECT name FROM Teams WHERE coach = (SELECT coach_id FROM Coaches WHERE first_name = 'Suzann' AND last_name = 'Robbins');",
    "SELECT first_name, last_name FROM Referees WHERE experience_years > 5;",
    "SELECT * FROM tournaments, sports WHERE tournaments.sport_id = sports.sport_id ORDER BY tournament_id ASC;",
    "SELECT player_id, first_name, last_name FROM Players WHERE age > 25 AND market_value > 10000;",
    "SELECT name FROM Sports WHERE sport_id IN (SELECT sport_id FROM Tournaments WHERE start_date BETWEEN '2023-01-01' AND '2023-12-31');",
    "SELECT COUNT(*) AS total_matches FROM Matches WHERE match_date < '2024-11-01';",
    "SELECT team_id, name FROM Teams WHERE team_id NOT IN (SELECT team_id FROM Team_Tournament_Participation WHERE tournament_id = 5);",
    "SELECT referee_id, first_name, last_name FROM Referees WHERE referee_id NOT IN (SELECT referee_id FROM Referees_in_Match WHERE match_id = 3);",
    "SELECT DISTINCT location, matches.match_id FROM Matches WHERE match_date BETWEEN '2020-11-01' AND '2024-11-30';",
    "SELECT tournament_id, COUNT(*) AS num_matches FROM Matches GROUP BY tournament_id;",
    "SELECT team_id, SUM(total_minutes_played) AS total_played_minutes FROM Players GROUP BY team_id;",
    "SELECT team_id, name FROM Teams WHERE founded_year < 2000;",
    "SELECT team_id, name FROM Teams WHERE coach IN (SELECT coach_id FROM Coaches WHERE experience_years > 10);",
    "SELECT team_id, AVG(salary) AS average_salary FROM Players GROUP BY team_id;",
    "SELECT referee_id, COUNT(*) AS total_matches FROM Referees_in_Match GROUP BY referee_id;",
    "SELECT player_id, first_name, last_name FROM Players WHERE team_captain = TRUE;",
    "SELECT COUNT(p.team_id) FROM Players as p, Teams as t WHERE p.team_id = t.team_id GROUP BY p.team_id;",
    "SELECT player_id, first_name, last_name FROM Players WHERE team_id IN (SELECT team_id FROM Teams WHERE coach IN (SELECT coach_id FROM Coaches WHERE first_name = 'Beckie' AND last_name = 'Calhoun'));",
    "SELECT team_id, COUNT(DISTINCT player_id) AS total_players FROM Players GROUP BY team_id HAVING total_players < 5;"
]

# Main execution
if __name__ == "__main__":
    conn = create_connection()
    if conn:
        create_times_table(conn)

        # List to hold execution times
        execution_times = []

        # Execute and time each query
        for query in queries:
            exec_time = execute_query_with_timing(conn, query)
            execution_times.append((query, exec_time))

        # Print each query with its execution time
        for query, exec_time in execution_times:
            print(f"Query: {query}\nExecution Time: {exec_time:.6f} seconds\n")

        # Save the results to a .txt file
        with open('query_times_with_indices.txt', 'w') as f:
            for query, exec_time in execution_times:
                f.write(f"Query: {query}\nExecution Time: {exec_time:.6f} seconds\n\n")

        conn.close()