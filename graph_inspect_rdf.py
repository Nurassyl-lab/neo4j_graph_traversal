# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 22:39:04 2024

@author: Eduin Hernandez
Sample code to extract matching nodes and neighborhood
"""
from utils.fb_wiki_graph import FbWikiGraph

if __name__ == '__main__':
    
    g = FbWikiGraph('bolt://localhost:7687', 'neo4j', '11082000')
    
    nodeA = g.match_node('Q76')
    
    nodesB, relsB = g.match_connected('Q76') #extracting the neighborhood of parent node