import streamlit as st
import pandas as pd
from datetime import datetime, time
from streamlit.column_config import SelectboxColumn

def table_with_dialog(df, key, on_edit=None, on_delete=None, 
                     dropdown_columns=None, hidden_columns=None, column_labels=None,
                     disabled_columns=None, allow_edit=True, allow_delete=False):
    """
    Read-only table with dialog-based CRUD operations using st.dialog
    disabled_columns: list of column names that should be disabled in edit dialog
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
    
    # Show data editor (read-only)
    event = st.dataframe(
        display_df,
        key=f"{key}_display",
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True
    )

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 8])
    
    selected_rows = event.selection.rows if hasattr(event, 'selection') and event.selection else []
    
    with col1:
        if st.button("✏️ Sửa", disabled=not selected_rows or not allow_edit, key=f"{key}_edit_btn"):
            st.session_state[f"{key}_selected_row"] = selected_rows[0]
            st.session_state[f"{key}_show_edit"] = True
            st.rerun()
    
    with col2:
        if st.button("🗑️ Xóa", disabled=not selected_rows or not allow_delete, key=f"{key}_delete_btn"):
            st.session_state[f"{key}_selected_row"] = selected_rows[0]
            st.session_state[f"{key}_show_delete"] = True
            st.rerun()

    # Edit dialog
    if st.session_state.get(f"{key}_show_edit", False):
        edit_dialog(df, key, on_edit, dropdown_columns, hidden_columns, disabled_columns, original_to_display)

    # Delete confirmation dialog
    if st.session_state.get(f"{key}_show_delete", False):
        delete_dialog(df, key, on_delete)

    return display_df

@st.dialog("Chỉnh sửa thông tin")
def edit_dialog(df, key, on_edit, dropdown_columns, hidden_columns, disabled_columns, original_to_display):
    from service.guest_service import get_houses_with_managers_map
    
    row_idx = st.session_state.get(f"{key}_selected_row", 0)
    current_row = df.iloc[row_idx].to_dict()
    
    # Get houses with managers for dynamic updates
    houses_with_managers_map, _ = get_houses_with_managers_map()
    
    new_values = {}
    
    # Create form fields for each editable column
    for orig_col in df.columns:
        if orig_col in (hidden_columns or []):
            continue
            
        display_col = original_to_display.get(orig_col, orig_col)
        current_value = current_row[orig_col]
        is_disabled = disabled_columns and orig_col in disabled_columns
        
        # Special handling for view_date (datetime field)
        if orig_col == 'view_date':
            st.write(f"**{display_col}**")
            col_date, col_time = st.columns(2)
            
            # Parse current datetime value from formatted string
            current_date = None
            current_time = None
            if current_value and current_value != "":
                try:
                    # Parse the formatted display string (dd/mm/yyyy HH:MM)
                    dt_obj = datetime.strptime(str(current_value), "%d/%m/%Y %H:%M")
                    current_date = dt_obj.date()
                    current_time = dt_obj.time()
                except:
                    pass
            
            with col_date:
                new_date = st.date_input(
                    "Ngày", 
                    value=current_date,
                    disabled=is_disabled,
                    key=f"{key}_edit_date"
                )
            with col_time:
                new_time = st.time_input(
                    "Giờ", 
                    value=current_time,
                    disabled=is_disabled,
                    key=f"{key}_edit_time"
                )
            
            # Combine date and time to ISO format
            if new_date and new_time:
                new_datetime = datetime.combine(new_date, new_time)
                new_values[orig_col] = new_datetime.isoformat()
            elif new_date:
                new_datetime = datetime.combine(new_date, time(0, 0))
                new_values[orig_col] = new_datetime.isoformat()
            else:
                new_values[orig_col] = ""
                
        # Check if this column has dropdown options
        elif dropdown_columns and orig_col in dropdown_columns:
            options = dropdown_columns[orig_col]
            try:
                default_index = options.index(current_value) if current_value in options else 0
            except:
                default_index = 0
            new_values[orig_col] = st.selectbox(
                display_col, 
                options, 
                index=default_index,
                disabled=is_disabled,
                key=f"{key}_edit_{orig_col}"
            )
            
            # If this is house_address selection, show corresponding manager
            if orig_col == 'house_address' and houses_with_managers_map:
                selected_address = new_values[orig_col]
                # Find house_id for the selected address
                house_id = None
                for hid, house_info in houses_with_managers_map.items():
                    if house_info['address'] == selected_address:
                        house_id = hid
                        break
                
                if house_id and house_id in houses_with_managers_map:
                    manager_name = houses_with_managers_map[house_id]['manager_name']
                    # Update the manager_name field value
                    new_values['manager_name'] = manager_name
        else:
            # Regular text input with special handling for manager_name
            if orig_col == 'manager_name' and 'manager_name' in new_values:
                # Use the updated manager name from house selection
                display_value = new_values['manager_name']
            else:
                display_value = str(current_value) if current_value is not None else ""
                
            new_values[orig_col] = st.text_input(
                display_col, 
                value=display_value,
                disabled=is_disabled,
                key=f"{key}_edit_{orig_col}"
            )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lưu", key=f"{key}_save", use_container_width=True):
            # Close dialog first
            st.session_state[f"{key}_show_edit"] = False
            
            if on_edit:
                # Filter out unchanged values
                updates = {}
                for k, v in new_values.items():
                    if k == 'view_date':
                        # For datetime fields, compare the ISO strings
                        if str(v) != str(current_row[k]):
                            updates[k] = v
                    else:
                        if str(v) != str(current_row[k]):
                            updates[k] = v
                if updates:
                    on_edit(row_idx=row_idx, new_values=updates)
                else:
                    st.success("Không có thay đổi nào để lưu")
            st.rerun()
            
    with col2:
        if st.button("Hủy", key=f"{key}_cancel", use_container_width=True):
            st.session_state[f"{key}_show_edit"] = False
            st.rerun()

@st.dialog("Xác nhận xóa")
def delete_dialog(df, key, on_delete):
    row_idx = st.session_state.get(f"{key}_selected_row", 0)
    current_row = df.iloc[row_idx].to_dict()
    
    st.write("Bạn có chắc chắn muốn xóa bản ghi này?")
    st.write(f"**ID:** {current_row.get('id', 'N/A')}")
    st.write(f"**Tên khách:** {current_row.get('guest_name', 'N/A')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Xóa", key=f"{key}_confirm_delete", type="primary", use_container_width=True):
            # Close dialog first
            st.session_state[f"{key}_show_delete"] = False
            
            if on_delete:
                on_delete(row_idx=row_idx, old_row=current_row)
            st.rerun()
            
    with col2:
        if st.button("Hủy", key=f"{key}_cancel_delete", use_container_width=True):
            st.session_state[f"{key}_show_delete"] = False
            st.rerun()
