import re

def get_prompt_sets(metadata_text, relevant_text, previous_text):
    meta_set = set(metadata_text.split())
    rel_set = set(relevant_text.split())
    prev_set = set(previous_text.split())
    return meta_set, rel_set, prev_set

def highlight_prompt_by_component(metadata_text, relevant_text, previous_text, candidate_spl):
    """
    Highlights words in each prompt component that appear in the candidate SPL.
    For metadata, also check for 'index=...' or 'sourcetype=...' vs. 'Index: ...' or 'Sourcetype: ...'
    Returns combined HTML and a dictionary with match counts.
    """
    colors = {
        "metadata": "#DAE8FC",
        "relevant": "#D5E8D4",
        "previous": "#F8CECC",
    }
    candidate_tokens = set(candidate_spl.split())
    
    def highlight_text(text, highlight_color, candidate_tokens, component):
        match_count = 0
        if component == "metadata":
            # For each candidate token of form key=value, highlight matches in the text
            for token in candidate_tokens:
                m = re.match(r'(?i)^(index|sourcetype)\s*=\s*["\']?([^"\'\s]+)["\']?$', token)
                if m:
                    key = m.group(1).lower()
                    value = m.group(2)
                    pattern = rf'(?i)\b{key}:\s*["\']?{re.escape(value)}["\']?'
                    new_text, n = re.subn(
                        pattern,
                        lambda m: f'<span style="background-color:{highlight_color}">{m.group(0)}</span>',
                        text
                    )
                    text = new_text
                    match_count += n
            return text, match_count
        else:
            words = text.split()
            new_words = []
            for word in words:
                if word in candidate_tokens:
                    new_words.append(f'<span style="background-color:{highlight_color}">{word}</span>')
                    match_count += 1
                else:
                    new_words.append(word)
            return " ".join(new_words), match_count

    highlighted_metadata, count_metadata = highlight_text(metadata_text, colors["metadata"], candidate_tokens, "metadata")
    highlighted_relevant, count_relevant = highlight_text(relevant_text, colors["relevant"], candidate_tokens, "relevant")
    highlighted_previous, count_previous = highlight_text(previous_text, colors["previous"], candidate_tokens, "previous")
    
    combined_html = f"""
    <div>
      <h4>SPL Metadata</h4>
      <p>{highlighted_metadata}</p>
      <hr>
      <h4>Relevant SPL Examples</h4>
      <p>{highlighted_relevant}</p>
      <hr>
      <h4>Previous User SPL Examples</h4>
      <p>{highlighted_previous}</p>
    </div>
    """
    counts = {
        "metadata": count_metadata,
        "relevant": count_relevant,
        "previous": count_previous
    }
    return combined_html, counts

def highlight_prompt_usage(candidate_spl, prompt_text):
    """
    For each token in the candidate SPL of form key=value (index=..., sourcetype=...),
    if the prompt has "Key: value", wrap the token in <mark>.
    """
    tokens = candidate_spl.split()
    highlighted_tokens = []
    for token in tokens:
        m = re.match(r'(?i)^(index|sourcetype)\s*=\s*["\']?([^"\'\s]+)["\']?$', token)
        if m:
            key = m.group(1).lower()
            value = m.group(2)
            pattern_prompt = rf'(?i)\b{key}:\s*["\']?{re.escape(value)}["\']?'
            if re.search(pattern_prompt, prompt_text):
                highlighted_tokens.append(f"<mark>{token}</mark>")
            else:
                highlighted_tokens.append(token)
        else:
            highlighted_tokens.append(token)
    return " ".join(highlighted_tokens)