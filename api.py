from flask import Flask, request, jsonify
import pymysql
from pymysql.err import OperationalError, MySQLError
import threading
import logging
from logging.handlers import RotatingFileHandler
from queue import Queue

app = Flask(__name__)

# Configure logging
handler = RotatingFileHandler('api.log', maxBytes=1000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Database connection configuration
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "stms",
    "cursorclass": pymysql.cursors.DictCursor,
    "charset": "utf8mb4",
    "autocommit": True,  # Set autocommit to True
}

# Connection Pool Implementation
class ConnectionPool:
    def __init__(self, maxsize=10):
        self.pool = Queue(maxsize)
        self.maxsize = maxsize
        self._initialize_pool()

    def _initialize_pool(self):
        for _ in range(self.maxsize):
            connection = pymysql.connect(**dbconfig)
            self.pool.put(connection)

    def get_connection(self):
        try:
            return self.pool.get(block=True, timeout=5)
        except Exception as e:
            app.logger.error(f"Error getting connection from pool: {e}")
            raise

    def release_connection(self, connection):
        try:
            if connection.open:
                self.pool.put(connection)
            else:
                # Recreate the connection if it's closed
                new_connection = pymysql.connect(**dbconfig)
                self.pool.put(new_connection)
        except Exception as e:
            app.logger.error(f"Error releasing connection back to pool: {e}")

# Initialize the connection pool
connection_pool = ConnectionPool(maxsize=10)

# Helper function to get a connection from the pool
def get_db_connection():
    try:
        connection = connection_pool.get_connection()
        return connection
    except MySQLError as e:
        app.logger.error(f"Error getting connection from pool: {e}")
        return None

# Endpoint to fetch all tables
@app.route('/tables', methods=['GET'])
def get_tables():
    app.logger.info("Received request for /tables endpoint")
    connection = get_db_connection()
    if connection is None:
        app.logger.error("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
        table_list = [list(table.values())[0] for table in tables]
        app.logger.info(f"Returning tables: {table_list}")
        return jsonify({'tables': table_list}), 200
    except Exception as e:
        app.logger.error(f"Error fetching tables: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Endpoint to fetch data from a table
@app.route('/data/<table_name>', methods=['GET'])
def get_table_data(table_name):
    app.logger.info(f"Fetching data for table: {table_name}")
    connection = get_db_connection()
    if connection is None:
        app.logger.error("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{table_name}`;")
            rows = cursor.fetchall()

            cursor.execute(f"DESCRIBE `{table_name}`;")
            columns_info = cursor.fetchall()
            columns = [col['Field'] for col in columns_info]

        data = [row for row in rows]  # Rows are dictionaries
        return jsonify({'columns': columns, 'data': data}), 200
    except Exception as e:
        app.logger.error(f"Error fetching data for table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Endpoint to get table schema
@app.route('/schema/<table_name>', methods=['GET'])
def get_table_schema(table_name):
    app.logger.info(f"Fetching schema for table: {table_name}")
    connection = get_db_connection()
    if connection is None:
        app.logger.error("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE `{table_name}`;")
            schema = cursor.fetchall()
        columns = [{'Field': col['Field'], 'Type': col['Type'], 'Null': col['Null'], 'Key': col['Key'],
                    'Default': col['Default'], 'Extra': col['Extra']} for col in schema]
        return jsonify({'schema': columns}), 200
    except Exception as e:
        app.logger.error(f"Error fetching schema for table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Endpoint to add data to a table
@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    table_name = data.get('table_name')
    record = data.get('record')
    app.logger.info(f"Adding data to table {table_name}: {record}")

    if not table_name or not record:
        return jsonify({'error': 'Invalid data'}), 400

    connection = get_db_connection()
    if connection is None:
        app.logger.error("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            columns = ', '.join(f"`{col}`" for col in record.keys())
            placeholders = ', '.join(f"%({col})s" for col in record.keys())
            sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders});"
            cursor.execute(sql, record)
        app.logger.info(f"Data added to table {table_name}")
        return jsonify({'message': 'Data added successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error adding data to table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Endpoint to update data in a table
@app.route('/update_data', methods=['PUT'])
def update_data():
    data = request.json
    table_name = data.get('table_name')
    record = data.get('record')
    key = data.get('key')  # {'column_name': 'value'}
    app.logger.info(f"Updating data in table {table_name}: {record} with key {key}")

    if not table_name or not record or not key:
        return jsonify({'error': 'Invalid data'}), 400

    connection = get_db_connection()
    if connection is None:
        app.logger.error("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            set_clause = ', '.join(f"`{col}` = %({col})s" for col in record.keys())
            where_clause = ' AND '.join(f"`{col}` = %({col})s" for col in key.keys())
            params = {**record, **key}
            sql = f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause};"
            cursor.execute(sql, params)
        app.logger.info(f"Data updated in table {table_name}")
        return jsonify({'message': 'Data updated successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error updating data in table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Endpoint to delete data from a table
@app.route('/delete_data', methods=['DELETE'])
def delete_data():
    data = request.json
    table_name = data.get('table_name')
    key = data.get('key')  # {'column_name': 'value'}
    app.logger.info(f"Deleting data from table {table_name} with key {key}")

    if not table_name or not key:
        return jsonify({'error': 'Invalid data'}), 400

    connection = get_db_connection()
    if connection is None:
        app.logger.error("Failed to connect to the database")
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            where_clause = ' AND '.join(f"`{col}` = %({col})s" for col in key.keys())
            sql = f"DELETE FROM `{table_name}` WHERE {where_clause};"
            cursor.execute(sql, key)
        app.logger.info(f"Data deleted from table {table_name}")
        return jsonify({'message': 'Data deleted successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error deleting data from table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Endpoint to search data in a table
@app.route('/search/<table_name>', methods=['POST'])
def search_data(table_name):
    data = request.json  # Expecting a JSON object with search parameters
    use_regex = data.pop('use_regex', False)

    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500
    try:
        with connection.cursor() as cursor:
            # Fetch column types
            cursor.execute(f"DESCRIBE `{table_name}`;")
            columns_info = cursor.fetchall()
            columns = [col['Field'] for col in columns_info]
            col_types = {col['Field']: col['Type'] for col in columns_info}

            # Build WHERE clause
            where_clauses = []
            params = {}
            for col, value in data.items():
                col_type = col_types.get(col, '')
                if any(op in value for op in ['>=', '<=', '>', '<']):
                    # Handle numeric comparisons
                    operator = ''
                    for op in ['>=', '<=', '>', '<']:
                        if op in value:
                            operator = op
                            break
                    number = value.replace(operator, '').strip()
                    where_clauses.append(f"`{col}` {operator} %({col})s")
                    params[col] = number
                else:
                    if use_regex:
                        where_clauses.append(f"`{col}` LIKE %({col})s")
                        params[col] = f"%{value}%"
                    else:
                        where_clauses.append(f"`{col}` = %({col})s")
                        params[col] = value

            where_clause = " AND ".join(where_clauses)
            sql = f"SELECT * FROM `{table_name}`"
            if where_clause:
                sql += f" WHERE {where_clause}"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Prepare the response
            data = [row for row in rows]
            return jsonify({'columns': columns, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection_pool.release_connection(connection)

# Error handler to catch all exceptions and return JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {e}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
