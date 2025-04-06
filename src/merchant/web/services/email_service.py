import emails
from emails.template import JinjaTemplate
import os
from typing import List, Optional
from pathlib import Path

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender = os.getenv("EMAIL_SENDER", "your-crm@example.com")
        
    def _create_message(
        self,
        subject: str,
        html_content: str,
        to_email: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None
    ):
        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=self.sender
        )

        # 添加收件人
        message.to = to_email
        if cc:
            message.cc = cc
        if bcc:
            message.bcc = bcc

        # 添加附件
        if attachments:
            for attachment in attachments:
                message.attach(
                    filename=attachment["filename"],
                    content_type=attachment.get("content_type", "application/octet-stream"),
                    data=attachment["data"]
                )

        return message

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None
    ) -> dict:
        """
        发送邮件
        :param to_email: 收件人邮箱
        :param subject: 邮件主题
        :param html_content: HTML格式的邮件内容
        :param cc: 抄送列表
        :param bcc: 密送列表
        :param attachments: 附件列表，每个附件是一个字典，包含 filename, content_type 和 data
        :return: 发送结果
        """
        message = self._create_message(
            subject=subject,
            html_content=html_content,
            to_email=to_email,
            cc=cc,
            bcc=bcc,
            attachments=attachments
        )

        response = message.send(
            smtp={
                "host": self.smtp_host,
                "port": self.smtp_port,
                "user": self.smtp_user,
                "password": self.smtp_password,
                "tls": True,
            }
        )

        if response.status_code not in [250, 200]:
            raise Exception(f"Failed to send email: {response.error}")

        return {
            "status": "success",
            "message_id": response.message_id,
            "to": to_email,
            "subject": subject
        }

    def send_customer_engagement_email(
        self,
        to_email: str,
        customer_name: str,
        content: str,
        attachments: Optional[List[dict]] = None
    ) -> dict:
        """
        发送客户互动邮件
        :param to_email: 客户邮箱
        :param customer_name: 客户名称
        :param content: 邮件内容
        :param attachments: 附件列表
        :return: 发送结果
        """
        subject = f"关于您的业务咨询 - {customer_name}"
        
        # 这里可以使用模板引擎来渲染邮件内容
        html_content = f"""
        <html>
            <body>
                <p>尊敬的 {customer_name}：</p>
                <div>{content}</div>
                <p>
                    <br>
                    祝好，<br>
                    您的客户经理
                </p>
            </body>
        </html>
        """
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            attachments=attachments
        ) 