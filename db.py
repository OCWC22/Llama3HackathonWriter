import json
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the environment variables
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Check for missing environment variables
if not URI or not USERNAME or not PASSWORD:
    raise Exception("Environment variables for Neo4j are not set properly.")

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
AUTH = (USERNAME, PASSWORD)

def create_driver(uri, auth):
    """Create a Neo4j driver instance."""
    driver = GraphDatabase.driver(uri, auth=auth)
    try:
        # Verify database connectivity
        with driver.session() as session:
            session.run("RETURN 1")
        print("Connection verified.")
    except Exception as e:
        print(f"Failed to verify connection: {e}")
    return driver

def read_all(driver):
    """Read all and print"""
    n = 0
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n")
        for record in result:
            print(record)
            n+=1
    print(f"total: {n}")

def insert(tx, data_file_name, subtopic):
    """insert all records in data_file_name under node subtopic, create node subtopic if doesn't exist"""
    # Load JSON data from file
    with open(f"data/{data_file_name}", 'r') as file:
        data = json.load(file)

    # Create the subtopic node if it doesn't exist
    tx.run("MERGE (s:Subtopic {name: $subtopic})", subtopic=subtopic)

    # Insert data under the subtopic node
    for record in data:
        tx.run("""
            MATCH (s:Subtopic {name: $subtopic})
            MERGE (e:Example {suggestions: $suggestions, source: $source})
            ON CREATE SET e.people = $people
            MERGE (e)-[:RELATED_TO]->(s)
            """,
            subtopic=subtopic,
            people=record['people'],
            suggestions=record['suggestions'],
            source=record['source']
        )

def count_meetings(tx):
    """Count the number of Meeting nodes in the database."""
    result = tx.run("MATCH (m:Subtopic meeting) RETURN count(m) AS total")
    return result.single()[0]  # Return the count of Meeting nodes

def fetch_meeting_examples(driver):
    with driver.session() as session:
        query = """
        MATCH (s:Subtopic {name: "meeting"})<-[:RELATED_TO]-(e:Example)
        RETURN e
        """
        result = session.run(query)
        for record in result:
            print(record)
        return result

# if __name__ == "__main__":
#     driver = create_driver(URI, AUTH)
#     if driver:
#         with driver.session() as session:
#             meeting_count = session.read_transaction(count_meetings)
#             print(f"Total number of Meeting nodes: {meeting_count}")
#         driver.close()
    
if __name__ == "__main__":
    driver = create_driver(URI, AUTH)
    if driver:
        try:
            # Define the file path and subtopic name
            # data_file_name = 'comm.json'  # Update with the actual path to your JSON file
            # subtopic_name = 'comm'  # Define your subtopic name

            # Use a Neo4j session to execute the transaction
            # with driver.session() as session:
                # session.write_transaction(insert, data_file_name, subtopic_name)
            fetch_meeting_examples(driver)

            # Run a test query to check data insertion
            # read_all(driver)
        finally:
            driver.close()  # Ensure the driver is closed properly
