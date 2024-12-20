import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import os


class Mail:
    from_email_address = "quality_index@mail.ru"
    password = "BzJCnUCwWhabUsjp0Vfw"
    smtpobj = smtplib.SMTP('smtp.mail.ru', 25)
    smtpobj.starttls()
    smtpobj.login(from_email_address, password)

    def send_code(self, to_email_address):
        mess = MIMEMultipart()

        # HTML сообщение с красивым оформлением
        notification_message = """
        <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        color: #333;
                        padding: 20px;
                        margin: 0;
                    }
                    .email-container {
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        padding: 20px;
                        text-align: center;
                    }
                    h1 {
                        color: #0056b3;
                    }
                    p {
                        font-size: 16px;
                        line-height: 1.5;
                    }
                    .footer {
                        font-size: 12px;
                        color: #888;
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="email-container">
                    <h1>Изменение индекса качества</h1>
                    <p>Индекс качества клиентского сервиса изменился!<br>
                    Проверьте здесь: http://127.0.0.1:8000/review/</p>
                    <p>Спасибо, что вы с нами!</p>
                    <div class="footer">
                        Это письмо сгенерировано автоматически. Пожалуйста, не отвечайте на него.
                    </div>
                </div>
            </body>
        </html>
        """

        # Заголовки письма
        mess['From'] = self.from_email_address
        mess['To'] = to_email_address
        mess['Subject'] = 'Изменение индекса качества'

        # Добавляем вложение
        attachment_path = '/home/croissant/хак/index.png'
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(open(attachment_path, 'rb').read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        mess.attach(attachment)

        # Добавляем HTML сообщение
        mess.attach(MIMEText(notification_message, 'html'))

        # Отправка письма
        self.smtpobj.sendmail(self.from_email_address, to_email_address, mess.as_string())

    def close_connection(self):
        self.smtpobj.quit()
