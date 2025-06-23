from supabase import acreate_client, AsyncClient, create_client, Client
from config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

async def create_async_supabase():
  supabase: AsyncClient = await acreate_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
  return supabase

