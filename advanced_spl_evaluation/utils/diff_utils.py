import difflib

def build_diff_html(expected_spl, candidate_spl, meta_set, rel_set, prev_set):
    """
    Uses difflib.HtmlDiff to create a side-by-side diff table
    comparing Expected SPL and Candidate SPL.
    """
    expected_tokens = expected_spl.split()
    candidate_tokens = candidate_spl.split()

    html_diff = difflib.HtmlDiff(wrapcolumn=60).make_table(
        fromlines=expected_tokens,
        tolines=candidate_tokens,
        fromdesc='Expected SPL',
        todesc='Candidate SPL',
        context=True,
        numlines=2
    )
    # Wrap in minimal HTML or just return the table snippet
    full_html = f"""
    <html>
    <head>
      <style>
      table.diff {{font-family: monospace; border: 1px solid #ccc; border-collapse: collapse; width: 100%;}}
      table.diff th, table.diff td {{border: 1px solid #ccc; padding: 4px;}}
      .diff_header {{background-color: #f0f0f0;}}
      .diff_next {{background-color: #fafafa;}}
      </style>
    </head>
    <body>
    {html_diff}
    </body>
    </html>
    """
    return full_html