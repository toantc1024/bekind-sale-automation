import streamlit as st
from streamlit_local_storage import LocalStorage
from library.demo_func import add_to_local, get_from_local, set_item

from streamlit_local_storage import LocalStorage

locals = LocalStorage()

item = locals.getItem('1"')
st.write(f"Item from local storage: {item}")
set_item()
# if item is not None:
#     st.write(f"Item from local storage: {item}")
# else:
#     itemKey = "camera"
#     itemValue = {"DOG": 123, "CAT": 456 }
#     add_to_local(itemKey, itemValue)


# import streamlit as st
# from service.account_service import get_account_by_phone
# from page.auth import login_page
# from library.supabase import supabase
# from library.local_storage import LocalStorageManager
# from page.property_management import display_property_management
# from page.client_management import display_client_management
# from page.account_management import display_account_management

# def main():
#     locals = LocalStorageManager()
    
#     account = locals.get_from_local_storage("account")

#     if account is None:
#         st.title("Bekind")
#         login_page(locals=locals)
#     else:
#         role = account.get("role", "").lower()
        
#         # Sidebar for navigation
#         with st.sidebar:
#             st.title(f"Xin chào, {account.get('name', '')}")
#             st.text(f"Vai trò: {role.upper()}")
#             st.divider()
            
#             # Dynamic sidebar based on role
#             if role == "admin":
#                 page = st.radio("Chọn trang:", ["Trang chủ", "Quản lý nhà", "Quản lý khách", "Quản lý tài khoản"])
#             elif role == "manager":
#                 page = st.radio("Chọn trang:", ["Trang chủ", "Quản lý nhà", "Quản lý khách"])
#             elif role == "marketer":
#                 page = st.radio("Chọn trang:", ["Trang chủ", "Quản lý khách"])
#             else:
#                 page = "Trang chủ"  # Default fallback
                
#             if st.button("Đăng xuất"):
#                 locals.remove_from_local_storage("account")
#                 st.rerun()
        
#         # Display selected page
#         if page == "Trang chủ":
#             st.title("Bekind - Trang chủ")
#             st.write(f"Chào mừng {account.get('name', '')} đến với hệ thống Bekind!")
            
#         elif page == "Quản lý nhà":
#             if role in ["admin", "manager"]:
#                 display_property_management()
#             else:
#                 st.error("Bạn không có quyền truy cập trang này!")
                
#         elif page == "Quản lý khách":
#             display_client_management()
            
#         elif page == "Quản lý tài khoản" and role == "admin":
#             display_account_management()

# if __name__ == "__main__":
#     main()