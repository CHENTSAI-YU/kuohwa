# utils/mail_utils.py
import smtplib
from email.mime.text import MIMEText
from configs import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD



class MailUtils:
    @staticmethod
    def send_forget_password_mail(to_email, new_password):
        #接收 to_email 與 new_password 並寄出信件
        try:
            subject = "【敏捷訂單系統】重設密碼通知"
            content = f"您的新臨時密碼為：{new_password}\n請登入後儘速變更密碼。"
            
            msg = MIMEText(content, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = SENDER_EMAIL
            msg["To"] = to_email  # ← 使用傳進來的 to_email

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"郵件發送失敗: {e}")
            return False


