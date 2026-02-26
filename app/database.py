from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from datetime import date

#credentials for Neo4j aura database
load_dotenv()

#initialize a graphdatabase driver class, with functions to run queries
class Neo4jService:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    #Return the graph
    def get_all_nodes(self):
        query = """
            MATCH (n)-[r]->(m)
            RETURN n, r, m
        """
        result = self.driver.session().run(query)
        return [
            {
                "n": dict(record["n"]),
                "r": dict(record["r"]),
                "m": dict(record["m"])
            }
            for record in result
        ]
    
    #Check if a user exists
    def user_exists(self, name):
        query = """
        RETURN EXISTS { MATCH (u:User {name: $name})} AS exists
        """
        result = self.driver.session().run(query, name=name)
        return result.single()["exists"]

    #Create a user
    def create_user(self, name):
        query = """
        CREATE (u:User {name: $name})
        RETURN u
        """
        result = self.driver.session().run(query, name=name)
        return result.single()["u"]
    
    #Add an entry
    def create_entry(self, city, original, target, word):
        query = """
        CREATE (e:Entry {city: $city, original: $original, target: $target, word: $word})
        RETURN e
        """
        result = self.driver.session().run(query, 
                                           city=city, 
                                           original=original, 
                                           target=target, 
                                           word=word)
        return result.single()["e"]
    
    #Add a relationship
    def create_relationship(self, city, original, target, word, name):
        query = """
        MATCH (u:User {name: $name}), (e:Entry {city: $city, original: $original, target: $target, word: $word})
        CREATE (u)-[r:CREATED_BY {date: $date}]->(e)
        RETURN u,r,e
        """
        result = self.driver.session().run(query, 
                                           city=city, 
                                           original=original, 
                                           target=target, 
                                           word=word,
                                           name=name,
                                           date=date.today().isoformat())
        record = result.single()
        return record["u"], record["r"], record["e"]

"""db = Neo4jService(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

nodes = db.get_all_nodes()
casey = User("Casey")
add_user = db.create_user(casey)

print(add_user)
print(nodes)
db.close()"""
