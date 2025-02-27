import streamlit as st
import pandas as pd
import re

from utils.parse_utils import parse_prompt_components
from utils.highlight_utils import (
    get_prompt_sets,
    highlight_prompt_by_component,
    highlight_prompt_usage
)
from utils.diff_utils import build_diff_html
from utils.scoring_utils import bucket_rouge, bucket_generic

def main():
    st.title("Advanced SPL Comparison and Visualization")

    # 1) File Upload
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if not uploaded_file:
        st.info("Please upload a CSV file to begin.")
        return

    # Read the CSV into a DataFrame
    df = pd.read_csv(uploaded_file)

    # 2) Column Mapping (Candidate SPL, Expected SPL, Query, Prompt, etc.)
    st.sidebar.header("Mapping CSV Columns")
    candidate_spl_col = st.sidebar.selectbox(
        "Select Candidate SPL Column",
        options=df.columns,
        index=df.columns.get_loc("Candidate SPL") if "Candidate SPL" in df.columns else 0
    )
    expected_spl_col = st.sidebar.selectbox(
        "Select Expected SPL Column",
        options=df.columns,
        index=df.columns.get_loc("Expected SPL") if "Expected SPL" in df.columns else 0
    )
    query_col = st.sidebar.selectbox(
        "Select Query Column",
        options=df.columns,
        index=df.columns.get_loc("Query") if "Query" in df.columns else 0
    )
    prompt_col = st.sidebar.selectbox(
        "Select Prompt Column",
        options=df.columns,
        index=df.columns.get_loc("Prompt") if "Prompt" in df.columns else 0
    )

    # Basic validation
    required_cols = [candidate_spl_col, expected_spl_col, query_col, prompt_col]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Column '{col}' not found in the CSV.")
            return

    # 3) Additional Score Columns
    score_columns = [
        "Rouge Score", "Bleu Score",
        "Source Score", "Index Precision", "Index Recall",
        "Sourcetype Score", "Sourcetype Precision", "Sourcetype Recall",
        "Executability Score", "Result Field Similarity Score",
        "Result Value Similarity Score", "Non-empty Execution Results",
        "Parsing Result"
    ]

    # Create "bucket" columns for each additional score if present
    for col in score_columns:
        if col in df.columns:
            bucket_col = f"{col}_Bucket"
            try:
                df[col] = pd.to_numeric(df[col])
                is_numeric = True
            except:
                is_numeric = False
            unique_vals = df[col].dropna().unique()
            if is_numeric:
                if len(unique_vals) > 2:
                    df[bucket_col] = df[col].apply(lambda v: bucket_generic(v, unique_vals))
                else:
                    # e.g. for binary columns
                    df[bucket_col] = df[col].apply(lambda v: str(int(v)) if pd.notnull(v) else "NA")
            else:
                df[bucket_col] = df[col].astype(str)
    filters = {}

    # "Reset Score Filters" button
    if st.sidebar.button("Reset Score Filters"):
        for col in score_columns:
            bucket_col = f"{col}_Bucket"
            if bucket_col in df.columns:
                default_options = sorted(df[bucket_col].dropna().unique().tolist())
                # Force re-run with all selected
                filters[bucket_col] = default_options
        st.experimental_rerun()

    # 4) Filters in Sidebar
    st.sidebar.header("Additional Score Filters")
    filters = {}
    for col in score_columns:
        bucket_col = f"{col}_Bucket"
        if bucket_col in df.columns:
            options = sorted(df[bucket_col].dropna().unique().tolist())
            selected = st.sidebar.multiselect(f"Filter {col}", options, default=options)
            filters[bucket_col] = selected

    

    # Apply filters
    filtered_df = df.copy()
    for bucket_col, selected_vals in filters.items():
        if selected_vals:
            filtered_df = filtered_df[filtered_df[bucket_col].isin(selected_vals)]

    st.write(f"### Filtered Data (Total Rows: {len(filtered_df)})")
    st.dataframe(filtered_df.head(5))

    # --- Global Summary Across All Rows ---
    total_metadata = 0
    total_relevant = 0
    total_previous = 0

    for idx, row in filtered_df.iterrows():
        metadata_text, relevant_text, previous_text = parse_prompt_components(row[prompt_col])
        _, counts = highlight_prompt_by_component(metadata_text, relevant_text, previous_text, row[candidate_spl_col])
        total_metadata += 1 if counts.get("metadata", 0) else 0
        total_relevant += 1 if counts.get("relevant", 0) else 0
        total_previous += 1 if counts.get("previous", 0) else 0

    st.markdown("## Global Prompt Word Match Summary")
    st.write(f"SPL Metadata: {total_metadata} matches")
    st.write(f"Relevant SPL Examples: {total_relevant} matches")
    st.write(f"Previous User SPL Examples: {total_previous} matches")

    # 5) Display Diff + Prompt Highlighting for each row
    for idx, row in filtered_df.iterrows():
        st.markdown("---")
        st.subheader(f"Row {idx}")
        st.markdown(f"**Query:** {row[query_col]}")

        # Parse prompt into components
        metadata_text, relevant_text, previous_text = parse_prompt_components(row[prompt_col])
        meta_set, rel_set, prev_set = get_prompt_sets(metadata_text, relevant_text, previous_text)

        # Show SPL Diff
        st.markdown("#### SPL Comparison Diff")
        diff_html = build_diff_html(row[expected_spl_col], row[candidate_spl_col], meta_set, rel_set, prev_set)

        # We'll embed the diff HTML in an iframe or use st.components
        st.components.v1.html(diff_html, height=300, scrolling=True)

        # Prompt highlighting by component
        prompt_html, counts = highlight_prompt_by_component(
            metadata_text, relevant_text, previous_text, row[candidate_spl_col]
        )
        st.markdown("**Prompt Word Match Summary:**")
        st.write(f"- SPL Metadata: {counts['metadata']} matches")
        st.write(f"- Relevant SPL Examples: {counts['relevant']} matches")
        st.write(f"- Previous User SPL Examples: {counts['previous']} matches")
        total_matches = sum(counts.values())
        st.write(f"**Total Matches:** {total_matches}")

        st.markdown("#### Prompt Highlighting by Component")
        st.markdown(prompt_html, unsafe_allow_html=True)

        # Candidate SPL with index/sourcetype highlight
        st.markdown("#### Candidate SPL with Prompt Usage Highlighting")
        highlighted_candidate = highlight_prompt_usage(row[candidate_spl_col], row[prompt_col])
        st.markdown(highlighted_candidate, unsafe_allow_html=True)

        # with st.expander("Show Full Prompt"):
        #     st.text(row[prompt_col])


if __name__ == "__main__":
    main()
