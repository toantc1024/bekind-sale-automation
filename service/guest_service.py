from library.supabase import supabase
from typing import List, Dict, Optional, Tuple
from datetime import datetime

def get_guests_with_details(account_id: int = None, role: str = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """
    Get guests with full details (joined with Account and House tables)
    Filters based on user role and account_id
    """
    try:
        query = supabase.table('Guest').select("""
            id,
            created_at,
            marketer_id,
            house_id,
            view_date,
            guest_name,
            guest_phone_number,
            status,
            admin_note,
            manager_note,
            marketer:Account!Guest_marketer_id_fkey(id, full_name, phone_number),
            house:House!Guest_house_id_fkey(id, address, manager:Account!House_manager_id_fkey(id, full_name))
        """)
        
        # Apply role-based filtering
        if role == "Marketing":
            query = query.eq('marketer_id', account_id)
        elif role == "Quản lý":
            # Get houses managed by this manager first
            houses_response = supabase.table('House').select('id').eq('manager_id', account_id).execute()
            if houses_response.data:
                house_ids = [house['id'] for house in houses_response.data]
                query = query.in_('house_id', house_ids)
            else:
                return [], None  # No houses managed, no guests
        
        response = query.execute()
        return response.data, None
    except Exception as e:
        return None, str(e)

def create_guest(marketer_id: int, house_id: int, guest_name: str, guest_phone_number: str, 
                view_date: str = None, status: str = "Mới") -> Tuple[Optional[Dict], Optional[str]]:
    """Create a new guest"""
    try:
        guest_data = {
            'marketer_id': marketer_id,
            'house_id': house_id,
            'guest_name': guest_name,
            'guest_phone_number': guest_phone_number,
            'status': status
        }
        if view_date:
            # Convert to proper format for database
            guest_data['view_date'] = view_date
            
        response = supabase.table('Guest').insert(guest_data).execute()
        if response.data:
            return response.data[0], "Thêm khách thành công"
        return None, "Không thể thêm khách"
    except Exception as e:
        return None, str(e)

def update_guest(guest_id: int, updates: Dict, role: str = None, account_id: int = None) -> Tuple[Optional[Dict], Optional[str]]:
    """Update guest with role-based restrictions"""
    try:
        # Role-based field restrictions
        if role in ["Marketing", "Quản lý"]:
            # Remove marketer_id from updates for non-admin roles
            updates = {k: v for k, v in updates.items() if k != 'marketer_id'}
        
        # Handle view_date conversion if it's in the updates
        if 'view_date' in updates and updates['view_date']:
            view_date_value = updates['view_date']
            # If it's already an ISO string, keep it; otherwise convert
            if not isinstance(view_date_value, str) or 'T' not in view_date_value:
                # This shouldn't happen with our new implementation, but keeping as fallback
                updates['view_date'] = str(view_date_value)
        
        response = supabase.table('Guest').update(updates).eq('id', guest_id).execute()
        if response.data:
            return response.data[0], "Cập nhật thành công"
        return None, "Không thể cập nhật"
    except Exception as e:
        return None, str(e)

def delete_guest(guest_id: int) -> Tuple[bool, str]:
    """Delete a guest (admin only)"""
    try:
        response = supabase.table('Guest').delete().eq('id', guest_id).execute()
        return True, "Xóa khách thành công"
    except Exception as e:
        return False, str(e)

def get_marketers_name_map() -> Tuple[Optional[Dict], Optional[str]]:
    """Get mapping of marketer IDs to names (Marketing role only)"""
    try:
        response = supabase.table('Account').select('id, full_name').eq('role', 'Marketing').execute()
        if response.data:
            return {account['id']: account['full_name'] for account in response.data}, None
        return {}, None
    except Exception as e:
        return None, str(e)

def get_houses_name_map(manager_id: int = None) -> Tuple[Optional[Dict], Optional[str]]:
    """Get mapping of house IDs to addresses, optionally filtered by manager"""
    try:
        query = supabase.table('House').select('id, address')
        if manager_id:
            query = query.eq('manager_id', manager_id)
        
        response = query.execute()
        if response.data:
            return {house['id']: house['address'] for house in response.data}, None
        return {}, None
    except Exception as e:
        return None, str(e)

def get_houses_with_managers_map(manager_id: int = None) -> Tuple[Optional[Dict], Optional[str]]:
    """Get mapping of house IDs to addresses and manager info, optionally filtered by manager"""
    try:
        query = supabase.table('House').select('id, address, manager:Account!House_manager_id_fkey(id, full_name)')
        if manager_id:
            query = query.eq('manager_id', manager_id)
        
        response = query.execute()
        if response.data:
            houses_map = {}
            for house in response.data:
                houses_map[house['id']] = {
                    'address': house['address'],
                    'manager_name': house['manager']['full_name'] if house['manager'] else 'N/A'
                }
            return houses_map, None
        return {}, None
    except Exception as e:
        return None, str(e)

def get_guest_status_options() -> List[str]:
    """Get available guest status options"""
    return ["Chốt", "Gần xem", "Không xem", "Đang chăm sóc", "Không chốt"]

def get_guest_analytics_by_manager(start_date: str = None, end_date: str = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """Get guest statistics grouped by manager and status within date range"""
    try:
        query = supabase.table('Guest').select("""
            status,
            house:House!Guest_house_id_fkey(
                manager:Account!House_manager_id_fkey(id, full_name)
            )
        """)
        
        if start_date:
            query = query.gte('created_at', start_date)
        if end_date:
            query = query.lte('created_at', end_date)
            
        response = query.execute()
        
        if response.data:
            # Group by manager and status
            stats = {}
            for guest in response.data:
                if guest['house'] and guest['house']['manager']:
                    manager_id = guest['house']['manager']['id']
                    manager_name = guest['house']['manager']['full_name']
                    status = guest['status']
                    
                    if manager_id not in stats:
                        stats[manager_id] = {
                            'manager_name': manager_name,
                            'Chốt': 0, 'Gần xem': 0, 'Không xem': 0, 'Đang chăm sóc': 0, 'Không chốt': 0,
                            'total': 0
                        }
                    
                    stats[manager_id][status] = stats[manager_id].get(status, 0) + 1
                    stats[manager_id]['total'] += 1
            
            return list(stats.values()), None
        return [], None
    except Exception as e:
        return None, str(e)

def get_guest_analytics_by_marketer(start_date: str = None, end_date: str = None) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """Get guest statistics grouped by marketer and status within date range"""
    try:
        query = supabase.table('Guest').select("""
            status,
            marketer:Account!Guest_marketer_id_fkey(id, full_name)
        """)
        
        if start_date:
            query = query.gte('created_at', start_date)
        if end_date:
            query = query.lte('created_at', end_date)
            
        response = query.execute()
        
        if response.data:
            # Group by marketer and status
            stats = {}
            for guest in response.data:
                if guest['marketer']:
                    marketer_id = guest['marketer']['id']
                    marketer_name = guest['marketer']['full_name']
                    status = guest['status']
                    
                    if marketer_id not in stats:
                        stats[marketer_id] = {
                            'marketer_name': marketer_name,
                            'Chốt': 0, 'Gần xem': 0, 'Không xem': 0, 'Đang chăm sóc': 0, 'Không chốt': 0,
                            'total': 0
                        }
                    
                    stats[marketer_id][status] = stats[marketer_id].get(status, 0) + 1
                    stats[marketer_id]['total'] += 1
            
            return list(stats.values()), None
        return [], None
    except Exception as e:
        return None, str(e)
