from fastapi import Depends, HTTPException

def admin_only(user_role: str = "admin"):
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
