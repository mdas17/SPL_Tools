import re

def parse_prompt_components(prompt_text):
    """
    Assumes the prompt contains headings like:
      ### SPL metadata
      ### Relevant SPL Examples
      ### Previous user SPL Examples
    Returns: (metadata_text, relevant_text, previous_text)
    """
    metadata_text = ""
    relevant_text = ""
    previous_text = ""

    pattern = r"(?:^|\n)###\s*(SPL metadata|Relevant SPL Examples|Previous user SPL Examples)\s*\n"
    parts = re.split(pattern, prompt_text)
    current_section = None

    for i, chunk in enumerate(parts):
        if i % 2 == 1:  # heading
            current_section = chunk.strip().lower()
        else:  # text
            if current_section == "spl metadata":
                metadata_text = chunk.strip()
            elif current_section == "relevant spl examples":
                relevant_text = chunk.strip()
            elif current_section == "previous user spl examples":
                previous_text = chunk.strip()

    return metadata_text, relevant_text, previous_text