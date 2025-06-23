import streamlit as st 
from streamlit_local_storage import LocalStorage
from page.auth import login_page

from page.admin_page import admin_dashboard
from page.manager_page import manager_dashboard
from page.marketing_page import marketing_dashboard

def main():
    st.set_page_config(page_title="BeKind Internal", layout="wide")
    
    # Set up session states for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "guests"
    
    locals = LocalStorage()
    
    # Check if logout button was pressed (using session state)
    if "logout_clicked" not in st.session_state:
        st.session_state.logout_clicked = False
        
    if st.session_state.logout_clicked:
        locals.deleteItem("account")
        st.session_state.logout_clicked = False
        # st.rerun()
        
    account = locals.getItem("account")
    
    if account is None:
        login_page()
    else:
        # save account to session state
        if "account" not in st.session_state:
            st.session_state.account = account
        else:
            st.session_state.account.update(account)
        with st.sidebar:
            st.write(f"### Xin chào, {account.get('full_name', '')}")
            st.write(f"**Vai trò:** {account.get('role', '').capitalize()}")
            st.divider()
            role = account.get('role', '').lower()
            # if st.sidebar.button("Trang chủ", use_container_width=True, 
            #                     key="dashboard_btn",
            #                     type="primary" if st.session_state.current_page == "dashboard" else "secondary"):
            #     st.session_state.current_page = "dashboard"
            #     st.rerun()
            
            if role == "quản trị viên":
                if st.sidebar.button("Quản lý khách", use_container_width=True,
                                    key="guests_btn",
                                    type="primary" if st.session_state.current_page == "guests" else "secondary"):
                    st.session_state.current_page = "guests"
                    st.rerun()
                
            
                if st.sidebar.button("Quản lý nhà", use_container_width=True,
                                    key="houses_btn",
                                    type="primary" if st.session_state.current_page == "houses" else "secondary"):
                    st.session_state.current_page = "houses"
                    st.rerun()
                    
                if st.sidebar.button("Quản lý tài khoản", use_container_width=True,
                                    key="accounts_btn",
                                    type="primary" if st.session_state.current_page == "accounts" else "secondary"):
                    st.session_state.current_page = "accounts"
                    st.rerun()
                    

            elif role == "quản lý":
                if st.sidebar.button("Quản lý khách", use_container_width=True,
                                    key="guests_btn",
                                    type="primary" if st.session_state.current_page == "guests" else "secondary"):
                    st.session_state.current_page = "guests"
                    st.rerun()

            
            elif role == "marketing":
                if st.sidebar.button("Quản lý khách", use_container_width=True,
                                    key="guests_btn",
                                    type="primary" if st.session_state.current_page == "guests" else "secondary"):
                    st.session_state.current_page = "guests"
                    st.rerun()
            st.write("")
            st.write("")
            st.write("")
            if st.sidebar.button("Đăng xuất", use_container_width=True, type="secondary"):
                st.session_state.logout_clicked = True
                st.rerun()
        
        if role == "quản trị viên":
            admin_dashboard(account, st.session_state.current_page)
        elif role == "quản lý":
            manager_dashboard(account, st.session_state.current_page)
        elif role == "marketing":
            marketing_dashboard(account, st.session_state.current_page)
        else:
            st.error("Vai trò không xác định. Vui lòng liên hệ quản trị viên.")
    
if __name__ == "__main__":
    main()
