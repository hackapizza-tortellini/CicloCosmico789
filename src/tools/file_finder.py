import os
from langgraph.graph import StateGraph
from langchain_core.tools import tool
import json
import pandas as pd

def search_pdfs_in_folder(state: StateGraph, folder_path: str = 'data/MenuTxtPdfMiner', context_chars: int = 1000):
    """
    Search for keywords in text files and return restaurant names and contexts where keywords were found.

    Args:
        state (StateGraph): State object containing 'keywords' list to search for
        folder_path (str): Path to the folder containing text files to search
        context_chars (int): Number of characters to include before and after each keyword match

    Returns:
        dict: A dictionary with two keys:
            - 'ristoranti': list of restaurant names where matches were found
            - 'contexts': list of text snippets containing the matches

    Example:
        >>> state = {'keywords': ['pizza', 'pasta']}
        >>> result = search_pdfs_in_folder(state)
        >>> # Example output:
        >>> {
        >>>     'ristoranti': ['Datapizza', 'Eco dei Sapori'],
        >>>     'contexts': [
        >>>         'Specialità della casa: pizza al algoritmo con...',
        >>>         'La nostra pasta alla matrice è...'
        >>>     ]
        >>> }
    """
    matching_files = {}
    all_contexts = []

    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r') as file:
            text = file.read()
            file_matches = False
            
            for keyword in state['keywords']:
                if keyword in text:
                    start = 0
                    while True:
                        pos = text.find(keyword, start)
                        if pos == -1:
                            break
                            
                        # Calculate context boundaries
                        context_start = max(0, pos - context_chars)
                        
                        # Extract context (only before the keyword)
                        context = text[context_start:pos + len(keyword)]
                        all_contexts.append(context)
                        file_matches = True
                        
                        start = pos + 1
            
            if file_matches:
                matching_files[filename.split('.')[0]] = True

    return {
       'ristoranti': list(matching_files.keys()),
       'contexts': all_contexts
    }

def search_pdfs_for_keyword(keyword: str, included: bool, folder_path: str = 'data/MenuTxtPdfMiner'):
    """
    Search for a single keyword in text files and return restaurant names based on inclusion/exclusion criteria.

    Args:
        keyword (str): The keyword to search for
        included (bool): If True, return files that contain the keyword. If False, return files that don't contain it
        folder_path (str): Path to the folder containing text files to search

    Returns:
        list[str]: List of restaurant names that match the criteria
    """
    matching_files = {}

    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r') as file:
            text = file.read()
            keyword_present = keyword in text
            
            if (included and keyword_present) or (not included and not keyword_present):
                matching_files[filename.split('.')[0]] = True

    return list(matching_files.keys())

def add_distance(planet: str):
    with open('data/Misc/Distanze.csv', 'r') as f:
        distance_df = pd.read_csv(f)
    return distance_df[distance_df['/'] == planet]

def search_pdfs_with_filters(state: StateGraph, folder_path: str = 'data/MenuJSON'):
    matching_files = {}
    all_contexts = []
    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r') as file:
            data = json.loads(file.read())
            file_matches = False
            
            all_included = False
            for recipe in data['recipes']:
                if state['ingredients_or_techniques']:
                    if all(keyword in str(recipe) for keyword in state['ingredients_or_techniques']):
                        all_included = True
                        break

            if all_included:
                matching_files[filename.split('.')[0]] = True
                
                # For each included keyword, find recipes containing it and add to context
                all_contexts.append('<ristorante><name>\n' + str(filename.split('.')[0]) + '\n</name>')
                all_contexts.append('<chef>\n' + str(data['chef']) + '\n</chef>')
                all_contexts.append('<pianeta>\n' + str(data['planet']) + '\n</pianeta>')
                all_contexts.append('<licences>\n' + str(data['licenses']) + '\n</licenses>')
                # all_contexts.append('distanza: ' + str(add_distance(data['planet'])))
                for recipe in data['recipes']:
                    recipe_str = str(recipe)
                    for keyword in state['ingredients_or_techniques']:
                        if keyword in recipe_str:
                            
                            all_contexts.append('<ricetta>\n' + str(recipe) + '\n</ricetta>')
                all_contexts.append('</ristorante>')

    return {
        'ristoranti': list(matching_files.keys()),
        'contexts': all_contexts
    }



# # Example usage
# query = "Quali piatti dovrei scegliere per un banchetto a tema magico che includa le celebri Cioccorane?"
# folder_path = r"data/Menu"  # Use raw string to avoid escape sequence issues

# matched_pdfs = search_pdfs_in_folder(folder_path, query)

# if matched_pdfs:
#     print("Query matched in the following PDF(s):")
#     for pdf, words in matched_pdfs.items():
#         print(f"- {pdf}: Matched words: {', '.join(words)}")
# else:
#     print("No matches found in the PDFs.")