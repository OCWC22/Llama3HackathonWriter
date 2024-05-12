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

def run_query(driver):
    """Run a sample query."""
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 5")
        for record in result:
            print(record)

if __name__ == "__main__":
    driver = create_driver(URI, AUTH)
    if driver:
        run_query(driver)
        driver.close()  # Ensure the driver is closed properly
