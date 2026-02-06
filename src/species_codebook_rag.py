import json
import re
from models import DCA_Agent_State
from db.species_codebook import SpeciesCodebook
from ai_client import call_ai

def species_codebook_retrieval_agent(state: DCA_Agent_State) -> DCA_Agent_State:
    """
    Look up all common name candidates in the species codebook,
    use AI to analyze matches and select the best species ID.
    """
    # Initialize codebook
    codebook = SpeciesCodebook("../data/codebook/Master - DCA Metadata Codebook - Master.csv")
    
    # If no candidates, return early
    if not state.common_name_candidates:
        state.selected_species_id = None
        return state
    
    # Collect all matches for each candidate
    all_matches = []
    
    for candidate in state.common_name_candidates:
        common_name = candidate.common_name
        candidate_confidence = candidate.confidence_score
        
        # Try fuzzy search first
        fuzzy_matches = codebook.search_by_common_name_fuzzy(common_name, threshold=60)
        
        if not fuzzy_matches.empty:
            # Convert matches to list of dicts
            for _, row in fuzzy_matches.iterrows():
                match_data = {
                    "candidate_common_name": common_name,
                    "candidate_confidence": candidate_confidence,
                    "codebook_common_name": row.get("Common Name", ""),
                    "common_abbre": row.get("Common Abbre", ""),
                    "group_abbre": row.get("Group Abbre", ""),
                    "family": row.get("Family", ""),
                    "kingdom": row.get("Kingdom", ""),
                    "phylum": row.get("Phylum", ""),
                    "class": row.get("Class", ""),
                    "similarity_score": row.get("similarity_score", 0),
                    "match_type": "fuzzy"
                }
                all_matches.append(match_data)
        else:
            # Fallback to exact search
            exact_matches = codebook.search_by_common_name_exact(common_name)
            if not exact_matches.empty:
                for _, row in exact_matches.iterrows():
                    match_data = {
                        "candidate_common_name": common_name,
                        "candidate_confidence": candidate_confidence,
                        "codebook_common_name": row.get("Common Name", ""),
                        "common_abbre": row.get("Common Abbre", ""),
                        "group_abbre": row.get("Group Abbre", ""),
                        "family": row.get("Family", ""),
                        "kingdom": row.get("Kingdom", ""),
                        "phylum": row.get("Phylum", ""),
                        "class": row.get("Class", ""),
                        "similarity_score": 100,  # Exact match
                        "match_type": "exact"
                    }
                    all_matches.append(match_data)
    
    # If no matches found, return None
    if not all_matches:
        state.selected_species_id = None
        return state
    
    # Format matches for AI analysis
    matches_text = "\n\n".join([
        f"Match {i+1}:\n"
        f"  Candidate: {match['candidate_common_name']} (confidence: {match['candidate_confidence']:.2f})\n"
        f"  Codebook Name: {match['codebook_common_name']}\n"
        f"  Common Abbre (Species ID): {match['common_abbre']}\n"
        f"  Group Abbre: {match['group_abbre']}\n"
        f"  Family: {match['family']}\n"
        f"  Match Type: {match['match_type']}\n"
        f"  Similarity Score: {match['similarity_score']}"
        for i, match in enumerate(all_matches)
    ])
    
    # Create AI prompt to analyze and select best match
    prompt = """
    You are analyzing codebook matches for coral species common names. 
    Your task is to select the best matching species identifier (Common Abbre) from the provided matches.
    
    Consider the following factors:
    1. Candidate confidence score (higher is better)
    2. Codebook match similarity score (higher is better)
    3. Match type (exact matches are preferred over fuzzy)
    4. Context from the original filename: {input_filename}
    
    Here are all the codebook matches found:
    
    {matches}
    
    Analyze these matches and select the best species identifier. Return your response in the following JSON format:
    {{
        "selected_common_abbre": "GOOSBAR",
        "selected_common_name": "Goose Barnacle",
        "reasoning": "Brief explanation of why this match was selected"
    }}
    
    If no match is suitable, return:
    {{
        "selected_common_abbre": null,
        "selected_common_name": null,
        "reasoning": "Explanation of why no match was suitable"
    }}
    """
    
    # Call AI to analyze matches
    response = call_ai(prompt, input_filename=state.input_filename, matches=matches_text)
    
    # Parse AI response
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            selected_abbre = data.get("selected_common_abbre")
            if selected_abbre and selected_abbre.lower() != "null":
                state.selected_species_id = selected_abbre
            else:
                state.selected_species_id = None
        else:
            # Fallback: try to extract the abbreviation directly
            abbre_match = re.search(r'[A-Z]{7}', response)
            if abbre_match:
                state.selected_species_id = abbre_match.group(0)
            else:
                state.selected_species_id = None
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        # If parsing fails, set to None
        state.selected_species_id = None
    
    return state
