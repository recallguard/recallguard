from fastapi import APIRouter
from backend.api.recalls.fetch_cpsc  import fetch_cpsc
from backend.api.recalls.fetch_fda   import fetch_fda
from backend.api.recalls.fetch_usda  import fetch_usda
from backend.api.recalls.fetch_nhtsa import fetch_nhtsa
from backend.api.recalls.scrape_misc import scrape_misc


router = APIRouter()

@router.get("/test", tags=["Recalls"])
def get_test_recalls():
    return {"status": "success", "source": "recalls router working"}

@router.get("/all", tags=["Recalls"])
def get_all_recalls():
    try:
        all_data = {
            "cpsc": fetch_cpsc(),
            "fda": fetch_fda(),
            "usda": fetch_usda(),
            "nhtsa": fetch_nhtsa(),
            "misc": scrape_misc()
        }
        return {"status": "success", "data": all_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
