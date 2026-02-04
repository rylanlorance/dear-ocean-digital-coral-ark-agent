import json
import re
from models import DCA_Agent_State, CommonNameCandidate
from ai_client import call_ai

def extract_common_name_candidates(state: DCA_Agent_State) -> DCA_Agent_State:
    """
    Extract common name candidates from the input filename using AI.
    """
    prompt = """
    You are a tool that extracts species common names from image filename strings. 
    Examples of common names include "Antler Coral" and "Cauliflower Coral".
    Many of the file names present in the Digital Coral Ark are incorrectly formatted, so 
    generate 2-3 potential common names with confidence scores.
    
    Given the following filename, extract the common name of the coral species present in the image.
    If no common name can be determined, return None.

    The common name will always be two or three words long. It will not contain any numbers or special characters.
    Ensure that your output is in the following format:
    {{
        "common_name": "Antler Coral",
        "confidence_score": 0.95
    }}
    
    Filename: {filename}
    """
    
    response = call_ai(prompt, filename=state.input_filename)
    
    # Parse the JSON response
    state.common_name_candidates = []
    
    if response.strip() and response.strip().lower() != "none":
        try:
            # Try to extract JSON from the response (in case there's extra text)
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                common_name = data.get("common_name", "").strip()
                confidence_score = float(data.get("confidence_score", 1.0))
                
                if common_name:
                    state.common_name_candidates = [
                        CommonNameCandidate(
                            common_name=common_name,
                            confidence_score=confidence_score
                        )
                    ]
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: if JSON parsing fails, try to extract just the common name
            # Remove any JSON-like structure and get the text
            cleaned = re.sub(r'[{{}}"]', '', response).strip()
            if cleaned and cleaned.lower() != "none":
                state.common_name_candidates = [
                    CommonNameCandidate(common_name=cleaned, confidence_score=0.5)
                ]
    
    return state