from library.supabase import supabase

def get_all_houses():
    try:
        response = supabase.table("House").select("*").execute()
        if response.data:
            return response.data, "Danh sách nhà đã được lấy thành công"
        return None, "Không có nhà nào"
    except Exception as e:
        return None, f"Lỗi khi lấy dữ liệu: {str(e)}"

def create_house(manager_id: int, address: str):
    try:
        data = {
            "manager_id": manager_id,
            "address": address
        }
        response = supabase.table("House").insert(data).execute()
        if response.data:
            return response.data[0], "Tạo nhà thành công"
        return None, "Lỗi khi tạo nhà"
    except Exception as e:
        return None, f"Lỗi khi tạo nhà: {str(e)}"

def update_house(house_id: int, data: dict):
    try:
        response = supabase.table("House").update(data).eq("id", house_id).execute()
        if response.data:
            return response.data[0], "Cập nhật nhà thành công"
        return None, "Lỗi khi cập nhật nhà"
    except Exception as e:
        return None, f"Lỗi khi cập nhật nhà: {str(e)}"

def delete_house(house_id: int):
    try:
        response = supabase.table("House").delete().eq("id", house_id).execute()
        if response.data:
            return True, "Xóa nhà thành công"
        return False, "Lỗi khi xóa nhà"
    except Exception as e:
        return False, f"Lỗi khi xóa nhà: {str(e)}"

def get_house_by_id(house_id: int):
    response = supabase.table("House").select("*").eq("id", house_id).execute()
    if response.data:
        return response.data[0]
    return None