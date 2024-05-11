from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def connect_and_query():
    # Get environment variables
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')

    # Initialize the Neo4j driver
    driver = GraphDatabase.driver(uri, auth=(username, password))
    ...

    # Initialize the Neo4j driver
    driver = GraphDatabase.driver(uri, auth=(username, password))

    # Define a simple query function
    def execute_query(tx):
        # Example query to return 10 nodes (modify as needed)
        return list(tx.run("MATCH (n) RETURN n LIMIT 10"))

    # Execute the query within a session
    with driver.session() as session:
        result = session.write_transaction(execute_query)
        for record in result:
            print(record)  # Print each record returned by the query

    # Close the driver
    driver.close()

def load_data_from_csv():
    # Get environment variables
    uri = os.environ.get('NEO4J_URI')
    username = os.environ.get('NEO4J_USERNAME')
    password = os.environ.get('NEO4J_PASSWORD')
    csv_url = os.environ.get('CSV_URL')

    driver = GraphDatabase.driver(uri, auth=(username, password))

    def load_csv(tx):
        query = """
        LOAD CSV WITH HEADERS FROM $url AS row
        CREATE (n:Person {name: row.name, age: toInteger(row.age)})
        """
        tx.run(query, url=csv_url)

    with driver.session() as session:
        session.write_transaction(load_csv)

    driver.close()

if __name__ == "__main__":
    connect_and_query()
    load_data_from_csv()
