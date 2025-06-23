import streamlit as st
from service.account_service import get_account_by_phone, create_account
from streamlit_local_storage import LocalStorage
import time

def login_page():
    # Initialize session state for login/registration success
    if "login_success" not in st.session_state:
        st.session_state.login_success = False
    if "register_success" not in st.session_state:
        st.session_state.register_success = False
    # Initialize active tab - default to 0 (login tab)
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0
        
    # Handle successful login/registration from previous run
    if st.session_state.login_success:
        st.session_state.login_success = False
        st.rerun()
    if st.session_state.register_success:
        st.session_state.register_success = False
        st.rerun()
        
    # Create tab navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Đăng nhập", 
                    type="primary" if st.session_state.active_tab == 0 else "secondary",
                    use_container_width=True):
            st.session_state.active_tab = 0
            st.rerun()
            
    with col2:
        if st.button("Đăng ký", 
                    type="primary" if st.session_state.active_tab == 1 else "secondary",
                    use_container_width=True):
            st.session_state.active_tab = 1
            st.rerun()
        
    locals = LocalStorage()
    
    # Show content based on active tab
    if st.session_state.active_tab == 0:
        st.header("Đăng nhập")
        # Show login prompt if coming from registration
        if st.session_state.get('show_login_prompt', False):
            st.markdown("<span style='color:green; font-size:16px;'>✅ Đăng ký thành công! Vui lòng đăng nhập với tài khoản vừa tạo.</span>", unsafe_allow_html=True)
            st.session_state.show_login_prompt = False
            
        phone_number = st.text_input(label="Số điện thoại", key="login_phone")
        login_btn = st.button(label="Đăng nhập")
        if login_btn:
            if not phone_number:
                st.error("Vui lòng nhập số điện thoại")
                return 
            else:
                account = get_account_by_phone(phone_number=phone_number)
                if account:
                    # Set item in localStorage
                    locals.setItem("account", account, key="account_info")
                    # Show success message
                    st.success(f"Đăng nhập thành công! Xin chào {account.get('name', '')}")
                    # Use session state to trigger rerun on next cycle
                    st.session_state.login_success = True
                    # Add delay to ensure localStorage has time to update
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Số điện thoại không tồn tại hoặc không chính xác")
    
    else:  # Registration tab
        st.header("Đăng ký")
        
        with st.form(key="signup_form"):
            full_name = st.text_input(label="Tên đầy đủ", key="signup_name")
            phone = st.text_input(label="Số điện thoại", key="signup_phone")
            role = st.selectbox(label="Vai trò", options=["Quản lý", "Marketing"], key="signup_role")
            submit_btn = st.form_submit_button(label="Đăng ký")
            
            if submit_btn:
                if not full_name or not phone:
                    st.error("Vui lòng điền đầy đủ thông tin")
                else:
                    existing_account = get_account_by_phone(phone_number=phone)
                    if existing_account:
                        st.error("Số điện thoại đã được sử dụng")
                    else:
                        new_account = create_account(full_name=full_name, phone_number=phone, role=role)
                        if new_account:
                            # Change to login tab
                            st.session_state.active_tab = 0
                            st.session_state.show_login_prompt = True
                            st.session_state.register_success = True
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Có lỗi xảy ra, vui lòng thử lại sau")

