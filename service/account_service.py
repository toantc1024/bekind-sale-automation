from library.supabase import supabase

def get_account_by_phone(phone_number: str) -> dict:
    response = supabase.table("Account").select("*").eq("phone_number", phone_number).execute()
    if response.data:
        return response.data[0] 
    return None

def create_account(full_name: str, phone_number: str, role: str):
    account = get_account_by_phone(phone_number=phone_number)
    if account is not None:
        return None, "Số điện thoại đã được sử dụng"
    data = {
        "full_name": full_name,
        "phone_number": phone_number,
        "role": role
    }
    response = supabase.table("Account").insert(data).execute()
    if response.data:
        return data, "Tạo tài khoản thành công"

    return None, "Lỗi khi tạo tài khoản"

def get_all_accounts():
    response = supabase.table("Account").select("*").execute()
    if response.data:
        return response.data, "Danh sách tài khoản đã được lấy thành công"
    return None, "Không có tài khoản nào hoặc lỗi khi lấy dữ liệu"

def update_account(account_id, data):
    response = supabase.table("Account").update(data).eq("id", account_id).execute()
    if response.data:
        return response.data[0], "Cập nhật tài khoản thành công"
    return None, "Lỗi khi cập nhật tài khoản"

def delete_account(account_id):
    response = supabase.table("Account").delete().eq("id", account_id).execute()
    if response.data:
        return True, "Xóa tài khoản thành công"
    return False, "Lỗi khi xóa tài khoản"

def get_account_name_map():
    """Get mapping of account IDs to full names for dropdown selections"""
    response = supabase.table("Account").select("id, full_name").execute()
    if response.data:
        name_map = {account['id']: account['full_name'] for account in response.data}
        return name_map, "Danh sách tài khoản đã được lấy thành công"
    return {}, "Không có tài khoản nào hoặc lỗi khi lấy dữ liệu"

def get_managers_name_map():
    """Get mapping of manager account IDs to full names (only accounts with 'Quản lý' role)"""
    try:
        response = supabase.table("Account").select("id, full_name, role").execute()
        if response.data:
            # Filter accounts with exact role "Quản lý" (case-sensitive)
            managers = [account for account in response.data if account.get('role') == "Quản lý"]
            name_map = {account['id']: account['full_name'] for account in managers}
            return name_map, "Danh sách quản lý đã được lấy thành công"
        return {}, "Không có quản lý nào"
    except Exception as e:
        return {}, f"Lỗi khi lấy dữ liệu quản lý: {str(e)}"