# utils/mail_utils.py
import smtplib #Python 內建的 SMTP 客戶端模組，用來連線郵件伺服器並寄信
from email.mime.text import MIMEText #用來組成純文字格式的信件內容
from configs import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD #從設定檔匯入 SMTP 連線資訊



class MailUtils:
    @staticmethod
    def send_forget_password_mail(to_email, new_password):
        #接收 to_email 與 new_password 並寄出信件
        try:
            #信件主旨
            subject = "重設密碼通知"
            #信件內容
            content = f"您的新臨時密碼為：{new_password}\n請登入後儘速變更密碼。"

            #組成一封純文字信件（plain），編碼用 utf-8 避免中文亂碼
            #msg：建立一個「信件內容物件」
            #MIMEText 是 Python 內建函式庫的工具，專門用來包裝信件內容
            #content：信件內容
            #"plain"：代表這是純文字信件
            #"utf-8"：文字編碼
            msg = MIMEText(content, "plain", "utf-8")
            msg["Subject"]=subject #設定信件主旨，把信件的「主旨」欄位設定成 subject
            #設定「寄件人」欄位，收件人的信箱軟體會顯示這封信是從 SENDER_EMAIL（設定檔裡的 Gmail 帳號）寄出的
            msg["From"]=SENDER_EMAIL #設定寄件人（讀 configs/smtp.py 的帳號）
            #設定「收件人」欄位，指定這封信要寄給誰，值是外部呼叫這個函式時傳進來的 to_email 參數
            msg["To"]=to_email  #收件人 ← 使用傳進來的 to_email

            #用 with 語法連線 SMTP 伺服器，區塊執行完會自動關閉連線
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls() #用 TLS 加密連線
                server.login(SENDER_EMAIL, SENDER_PASSWORD) #用寄件帳號密碼登入 SMTP 伺服器
                server.send_message(msg) #把組好的信件送出
            return True #寄信成功回傳 True
        #捕捉例外
        #except Exception:：攔截「任何類型的錯誤」
        #as e：把這個攔截到的錯誤物件存到變數 e 裡
        except Exception as e:
            print(f"郵件發送失敗: {e}") #{e} 會被自動轉成錯誤訊息的文字內容
            return False #寄信失敗回傳 False，讓呼叫端（forget()）知道要擋下後續動作


