# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:59:44 2024

@author: Eduin Hernandez
"""
import requests
from bs4 import BeautifulSoup

def fetch_title(soup: BeautifulSoup) -> str:
    try:
        # Extract title
        title_tag = soup.find("title")
        return title_tag.text.split(' - Wikidata')[0] if title_tag else ""
    except Exception as e:
        return ''
    
def fetch_description(soup: BeautifulSoup) -> str:
    try:
        # Extract English description
        description_tag = soup.find('div', class_='wikibase-entitytermsview-heading-description')
        return description_tag.text if description_tag else ""
    except Exception as e:
        return ''
    
def fetch_freebase_id(soup: BeautifulSoup) -> str:
    try:
        # Find the div with id 'P646' which presumably contains the Freebase ID
        fb_id_container = soup.find('div', id="P646")
        if fb_id_container:
            # Navigate to the specific 'a' tag that contains the Freebase ID
            fb_id_link = fb_id_container.find('div', class_="wikibase-statementview-mainsnak")
            if fb_id_link:
                fb_id_link = fb_id_link.find('a')
                if fb_id_link and fb_id_link.text:
                    return fb_id_link.text.strip()  # Return the text, stripping any extra whitespace
        return ""  # Return an empty string if any part of the path is not found or the link has no text
    
    except Exception as e:
        return ''

def fetch_wiki_url(soup: BeautifulSoup) -> str:
    try:
        url_span = soup.find('span', class_="wikibase-sitelinkview-link wikibase-sitelinkview-link-enwiki")
        if url_span:
            link = url_span.find('a')
            return link.get('href') if link else ''
        return ""  # Return an empty string if any part of the path is not found or the link has no text
    
    except Exception as e:
        return ''

def fetch_alias(soup: BeautifulSoup) -> str:
    try:
        res = ''
        alias_ul = soup.find('ul', class_="wikibase-entitytermsview-aliases")
        for alias_val in alias_ul.find_all('li', class_="wikibase-entitytermsview-aliases-alias"):
            res += alias_val.text + '|'
        if res: res = res[:-1]
        return res  # Return an empty string if any part of the path is not found or the link has no text
    except Exception as e:
        return ''
    
def fetch_property(soup: BeautifulSoup, id_val: str) -> dict:
    try:
        prop_portion = soup.find('div', id=id_val)
        
        # Initialize a dictionary to hold the instance types and their QIDs
        res = {}
        # Iterate over each instance type in the 'instance of' div
        for value_snak in prop_portion.find_all('div', class_="wikibase-statementview-mainsnak"):
            link = value_snak.find('a')
            if link:
                qid = link.get('title')  # Get the QID from the title attribute
                instance_type = link.text.strip()  # Get the instance type text
                res[instance_type] = qid
        return res
    except Exception as e:
        return {}

def fetch_property_qid(soup: BeautifulSoup, id_val: str) -> list:
    'Returns only Qid'
    try:
        prop_portion = soup.find('div', id=id_val)
        
        # Initialize a dictionary to hold the instance types and their QIDs
        res = []
        # Iterate over each instance type in the 'instance of' div
        for value_snak in prop_portion.find_all('div', class_="wikibase-statementview-mainsnak"):
            link = value_snak.find('a')
            if link: res.append(link.get('title'))  # Get the QID from the title attribute
        return res
    except Exception as e:
        return []

def fetch_base_details(rdf, results):
    r = results.copy()
    
    if not rdf:
        return r # Return placeholders when RDF is blank
    
    try:
        url = f"http://www.wikidata.org/wiki/{rdf}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            r['RDF'] = rdf 
            r['Title'] = fetch_title(soup)
            r['Description'] = fetch_description(soup)
            r['MDI'] = fetch_freebase_id(soup)
            r['URL'] = fetch_wiki_url(soup)
            r['Alias'] = fetch_alias(soup)

            return r
        else:
            raise ConnectionError(f"HTTP status code {response.status_code}")
    except Exception as e:
        return r

def fetch_details(rdf, results, p_map):
    r = results.copy()
    
    if not rdf:
        return r # Return placeholders when RDF is blank
    try:
        url = f"http://www.wikidata.org/wiki/{rdf}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for k0 in p_map.keys():
                r[k0] = fetch_property(soup, p_map[k0])
            return r
        else:
            raise ConnectionError(f"HTTP status code {response.status_code}")
    except Exception as e:
        return r
    
def fetch_details_qid(rdf, results, p_map):
    r = results.copy()
    
    if not rdf:
        return r # Return placeholders when RDF is blank
    try:
        url = f"http://www.wikidata.org/wiki/{rdf}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for k0 in p_map.keys():
                r[k0] = fetch_property_qid(soup, k0)
            return r
        else:
            raise ConnectionError(f"HTTP status code {response.status_code}")
    except Exception as e:
        return r

#------------------------------------------------------------------------------

def fetch_property_relation(soup: BeautifulSoup, id_val: str) -> dict:
    relation_div = soup.find('div', id=id_val)
    if not relation_div:
        return {}
    
    relation_container = relation_div.find('div', class_="wikibase-statementview-mainsnak-container")
    if not relation_container:
        return {}
    
    relation_mainsnak = relation_container.find('div', class_='wikibase-statementview-mainsnak')
    if not relation_mainsnak:
        return {}
    
    relation_link = relation_mainsnak.find('a', title=True)
    if not relation_link:
        return {}
    
    relation_id = relation_link.get('title').replace('Property:', '')
    return {relation_id: relation_link.text.strip()}