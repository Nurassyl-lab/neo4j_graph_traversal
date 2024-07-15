# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 10:45:07 2024

@author: Eduin Hernandez
"""
from neo4j import GraphDatabase
import regex as re
from tqdm import tqdm

from typing import Dict, List

class FbWikiGraph():
    """
    Graph Used to create and update Freebase-Wikidata Hybrid in Neo4j
    """
    def __init__(self, uri:str, user:str, password:str) -> None:
        self.uri = uri
        self.user = user
        self.password = password
    
    # Function to clear all data from the graph
    def clear_graph(self, tx):
        tx.run("MATCH (n) DETACH DELETE n")

    def get_drive(self):
        return GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    # Function to create nodes for each RDF title mapping
    def create_nodes(self, tx, rdf_valid):
        for rdf in tqdm(rdf_valid, desc='Creating nodes'):
            tx.run("CREATE (:Node {RDF: $rdf})", rdf=rdf)
    
    # Function to process the txt files and create the graph in Neo4j
    def create_graph(self, rdf_valid: List[str]) -> None:
        driver = self.get_drive()
        
        with driver.session() as session:
            # Clear the graph before adding new data
            session.execute_write(self.clear_graph)
            # Create nodes for each RDF title mapping
            session.execute_write(self.create_nodes, rdf_valid)
        driver.close()
    
    def create_link_between_nodes(self, relation_map: Dict, file_name: str) -> None:
        driver = self.get_drive()
        with driver.session() as session:
            with open(file_name, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in tqdm(lines, desc="Creating links", position=0):
                    rdf_from, prop, rdf_to = line.strip().split()
                    relation_name = re.sub('\W+', '_', relation_map[prop])  # Sanitize to create a valid relationship type
                    query = (
                        "MATCH (a:Node {RDF: $rdf_from}), (b:Node {RDF: $rdf_to}) "
                        "MERGE (a)-[r:" + relation_name + " {Title: $p_title, Property: $prop}]->(b)"
                    )
                    session.run(query, rdf_from=rdf_from, rdf_to=rdf_to,
                                p_title=relation_map[prop], prop=prop)
                    
        driver.close()
    
    def update_nodes_information(self, rdf_info_map: Dict) -> None:
        driver = self.get_drive()
        with driver.session() as session:
            for rdf, info in tqdm(rdf_info_map.items(), desc='Updating nodes'):
                query = (
                    "MATCH (n:Node {RDF: $rdf}) "
                    "SET n += {"
                    "Title: $title, "
                    "Description: $description, "
                    "MDI: $mdi, "
                    "URL: $url, "
                    "Alias: $alias"
                    "}"
                )
                session.run(query, rdf=rdf, 
                            title=info['Title'],
                            description=info['Description'],
                            mdi=info['MDI'],
                            url=info['URL'],
                            alias=info['Alias'])
        driver.close()
