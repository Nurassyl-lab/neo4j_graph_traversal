# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 13:30:28 2024

@author: Eduin Hernandez
"""

from typing import Dict, List
import json
import pandas as pd
import csv

from utils.fb_wiki_graph import FbWikiGraph


def load_json(file_path: str) -> Dict[str, str]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def load_rdf_valid(file_path: str) -> List[str]:
    return pd.read_csv(file_path)['RDF'].tolist()


# Function to load MDI to Title mapping from CSV
def load_rdf_info_mapping(file_path: str) -> Dict:
    mapping = {}
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            mapping[row['RDF']] = row
    return mapping


if __name__ == '__main__':
    # Constants for file paths
    RDF_MAPPING = './data/rdf_valid.csv'
    RDF_TITLE_MAPPING = './data/rdf_info.csv'
    RELATION_MAPPING = './data/unique_properties_valid.json'
    FILE = './data/modified_triplet.txt'

    #--------------------------------------------------------------------------
    rdf_info_map = load_rdf_info_mapping(RDF_TITLE_MAPPING)
    relation_map = load_json(RELATION_MAPPING)
    rdf_valid = load_rdf_valid(RDF_MAPPING)
    
    g = FbWikiGraph('bolt://localhost:7687', 'neo4j', '11082000')
    g.create_graph(rdf_valid)

    g.update_nodes_information(rdf_info_map)
    g.create_link_between_nodes(relation_map, FILE)