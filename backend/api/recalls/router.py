from fastapi import APIRouter
from . import fetch_cpsc, fetch_fda, fetch_usda, fetch_nhtsa, scrape_misc

router = APIRouter()

@router.get("/test", tags=["Recalls"])
def get_test_recalls():
    return {"status": "success", "source": "recalls router working"}

@router.get("/all", tags=["Recalls"])
def get_all_recalls():
    try:
        all_data = {
            "cpsc": fetch_cpsc.fetch_cpsc(),
            "fda": fetch_fda.fetch_fda(),
            "usda": fetch_usda.fetch_usda(),
            "nhtsa": fetch_nhtsa.fetch_nhtsa(),
            "misc": scrape_misc.scrape_misc()
        }
        return {"status": "success", "data": all_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


