from email.mime import message
import streamlit as st
from datetime import datetime, timezone, timedelta
from component.table_with_dialog import table_with_dialog
from service.account_service import get_all_accounts, update_account, create_account, delete_account, get_account_name_map, get_managers_name_map
from service.house_service import get_all_houses, create_house, update_house, delete_house
from service.guest_service import get_guests_with_details, get_guest_status_options, get_houses_name_map, get_houses_with_managers_map, get_marketers_name_map, create_guest, update_guest, delete_guest, get_guest_analytics_by_manager, get_guest_analytics_by_marketer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def admin_dashboard(account, current_page="dashboard"):
    if current_page == "dashboard":
        st.title("Trang Tổng Quan Quản Trị")
        
        # Dashboard metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Tổng số nhà", value="15", delta="2")
            st.write(st.session_state.get("account"))
        with col2:
            st.metric(label="Tổng số tài khoản", value="8", delta="1")
        with col3:
            st.metric(label="Tổng số khách", value="45", delta="5")
            
        # Some charts or recent activity
        st.subheader("Hoạt động gần đây")
        st.write("Danh sách các hoạt động gần đây sẽ được hiển thị ở đây...")
        
        
    elif current_page == "houses":
        st.title("Quản lý nhà")
        st.write("Chức năng quản lý nhà dành cho quản trị viên")
        
        # Get houses and managers (only accounts with "Quản lý" role)
        houses, error = get_all_houses()
        manager_map, _ = get_managers_name_map()  # Assuming this function also filters by role
        if houses and manager_map:
            # Create a copy of houses data and map manager_id to manager names
            houses_display = []
            for house in houses:
                house_copy = house.copy()
                manager_name = manager_map.get(house['manager_id'], f"ID: {house['manager_id']}")
                house_copy['manager_name'] = manager_name
                houses_display.append(house_copy)
            
            df = pd.DataFrame(houses_display)
            
            # Reverse mapping: manager names to IDs
            name_to_id_map = {name: id for id, name in manager_map.items()}
            manager_names = list(manager_map.values())
            
            def handle_edit(row_idx, new_values):
                house_id = df.iloc[row_idx]['id']
                
                # Convert manager name back to ID if changed
                if 'manager_name' in new_values:
                    manager_name = new_values['manager_name']
                    manager_id = name_to_id_map.get(manager_name)
                    if manager_id:
                        new_values['manager_id'] = manager_id
                    del new_values['manager_name']  # Remove display field
                
                updated_house, message = update_house(house_id, new_values)
                if updated_house:
                    st.success(f"Cập nhật thành công: {message}")
                    st.rerun()
                else:
                    st.error(f"Lỗi cập nhật: {message}")

            def handle_add(new_row):
                # Convert manager name to ID
                manager_name = new_row.get('manager_name', '')
                manager_id = name_to_id_map.get(manager_name)
                
                if not manager_id:
                    st.error("Vui lòng chọn quản lý hợp lệ")
                    return
                
                created_house, message = create_house(
                    manager_id=manager_id,
                    address=new_row.get('address', '')
                )
                if created_house:
                    st.success(f"Thêm thành công: {message}")
                    st.rerun()
                else:
                    st.error(f"Lỗi thêm: {message}")

            def handle_delete(row_idx, old_row):
                house_id = df.iloc[row_idx]['id']
                
                success, message = delete_house(house_id)
                if success:
                    st.success(f"Xóa thành công: {message}")
                    st.rerun()
                else:
                    st.error(f"Lỗi xóa: {message}")
            editable_table(
                df,
                key="houses_table",
                on_edit=handle_edit,
                on_add=handle_add,
                on_delete=handle_delete,
                dropdown_columns={"manager_name": manager_names},
                hidden_columns=["id", "created_at", "manager_id"],
                column_labels={
                    "address": "Địa chỉ",
                    "manager_name": "Quản lý"
                }
            )
        elif not manager_map:
            st.error("Không thể tải danh sách quản lý")
        else:
            st.error(f"Lỗi: {error or 'Không thể tải danh sách nhà'}")
        
    elif current_page == "accounts":
        st.title("Quản lý tài khoản") 
        st.write("Chức năng quản lý tài khoản người dùng")
        
        accounts, error = get_all_accounts()
        if accounts:
            df = pd.DataFrame(accounts)
            
            def handle_edit(row_idx, new_values):
                # Get the account ID from the original dataframe
                account_id = df.iloc[row_idx]['id']
                
                # Update account using service
                updated_account, message = update_account(account_id, new_values)
                if updated_account:
                    st.success(f"Cập nhật thành công: {message}")
                    st.rerun()  # Refresh the page to show updated data
                else:
                    st.error(f"Lỗi cập nhật: {message}")

            def handle_add(new_row):
                # Create new account using service
                st.write("Thêm tài khoản mới", new_row)
                created_account, message = create_account(
                    full_name=new_row.get('full_name', ''),
                    phone_number=new_row.get('phone_number', ''),
                    role=new_row.get('role', '')
                )
                if created_account:
                    st.success(f"Thêm thành công: {message}")
                    st.rerun()  # Refresh the page to show new data
                else:
                    st.error(f"Lỗi thêm: {message}")

            def handle_delete(row_idx, old_row):
                # Get the account ID from the original dataframe
                account_id = df.iloc[row_idx]['id']
                
                # Delete account using service
                success, message = delete_account(account_id)
                if success:
                    st.success(f"Xóa thành công: {message}")
                    st.rerun()  # Refresh the page to show updated data
                else:
                    st.error(f"Lỗi xóa: {message}")

            editable_table(
                df,
                key="accounts_table",
                on_edit=handle_edit,
                on_add=handle_add,
                on_delete=handle_delete,
                dropdown_columns={"role": ["Quản trị viên", "Marketing", "Quản lý"]},
                hidden_columns=["id", "created_at"],
                column_labels={
                    "full_name": "Họ và tên",
                    "phone_number": "Số điện thoại", 
                    "role": "Vai trò"
                }
            )
        else:
            st.error(error or "Không thể tải danh sách tài khoản")
    elif current_page == "guests":
        st.title("Quản lý khách")
        st.write("Chức năng quản lý khách hàng dành cho quản trị viên")
        
        # Get data
        guests, guest_error = get_guests_with_details()  # Admin sees all guests
        guest_status_options = get_guest_status_options()
        houses_name_map, house_error = get_houses_name_map()
        houses_with_managers_map, house_manager_error = get_houses_with_managers_map()
        marketers_name_map, marketer_error = get_marketers_name_map()
        
        if guest_error or house_error or house_manager_error or marketer_error:
            st.error("Không thể lấy dữ liệu. Vui lòng thử lại sau.")
            return
            
        # Add new guest dialog
        if st.button("➕ Thêm khách mới"):
            st.session_state.show_admin_add_dialog = True
            st.rerun()
            
        if st.session_state.get('show_admin_add_dialog', False):
            admin_add_guest_dialog(houses_name_map, guest_status_options, marketers_name_map)
        
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
            
            # Column configuration for admin role
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
            
            # Admin role restrictions - disable manager and marketer assignment
            hidden_columns = ['id']
            disabled_columns = ['manager_name', 'created_at']
            
            def handle_edit(row_idx, new_values):
                guest_id = df.iloc[row_idx]['id']
                # Admin can edit all fields except restricted ones
                allowed_fields = ['guest_name', 'guest_phone_number', 'view_date', 'status', 'admin_note', 'manager_note']
                updates = {k: v for k, v in new_values.items() if k in allowed_fields}
                
                # Handle house address change
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
                    result, message = update_guest(guest_id, updates, role="Admin")
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
                key="admin_guests_table",
                on_edit=handle_edit,
                on_delete=handle_delete,
                dropdown_columns=dropdown_columns,
                hidden_columns=hidden_columns,
                disabled_columns=disabled_columns,
                column_labels=column_labels,
                allow_edit=True,
                allow_delete=True  # Admin can delete
            )
            
        else:
            st.error("Không thể lấy danh sách khách hàng. Vui lòng thử lại sau.")

    elif current_page == "analytics":
        st.title("Thống kê và phân tích")
        st.write("Báo cáo thống kê khách hàng theo quản lý và nhân viên marketing")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            # Default to start of current week (Monday)
            today = datetime.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            start_date = st.date_input("Từ ngày", value=start_of_week, key="analytics_start_date")
        
        with col2:
            # Default to end of current week (Sunday)
            end_of_week = start_of_week + timedelta(days=6)
            end_date = st.date_input("Đến ngày", value=end_of_week, key="analytics_end_date")
        
        if start_date and end_date:
            start_date_str = start_date.isoformat() + "T00:00:00"
            end_date_str = end_date.isoformat() + "T23:59:59"
            
            # Get analytics data
            manager_stats, manager_error = get_guest_analytics_by_manager(start_date_str, end_date_str)
            marketer_stats, marketer_error = get_guest_analytics_by_marketer(start_date_str, end_date_str)
            
            if manager_error or marketer_error:
                st.error("Không thể lấy dữ liệu thống kê. Vui lòng thử lại sau.")
                return
            
            # Manager statistics section
            st.subheader("📊 Thống kê theo Quản lý nhà")
            if manager_stats:
                manager_df = pd.DataFrame(manager_stats)
                st.dataframe(
                    manager_df,
                    column_config={
                        "manager_name": "Quản lý",
                        "Mới": st.column_config.NumberColumn("Mới", format="%d"),
                        "Đã xem": st.column_config.NumberColumn("Đã xem", format="%d"),
                        "Quan tâm": st.column_config.NumberColumn("Quan tâm", format="%d"),
                        "Đặt cọc": st.column_config.NumberColumn("Đặt cọc", format="%d"),
                        "Hủy": st.column_config.NumberColumn("Hủy", format="%d"),
                        "total": st.column_config.NumberColumn("Tổng", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Không có dữ liệu quản lý trong khoảng thời gian này")
            
            # Marketer statistics section
            st.subheader("📈 Thống kê theo Marketing")
            if marketer_stats:
                marketer_df = pd.DataFrame(marketer_stats)
                st.dataframe(
                    marketer_df,
                    column_config={
                        "marketer_name": "Marketing",
                        "Mới": st.column_config.NumberColumn("Mới", format="%d"),
                        "Đã xem": st.column_config.NumberColumn("Đã xem", format="%d"),
                        "Quan tâm": st.column_config.NumberColumn("Quan tâm", format="%d"),
                        "Đặt cọc": st.column_config.NumberColumn("Đặt cọc", format="%d"),
                        "Hủy": st.column_config.NumberColumn("Hủy", format="%d"),
                        "total": st.column_config.NumberColumn("Tổng", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Không có dữ liệu marketing trong khoảng thời gian này")
            
            # Charts section
            st.subheader("📊 Biểu đồ thống kê")
            
            # Create charts if we have data
            if manager_stats or marketer_stats:
                chart_col1, chart_col2 = st.columns(2)
                
                # Manager chart
                with chart_col1:
                    if manager_stats:
                        st.write("**Thống kê theo Quản lý**")
                        manager_chart_df = manager_df.set_index('manager_name')[['Mới', 'Đã xem', 'Quan tâm', 'Đặt cọc', 'Hủy']]
                        fig_manager = px.bar(
                            manager_chart_df.T,
                            title="Số lượng khách theo trạng thái - Quản lý",
                            labels={'index': 'Trạng thái', 'value': 'Số lượng'},
                            height=400
                        )
                        st.plotly_chart(fig_manager, use_container_width=True)
                
                # Marketer chart
                with chart_col2:
                    if marketer_stats:
                        st.write("**Thống kê theo Marketing**")
                        marketer_chart_df = marketer_df.set_index('marketer_name')[['Mới', 'Đã xem', 'Quan tâm', 'Đặt cọc', 'Hủy']]
                        fig_marketer = px.bar(
                            marketer_chart_df.T,
                            title="Số lượng khách theo trạng thái - Marketing",
                            labels={'index': 'Trạng thái', 'value': 'Số lượng'},
                            height=400
                        )
                        st.plotly_chart(fig_marketer, use_container_width=True)
                
                # Overall status distribution pie chart
                if manager_stats and marketer_stats:
                    st.write("**Phân bố tổng thể theo trạng thái**")
                    
                    # Calculate total by status across all managers and marketers
                    total_by_status = {}
                    status_columns = ['Mới', 'Đã xem', 'Quan tâm', 'Đặt cọc', 'Hủy']
                    
                    for status in status_columns:
                        total_by_status[status] = sum(row.get(status, 0) for row in manager_stats)
                    
                    if sum(total_by_status.values()) > 0:
                        fig_pie = px.pie(
                            values=list(total_by_status.values()),
                            names=list(total_by_status.keys()),
                            title="Phân bố khách hàng theo trạng thái"
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Không có dữ liệu để hiển thị biểu đồ")

@st.dialog("Thêm khách mới")
def admin_add_guest_dialog(houses_name_map, guest_status_options, marketers_name_map):
    # Get houses with managers for dynamic manager display
    houses_with_managers_map, _ = get_houses_with_managers_map()
    
    guest_name = st.text_input("Tên khách hàng", key="admin_new_guest_name")
    guest_phone = st.text_input("Số điện thoại", key="admin_new_guest_phone")
    
    # House selection
    house_options = list(houses_name_map.values())
    house_ids = list(houses_name_map.keys())
    selected_house_address = st.selectbox("Nhà", house_options, key="admin_new_house")
    
    # Display manager for selected house
    if selected_house_address and houses_with_managers_map:
        house_id = house_ids[house_options.index(selected_house_address)]
        if house_id in houses_with_managers_map:
            manager_name = houses_with_managers_map[house_id]['manager_name']
            st.text_input("Quản lý nhà", value=manager_name, disabled=True, key="admin_new_manager_display")
    
    # Marketer selection
    marketer_options = list(marketers_name_map.values())
    marketer_ids = list(marketers_name_map.keys())
    selected_marketer_name = st.selectbox("Nhân viên marketing", marketer_options, key="admin_new_marketer")

    # Date and time selection
    st.write("**Ngày và giờ xem nhà**")
    col_date, col_time = st.columns(2)
    with col_date:
        view_date = st.date_input("Ngày xem nhà", value=None, key="admin_new_view_date")
    with col_time:
        view_time = st.time_input("Giờ xem nhà", value=None, key="admin_new_view_time")
    
    status = st.selectbox("Trạng thái", guest_status_options, key="admin_new_status")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Thêm", key="admin_add_guest_confirm", use_container_width=True):
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
                    st.session_state.show_admin_add_dialog = False
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Vui lòng điền đầy đủ thông tin")
                
    with col2:
        if st.button("Hủy", key="admin_add_guest_cancel", use_container_width=True):
            st.session_state.show_admin_add_dialog = False
            st.rerun()
