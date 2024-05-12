import json
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
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
def install_and_configure_apoc(tx):
    try:
        tx.run("RETURN apoc.version()")
    except neo4j.exceptions.ClientError as e:
        if "no procedure with the name" in str(e):
            # APOC library is not installed, proceed with installation
            result = tx.run("CALL apoc.help('apoc')")
            if result.single() is None:
                raise Exception("Failed to install APOC library")
            tx.run("CALL apoc.util.validate(true, true, true)")
        else:
            raise e
import uuid

def update_embeddings(tx):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    query = """
        MATCH (e:Example)
        WHERE e.embedding IS NULL
        RETURN e.id AS id, e.suggestions AS suggestions
    """
    results = tx.run(query)
    
    for record in results:
        suggestions = record["suggestions"]
        example_id = record["id"]
        
        if example_id is None:
            # Generate a unique identifier if id is missing
            example_id = str(uuid.uuid4())
            
            # Update the Example node with the generated id
            update_id_query = """
                MATCH (e:Example {suggestions: $suggestions})
                SET e.id = $example_id
            """
            tx.run(update_id_query, suggestions=suggestions, example_id=example_id)
            print("Updated missing id for record:", example_id)
        
        try:
            embedding = model.encode(suggestions).tolist()
            print("Embedding:", embedding)
            
            print("Record ID:", example_id)
            
            update_query = """
                MATCH (e:Example {id: $id})
                SET e.embedding = $embedding
            """
            
            print("Update query:", update_query)
            print("Parameters:", {"id": example_id, "embedding": embedding})
            
            tx.run(update_query, id=example_id, embedding=embedding)
            print("Embedding updated for record:", example_id)
        except Exception as e:
            print("Error encoding suggestions for record:", example_id)
            print("Error message:", str(e))
            
            empty_embedding = []
            update_query = """
                MATCH (e:Example {id: $id})
                SET e.embedding = $embedding
            """
            tx.run(update_query, id=example_id, embedding=empty_embedding)
            print("Empty embedding set for record:", example_id)

import numpy as np
def search_examples_by_subtopic(tx, subtopic, search_query, limit=5):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    search_embedding = model.encode(search_query)
    
    query = """
        MATCH (s:Subtopic {name: $subtopic})<-[:RELATED_TO]-(e:Example)
        RETURN e.id AS id, e.suggestions AS suggestions, e.embedding AS embedding, e.embedding IS NOT NULL AS has_embedding
    """
    results = tx.run(query, subtopic=subtopic)
    
    print("Query executed.")
    print("Subtopic:", subtopic)
    
    examples = []
    for record in results:
        print("Record:", record)
        # print("Record:", record)
        # example = record["e"]
        example_id = record["id"]
        suggestions = record["suggestions"]
        embedding = record["embedding"]
        has_embedding = record["has_embedding"]
        
        print("Embedding exists?", has_embedding)
        print("Embedding value:", embedding)
        embedding = np.array(embedding)
        similarity = np.dot(embedding, search_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(search_embedding))
        examples.append((example_id, suggestions, similarity))
        # print("Example:", example)
        # print("Example properties:", example.keys())
        # if "id" in record and "suggestions" in record and "embedding" in record:
            
            
        #     if has_embedding:
        #         embedding = np.array(embedding)
        #         similarity = np.dot(embedding, search_embedding) / (np.linalg.norm(embedding) * np.linalg.norm(search_embedding))
        #         examples.append((example_id, suggestions, similarity))
        #     else:
        #         print("Skipping record due to missing embedding.")
        # else:
        #     print("Skipping record due to missing keys.")
    
    print("Number of examples found:", len(examples))
    
    examples.sort(key=lambda x: x[2], reverse=True)
    return examples[:limit]
# def create_full_text_index(tx):
#     """Create a full-text search index for Example nodes."""
#     tx.run("""
#         CALL db.index.fulltext.createNodeIndex(
#             "examplesIndex",
#             ["Example"],
#             ["suggestions"]
#         )
#     """)

# def search_examples(tx, search_query):
#     """Search Examples using the full-text index and return results related to the 'meeting' subtopic."""
#     return tx.run("""
#         CALL db.index.fulltext.queryNodes("examplesIndex", $search_query) YIELD node, score
#         MATCH (node)-[:RELATED_TO]->(s:Subtopic {name: "meeting"})
#         RETURN node, score ORDER BY score DESC LIMIT 5
#     """, search_query=search_query)
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
            # Update existing Example nodes with embeddings
            # with driver.session() as session:
            #     session.execute_write(update_embeddings)

            subtopic_name = 'meeting'
            search_query = "effective meetings"

            with driver.session() as session:
                results = session.execute_read(search_examples_by_subtopic, subtopic_name, search_query)
                print(results)
                # for record in results:
                #     print(record["suggestions"], record["similarity"])

        finally:
            driver.close()
# if __name__ == "__main__":
#     driver = create_driver(URI, AUTH)
#     if driver:
#         try:
#             # Define the file path and subtopic name
#             # data_file_name = 'comm.json'  # Update with the actual path to your JSON file
#             # subtopic_name = 'comm'  # Define your subtopic name

#             # Use a Neo4j session to execute the transaction
#             # with driver.session() as session:
#                 # session.write_transaction(insert, data_file_name, subtopic_name)
#             # fetch_meeting_examples(driver)
#             # Update existing Example nodes with embeddings
#             with driver.session() as session:
#                 session.execute_write(install_and_configure_apoc)
#             with driver.session() as session:
#                 session.write_transaction(update_embeddings)

#             subtopic_name = 'meeting'
#             search_query = "effective meetings"

#             with driver.session() as session:
#                 results = session.read_transaction(search_examples_by_vector, subtopic_name, search_query)
#                 for record in results:
#                     print(record["e"]["suggestions"], record["similarity"])

#             # Run a test query to check data insertion
#             # read_all(driver)
#         finally:
#             driver.close()  # Ensure the driver is closed properly
