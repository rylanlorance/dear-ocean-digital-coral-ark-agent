import re
from datetime import datetime
from models import DCA_Agent_State


def extract_date(state: DCA_Agent_State) -> DCA_Agent_State:
    """
    Extract date from the input filename using regex patterns.
    Supports multiple date formats commonly found in image filenames.
    """
    filename = state.input_filename

    # Date patterns to try (ordered by specificity)
    patterns = [
        # YYYYMMDD (e.g., 20210421)
        (r'(\d{4})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])', '%Y%m%d'),
        # YYYY-MM-DD (e.g., 2021-04-21)
        (r'(\d{4})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])', '%Y-%m-%d'),
        # YYYY_MM_DD (e.g., 2021_04_21)
        (r'(\d{4})_(0[1-9]|1[0-2])_(0[1-9]|[12]\d|3[01])', '%Y_%m_%d'),
        # MM-DD-YYYY (e.g., 04-21-2021)
        (r'(0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])[-/](\d{4})', '%m-%d-%Y'),
        # MM_DD_YYYY (e.g., 04_21_2021)
        (r'(0[1-9]|1[0-2])_(0[1-9]|[12]\d|3[01])_(\d{4})', '%m_%d_%Y'),
        # DD-MM-YYYY (e.g., 21-04-2021) - less common, try last
        (r'(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](\d{4})', '%d-%m-%Y'),
    ]

    for pattern, date_format in patterns:
        match = re.search(pattern, filename)
        if match:
            date_str = match.group(0)
            try:
                # Normalize separators for parsing
                normalized = date_str.replace('/', '-').replace('_', '-')
                normalized_format = date_format.replace('/', '-').replace('_', '-')

                parsed_date = datetime.strptime(normalized, normalized_format)

                # Validate the date is reasonable (1990-2030)
                if 1990 <= parsed_date.year <= 2030:
                    state.date = parsed_date.strftime('%Y-%m-%d')
                    return state
            except ValueError:
                continue

    # No valid date found
    state.date = None
    return state
