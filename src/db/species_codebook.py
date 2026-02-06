import pandas as pd
from thefuzz import fuzz, process

class SpeciesCodebook:
    def __init__(self, filename: str):
        self.codebook = pd.read_csv(filename)
        print("self.codebook columns:", self.codebook.columns.tolist())
        
    def search_by_common_name_exact(self, common_name: str):
        """Exact substring search"""
        matches = self.codebook[self.codebook['Common Name'].str.contains(common_name, case=False, na=False)]
        return matches

    def search_by_common_name_fuzzy(self, common_name: str, threshold=70):
        """Fuzzy search with similarity threshold"""
        # Get all common names (drop NaN values)
        common_names = self.codebook['Common Name'].dropna().tolist()
        
        # Find best matches using fuzzy matching
        matches = process.extract(common_name, common_names, limit=5, scorer=fuzz.partial_ratio)
        
        # Filter by threshold and get the rows
        good_matches = [match for match in matches if match[1] >= threshold]
        
        if good_matches:
            # Get the actual dataframe rows for good matches
            matched_names = [match[0] for match in good_matches]
            result = self.codebook[self.codebook['Common Name'].isin(matched_names)]
            
            # Add similarity scores
            result = result.copy()
            result['similarity_score'] = result['Common Name'].apply(
                lambda x: next(match[1] for match in good_matches if match[0] == x)
            )
            return result.sort_values('similarity_score', ascending=False)
        else:
            return pd.DataFrame()  # Empty dataframe if no good matches
            
