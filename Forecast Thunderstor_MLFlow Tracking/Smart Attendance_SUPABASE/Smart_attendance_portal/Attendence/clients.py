
from supabase import create_client, Client
from .config  import SUPABASE_URL, SUPABASE_KEY
from .logger  import get_logger

log = get_logger(__name__)
_supabase_client = None

def get_supabase_client() -> Client:
    """Return shared Supabase client, creating it on first call."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase credentials. Check Colab Secrets.")
    try:
        log.info(f"Connecting to Supabase...")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        log.info("Supabase client initialised.")
    except Exception as e:
        log.exception(f"Supabase connection failed: {e}")
        raise
    return _supabase_client
