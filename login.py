from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import os, httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
    raise ValueError("❌ 환경변수가 누락되었습니다.")

router = APIRouter(prefix="/google", tags=["auth"])

@router.get("/login")
def google_login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    print("🔗 최종 URL:", google_auth_url)
    return RedirectResponse(url=google_auth_url)

@router.get("/callback")
async def google_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )

        if token_res.status_code != 200:
            return {"error": "토큰 요청 실패", "detail": token_res.text}

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        userinfo_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if userinfo_res.status_code != 200:
            return {"error": "유저 정보 조회 실패", "detail": userinfo_res.text}

        userinfo = userinfo_res.json()

    return {
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture")
    }
