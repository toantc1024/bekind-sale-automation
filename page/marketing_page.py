import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from service.guest_service import get_guests_with_details, get_guest_status_options, get_houses_name_map, get_houses_with_managers_map, get_marketers_name_map, create_guest, update_guest
from component.table_with_dialog import table_with_dialog

def format_vietnam_datetime(date_str):
    """Format datetime to Vietnam timezone (GMT+7)"""
    if not date_str:
        return ""
    try:
        # Parse the datetime string
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Convert to Vietnam timezone (GMT+7)
        vietnam_tz = timezone(timedelta(hours=7))
        vietnam_dt = dt.astimezone(vietnam_tz)
        return vietnam_dt.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str

def marketing_dashboard(account, current_page="dashboard"):
    if current_page == "dashboard":
        st.title("Trang Tổng Quan Marketing")
        
        # Dashboard metrics
        st.metric(label="Tổng số khách", value="25", delta="2")
            
        # Some charts or recent activity
        st.subheader("Hoạt động gần đây")
        st.write("Danh sách các hoạt động gần đây sẽ được hiển thị ở đây...")
        
    elif current_page == "guests":
        st.title("Quản lý khách")
        st.write("Chức năng quản lý khách hàng dành cho nhân viên marketing")
        
        # Get data
        guests, guest_error = get_guests_with_details(account_id=account['id'], role=account['role'])
        guest_status_options = get_guest_status_options()
        houses_name_map, house_error = get_houses_name_map()
        houses_with_managers_map, house_manager_error = get_houses_with_managers_map()
        
        if guest_error or house_error or house_manager_error:
            st.error("Không thể lấy dữ liệu. Vui lòng thử lại sau.")
            return
            
        # Add new guest dialog
        if st.button("➕ Thêm khách mới"):
            st.session_state.show_add_dialog = True
            st.rerun()
            
        if st.session_state.get('show_add_dialog', False):
            add_guest_dialog(account, houses_name_map, guest_status_options)
        
        if guests:
            # Prepare DataFrame
            df_data = []
            for guest in guests:
                df_data.append({
                    'id': guest['id'],
                    'guest_name': guest['guest_name'],
                    'guest_phone_number': guest['guest_phone_number'],
                    'house_address': guest['house']['address'],
                    'manager_name': guest['house']['manager']['full_name'],
                    'view_date': format_vietnam_datetime(guest['view_date']),
                    'status': guest['status'],
                    'marketer_name': guest['marketer']['full_name'],
                    'created_at': format_vietnam_datetime(guest['created_at']),
                    'admin_note': guest['admin_note'] or '',
                    'manager_note': guest['manager_note'] or ''
                })
            
            df = pd.DataFrame(df_data)
            
            # Column configuration for marketing role
            column_labels = {
                'id': 'ID',
                'guest_name': 'Tên khách',
                'guest_phone_number': 'Số điện thoại',
                'house_address': 'Địa chỉ nhà',
                'manager_name': 'Quản lý nhà',
                'view_date': 'Ngày và giờ xem',
                'status': 'Trạng thái',
                'marketer_name': 'Nhân viên marketing',
                'created_at': 'Ngày tạo',
                'admin_note': 'Ghi chú admin',
                'manager_note': 'Ghi chú quản lý'
            }
            
            # Dropdown options for edit dialog
            dropdown_columns = {
                'status': guest_status_options,
                'house_address': list(houses_name_map.values())
            }
            
            # Marketing role restrictions
            hidden_columns = ['id', 'created_at']
            disabled_columns = ['marketer_name', 'manager_name', 'admin_note', 'manager_note']
            
            def handle_edit(row_idx, new_values):
                guest_id = df.iloc[row_idx]['id']
                # Only allow editing specific fields for marketing role
                allowed_fields = ['guest_name', 'guest_phone_number', 'view_date', 'status']
                updates = {k: v for k, v in new_values.items() if k in allowed_fields}
                
                # Handle house address change
                if 'house_address' in new_values and new_values['house_address'] in houses_name_map.values():
                    house_ids = list(houses_name_map.keys())
                    house_options = list(houses_name_map.values())
                    house_id = house_ids[house_options.index(new_values['house_address'])]
                    updates['house_id'] = house_id
                    
                    # Update the manager name in the DataFrame for immediate UI update
                    if house_id in houses_with_managers_map:
                        df.at[row_idx, 'manager_name'] = houses_with_managers_map[house_id]['manager_name']
                    
                    updates.pop('house_address', None)  # Remove display field
                
                if updates:
                    result, message = update_guest(guest_id, updates, role=account['role'], account_id=account['id'])
                    if result:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Display table with dialog actions
            st.subheader("Danh sách khách hàng")
            table_with_dialog(
                df=df,
                key="guests_table",
                on_edit=handle_edit,
                dropdown_columns=dropdown_columns,
                hidden_columns=hidden_columns,
                disabled_columns=disabled_columns,
                column_labels=column_labels,
                allow_edit=True,
                allow_delete=False  # Marketing role cannot delete
            )
            
        else:
            st.error("Không thể lấy danh sách khách hàng. Vui lòng thử lại sau.")

@st.dialog("Thêm khách mới")
def add_guest_dialog(account, houses_name_map, guest_status_options):
    # Get houses with managers for dynamic manager display
    houses_with_managers_map, _ = get_houses_with_managers_map()
    
    guest_name = st.text_input("Tên khách hàng", key="new_guest_name")
    guest_phone = st.text_input("Số điện thoại", key="new_guest_phone")
    house_options = list(houses_name_map.values())
    house_ids = list(houses_name_map.keys())
    selected_house_address = st.selectbox("Nhà", house_options, key="new_house")
    
    # Display manager for selected house
    if selected_house_address and houses_with_managers_map:
        house_id = house_ids[house_options.index(selected_house_address)]
        if house_id in houses_with_managers_map:
            manager_name = houses_with_managers_map[house_id]['manager_name']
            st.text_input("Quản lý nhà", value=manager_name, disabled=True, key="new_manager_display")

    # Date and time selection
    st.write("**Ngày và giờ xem nhà**")
    col_date, col_time = st.columns(2)
    with col_date:
        view_date = st.date_input("Ngày xem nhà", value=None, key="new_view_date")
    with col_time:
        view_time = st.time_input("Giờ xem nhà", value=None, key="new_view_time")
    
    status = st.selectbox("Trạng thái", guest_status_options, key="new_status")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Thêm", key="add_guest_confirm", use_container_width=True):
            if guest_name and guest_phone and selected_house_address:
                house_id = house_ids[house_options.index(selected_house_address)]
                
                # Combine date and time
                view_datetime = None
                if view_date and view_time:
                    view_datetime = datetime.combine(view_date, view_time).isoformat()
                elif view_date:
                    view_datetime = datetime.combine(view_date, datetime.min.time()).isoformat()
                
                result, message = create_guest(
                    marketer_id=account['id'],
                    house_id=house_id,
                    guest_name=guest_name,
                    guest_phone_number=guest_phone,
                    view_date=view_datetime,
                    status=status
                )
                if result:
                    st.success(message)
                    st.session_state.show_add_dialog = False
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Vui lòng điền đầy đủ thông tin")
                
    with col2:
        if st.button("Hủy", key="add_guest_cancel", use_container_width=True):
            st.session_state.show_add_dialog = False
            st.rerun()