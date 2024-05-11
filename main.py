from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Now you can access the variables using os.getenv
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    
    