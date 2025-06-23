import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from component.table_with_dialog import table_with_dialog
from service.guest_service import get_guests_with_details, get_guest_status_options, get_houses_name_map, get_houses_with_managers_map, get_marketers_name_map, create_guest, update_guest, delete_guest

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

def manager_dashboard(account, current_page="dashboard"):
    if current_page == "dashboard":
        st.title("Trang Tổng Quan Quản Lý")
        
        # Dashboard metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Tổng số nhà", value="10", delta="1")
        with col2:
            st.metric(label="Tổng số khách", value="30", delta="3")
            
        # Some charts or recent activity
        st.subheader("Hoạt động gần đây")
        st.write("Danh sách các hoạt động gần đây sẽ được hiển thị ở đây...")
        
    elif current_page == "houses":
        st.title("Quản lý nhà")
        st.write("Chức năng quản lý nhà dành cho quản lý")
        # Implement house management functionality here
        
    elif current_page == "guests":
        st.title("Quản lý khách")
        st.write("Chức năng quản lý khách hàng dành cho quản lý")
        
        # Get data - manager sees guests from their managed houses
        guests, guest_error = get_guests_with_details(account_id=account['id'], role=account['role'])
        guest_status_options = get_guest_status_options()
        houses_name_map, house_error = get_houses_name_map(manager_id=account['id'])  # Only manager's houses
        houses_with_managers_map, house_manager_error = get_houses_with_managers_map(manager_id=account['id'])
        marketers_name_map, marketer_error = get_marketers_name_map()
        
        if guest_error or house_error or house_manager_error or marketer_error:
            st.error("Không thể lấy dữ liệu. Vui lòng thử lại sau.")
            return
            
        # Add new guest dialog
        if st.button("➕ Thêm khách mới"):
            st.session_state.show_manager_add_dialog = True
            st.rerun()
            
        if st.session_state.get('show_manager_add_dialog', False):
            manager_add_guest_dialog(account, houses_name_map, guest_status_options, marketers_name_map)
        
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
            
            # Column configuration for manager role
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
                'house_address': list(houses_name_map.values()),
                'marketer_name': list(marketers_name_map.values())
            }
            
            # Manager role restrictions - same as admin but for their houses only
            hidden_columns = ['id']
            disabled_columns = ['manager_name', 'admin_note', 'created_at']
            
            def handle_edit(row_idx, new_values):
                guest_id = df.iloc[row_idx]['id']
                # Manager can edit most fields except admin notes and manager assignment
                allowed_fields = ['guest_name', 'guest_phone_number', 'view_date', 'status', 'manager_note']
                updates = {k: v for k, v in new_values.items() if k in allowed_fields}
                
                # Handle house address change (only within manager's houses)
                if 'house_address' in new_values and new_values['house_address'] in houses_name_map.values():
                    house_ids = list(houses_name_map.keys())
                    house_options = list(houses_name_map.values())
                    house_id = house_ids[house_options.index(new_values['house_address'])]
                    updates['house_id'] = house_id
                    updates.pop('house_address', None)
                
                # Handle marketer change
                if 'marketer_name' in new_values and new_values['marketer_name'] in marketers_name_map.values():
                    marketer_ids = list(marketers_name_map.keys())
                    marketer_options = list(marketers_name_map.values())
                    marketer_id = marketer_ids[marketer_options.index(new_values['marketer_name'])]
                    updates['marketer_id'] = marketer_id
                    updates.pop('marketer_name', None)
                
                if updates:
                    result, message = update_guest(guest_id, updates, role=account['role'], account_id=account['id'])
                    if result:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            def handle_delete(row_idx, old_row):
                guest_id = df.iloc[row_idx]['id']
                success, message = delete_guest(guest_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            
            # Display table with dialog actions
            st.subheader("Danh sách khách hàng")
            table_with_dialog(
                df=df,
                key="manager_guests_table",
                on_edit=handle_edit,
                on_delete=handle_delete,
                dropdown_columns=dropdown_columns,
                hidden_columns=hidden_columns,
                disabled_columns=disabled_columns,
                column_labels=column_labels,
                allow_edit=True,
                allow_delete=True  # Manager can delete
            )
            
        else:
            st.error("Không thể lấy danh sách khách hàng. Vui lòng thử lại sau.")

@st.dialog("Thêm khách mới")
def manager_add_guest_dialog(account, houses_name_map, guest_status_options, marketers_name_map):
    # Get houses with managers for dynamic manager display
    houses_with_managers_map, _ = get_houses_with_managers_map(manager_id=account['id'])
    
    guest_name = st.text_input("Tên khách hàng", key="manager_new_guest_name")
    guest_phone = st.text_input("Số điện thoại", key="manager_new_guest_phone")
    
    # House selection (only manager's houses)
    house_options = list(houses_name_map.values())
    house_ids = list(houses_name_map.keys())
    selected_house_address = st.selectbox("Nhà", house_options, key="manager_new_house")
    
    # Display manager for selected house (will always be current manager)
    if selected_house_address and houses_with_managers_map:
        house_id = house_ids[house_options.index(selected_house_address)]
        if house_id in houses_with_managers_map:
            manager_name = houses_with_managers_map[house_id]['manager_name']
            st.text_input("Quản lý nhà", value=manager_name, disabled=True, key="manager_new_manager_display")
    
    # Marketer selection
    marketer_options = list(marketers_name_map.values())
    marketer_ids = list(marketers_name_map.keys())
    selected_marketer_name = st.selectbox("Nhân viên marketing", marketer_options, key="manager_new_marketer")

    # Date and time selection
    st.write("**Ngày và giờ xem nhà**")
    col_date, col_time = st.columns(2)
    with col_date:
        view_date = st.date_input("Ngày xem nhà", value=None, key="manager_new_view_date")
    with col_time:
        view_time = st.time_input("Giờ xem nhà", value=None, key="manager_new_view_time")
    
    status = st.selectbox("Trạng thái", guest_status_options, key="manager_new_status")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Thêm", key="manager_add_guest_confirm", use_container_width=True):
            if guest_name and guest_phone and selected_house_address and selected_marketer_name:
                house_id = house_ids[house_options.index(selected_house_address)]
                marketer_id = marketer_ids[marketer_options.index(selected_marketer_name)]
                
                # Combine date and time
                view_datetime = None
                if view_date and view_time:
                    view_datetime = datetime.combine(view_date, view_time).isoformat()
                elif view_date:
                    view_datetime = datetime.combine(view_date, datetime.min.time()).isoformat()
                
                result, message = create_guest(
                    marketer_id=marketer_id,
                    house_id=house_id,
                    guest_name=guest_name,
                    guest_phone_number=guest_phone,
                    view_date=view_datetime,
                    status=status
                )
                if result:
                    st.success(message)
                    st.session_state.show_manager_add_dialog = False
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Vui lòng điền đầy đủ thông tin")
                
    with col2:
        if st.button("Hủy", key="manager_add_guest_cancel", use_container_width=True):
            st.session_state.show_manager_add_dialog = False
            st.rerun()
