import streamlit as st
import pandas as pd
import numpy as np
from streamlit.column_config import SelectboxColumn

def editable_table(df, key, on_edit=None, on_add=None, on_delete=None, 
                  dropdown_columns=None, disabled_columns=None, hidden_columns=None, column_labels=None):
    """
    dropdown_columns: dict of {column_name: list_of_options} or list of column names
    disabled_columns: list of column names that should be read-only
    hidden_columns: list of column names that should be completely hidden
    column_labels: dict of {original_column_name: display_label}
    """
    # Filter out hidden columns
    display_df = df.copy()
    if hidden_columns:
        display_df = display_df.drop(columns=[col for col in hidden_columns if col in display_df.columns])
    
    # Rename columns for display
    original_to_display = {}
    display_to_original = {}
    if column_labels:
        for orig_col, display_label in column_labels.items():
            if orig_col in display_df.columns:
                original_to_display[orig_col] = display_label
                display_to_original[display_label] = orig_col
        display_df = display_df.rename(columns=original_to_display)
    
    column_config = {}
    
    # Handle dropdown columns using display names
    if dropdown_columns:
        if isinstance(dropdown_columns, dict):
            for orig_col, options in dropdown_columns.items():
                display_col = original_to_display.get(orig_col, orig_col)
                if display_col in display_df.columns:
                    column_config[display_col] = SelectboxColumn(
                        options=options,
                        required=False
                    )
        elif isinstance(dropdown_columns, list):
            for orig_col in dropdown_columns:
                display_col = original_to_display.get(orig_col, orig_col)
                if display_col in display_df.columns:
                    unique_vals = sorted(display_df[display_col].dropna().unique())
                    unique_vals = [val.item() if hasattr(val, 'item') else val for val in unique_vals]
                    column_config[display_col] = SelectboxColumn(
                        options=unique_vals,
                        required=False
                    )
    
    # Handle disabled columns using display names
    if disabled_columns:
        for orig_col in disabled_columns:
            display_col = original_to_display.get(orig_col, orig_col)
            if display_col in display_df.columns:
                column_config[display_col] = st.column_config.Column(
                    disabled=True
                )

    # Show data editor
    edited_df = st.data_editor(
        display_df,
        key=key,
        num_rows="dynamic",
        column_config=column_config
    )

    # Helper to convert values to native types and map display names back to original
    def to_native_and_map(d):
        result = {}
        for display_name, value in d.items():
            orig_name = display_to_original.get(display_name, display_name)
            result[orig_name] = value.item() if hasattr(value, "item") else value
        return result

    changes = st.session_state.get(key, {})

    # Handle edits
    for row_idx, new_values in changes.get("edited_rows", {}).items():
        if on_edit:
            on_edit(row_idx=int(row_idx), new_values=to_native_and_map(new_values))

    # Handle additions
    for row in changes.get("added_rows", []):
        if on_add:
            on_add(new_row=to_native_and_map(row))

    # Handle deletions
    for idx in changes.get("deleted_rows", []):
        old_row = display_df.iloc[idx].apply(lambda x: x.item() if hasattr(x, "item") else x).to_dict()
        old_row_mapped = to_native_and_map(old_row)
        if on_delete:
            on_delete(row_idx=idx, old_row=old_row_mapped)

    return edited_df