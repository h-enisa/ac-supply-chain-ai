import httpx
from app.core.config import settings


async def send_reset_email(to_email: str, full_name: str, reset_link: str) -> bool:
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: -apple-system, sans-serif; background: #F1EFE8; padding: 40px 20px;">
      <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 32px;">
        <h2 style="font-size:20px;font-weight:700;color:#1a1a18;margin:0 0 8px;">Reset your password</h2>
        <p style="font-size:14px;color:#5F5E5A;margin:0 0 24px;">
          Hi {full_name},<br><br>
          We received a request to reset your password. Click the button below.
        </p>
        <a href="{reset_link}" style="display:block;text-align:center;background:#185FA5;color:#fff;font-size:14px;font-weight:700;padding:12px 24px;border-radius:8px;text-decoration:none;margin-bottom:24px;">
          Reset password
        </a>
        <p style="font-size:12px;color:#888;">
          This link expires in <strong>1 hour</strong>. If you didn't request this, ignore this email.
        </p>
        <hr style="border:none;border-top:0.5px solid rgba(0,0,0,0.1);margin:24px 0;">
        <p style="font-size:11px;color:#aaa;text-align:center;">
          American Computers Albania · Rruga Sulejman Delvina, Tirana
        </p>
      </div>
    </body>
    </html>
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from":    settings.RESEND_FROM_EMAIL,
                    "to":      [to_email],
                    "subject": "Reset your password — American Computers Albania",
                    "html":    html_content,
                },
                timeout=10.0,
            )
            print(f"[Email] Resend status: {response.status_code}")
            print(f"[Email] Resend response: {response.text}")
            return response.status_code == 200
    except Exception as e:
        print(f"[Email] Failed to send reset email: {e}")
        return False