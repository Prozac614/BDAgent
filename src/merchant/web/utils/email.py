import imapclient
from typing import Tuple, List, Dict
import email
from email.header import decode_header
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_imap_connection(email: str, password: str, imap_server: str, imap_port: int) -> Tuple[bool, str]:
    """验证IMAP连接
    
    Args:
        email: 邮箱地址
        password: 密码
        imap_server: IMAP服务器地址
        imap_port: IMAP服务器端口

    Returns:
        Tuple[bool, str]: (是否成功, 错误信息)
    """
    try:
        # 创建IMAPClient连接
        client = imapclient.IMAPClient(imap_server, port=imap_port, use_uid=True, ssl=True)
        
        # 尝试登录
        client.login(email, password)
        
        # 发送ID信息
        id_info = {
            "name": "Python IMAP Client",
            "version": "1.0.0",
            "vendor": "Custom Client",
            "support-email": email
        }
        client.id_(id_info)
        logger.debug(f"Sent IMAP ID info: {id_info}")
        
        # 登录成功，关闭连接
        client.logout()
        
        return True, "Connection successful"
    except imapclient.exceptions.LoginError as e:
        error_msg = str(e)
        # 检查是否是 Gmail 的不安全登录错误
        if "Unsafe Login" in error_msg and "gmail.com" in imap_server:
            return False, "Gmail 需要应用专用密码。请访问 Google 账户设置 -> 安全性 -> 2 步验证 -> 应用专用密码，生成一个应用专用密码，然后使用该密码代替您的 Gmail 密码。"
        # 检查是否是163邮箱的错误
        elif "163.com" in email or "163.com" in imap_server:
            if "AUTHENTICATE failed" in error_msg:
                return False, "163邮箱登录失败。请确保您使用的是正确的密码。如果您开启了客户端授权码，请使用授权码而不是登录密码。"
            elif "Invalid credentials" in error_msg:
                return False, "163邮箱登录失败。请确保您使用的是正确的密码。如果您开启了客户端授权码，请使用授权码而不是登录密码。"
        return False, f"IMAP error: {error_msg}"
    except ConnectionRefusedError:
        return False, f"无法连接到IMAP服务器 {imap_server}:{imap_port}。请检查服务器地址和端口是否正确，以及服务器是否在运行。"
    except TimeoutError:
        return False, f"连接IMAP服务器 {imap_server}:{imap_port} 超时。请检查网络连接和服务器状态。"
    except OSError as e:
        if e.errno == 101:  # Network is unreachable
            return False, f"无法连接到IMAP服务器 {imap_server}:{imap_port}。请检查：\n1. 网络连接是否正常\n2. 服务器地址是否正确\n3. 防火墙设置是否允许该连接\n4. DNS解析是否正常"
        elif e.errno == 111:  # Connection refused
            return False, f"IMAP服务器 {imap_server}:{imap_port} 拒绝连接。请检查服务器是否在运行以及端口是否正确。"
        else:
            return False, f"连接错误: {str(e)}"
    except Exception as e:
        return False, f"连接错误: {str(e)}"

def fetch_inbox_emails(email_binding) -> List[Dict]:
    """获取邮箱收件箱中的邮件
    
    Args:
        email_binding: 邮箱绑定信息对象

    Returns:
        List[Dict]: 邮件列表，每个邮件包含基本信息
    """
    client = None
    try:
        logger.debug(f"Connecting to IMAP server: {email_binding.imap_server}:{email_binding.imap_port}")
        # 创建IMAPClient连接
        client = imapclient.IMAPClient(email_binding.imap_server, port=email_binding.imap_port, use_uid=True, ssl=True)
        
        logger.debug(f"Logging in with email: {email_binding.email}")
        # 登录
        client.login(email_binding.email, email_binding.password)
        
        # 发送ID信息
        id_info = {
            "name": "Python IMAP Client",
            "version": "1.0.0",
            "vendor": "Custom Client",
            "support-email": email_binding.email
        }
        client.id_(id_info)
        logger.debug(f"Sent IMAP ID info: {id_info}")
        
        # 列出可用的邮箱
        logger.debug("Listing mailboxes")
        folders = client.list_folders()
        logger.debug(f"List folders result: {folders}")
        
        # 检查是否有 INBOX
        has_inbox = False
        for folder in folders:
            if folder[2] == 'INBOX':
                has_inbox = True
                break
        
        if not has_inbox:
            logger.warning("INBOX not found, trying to select it anyway")
        
        logger.debug("Selecting INBOX")
        # 选择收件箱
        client.select_folder('INBOX')
        
        # 获取邮件总数
        total_messages = len(client.search(['ALL']))
        logger.debug(f"Total messages: {total_messages}")
        
        # 只获取最近的10封邮件
        start = max(1, total_messages - 9)  # 从倒数第10封开始，或者从第1封开始
        end = total_messages
        
        logger.debug(f"Fetching messages from {start} to {end}")
        emails = []
        
        # 获取邮件ID列表
        message_ids = client.search(['ALL'])
        recent_ids = message_ids[-10:] if len(message_ids) > 10 else message_ids
        
        # 获取邮件内容
        messages = client.fetch(recent_ids, ['RFC822', 'INTERNALDATE'])
        
        for uid, message_data in messages.items():
            logger.debug(f"Processing message: {uid}")
            
            # 解析邮件内容
            email_body = message_data[b'RFC822']
            email_message = email.message_from_bytes(email_body)
            
            # 解析邮件主题
            subject = decode_header(email_message["subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # 解析发件人
            from_addr = decode_header(email_message["from"])[0][0]
            if isinstance(from_addr, bytes):
                from_addr = from_addr.decode()
            
            # 获取日期
            date = message_data[b'INTERNALDATE']
            
            # 检查是否有附件
            has_attachments = False
            for part in email_message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                if part.get_filename():
                    has_attachments = True
                    break
            
            # 构建邮件信息
            email_info = {
                "id": str(uid),
                "subject": subject,
                "from_addr": from_addr,
                "date": date.isoformat(),
                "has_attachments": has_attachments
            }
            
            emails.append(email_info)
        
        logger.debug(f"Successfully fetched {len(emails)} emails")
        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
        raise Exception(f"Failed to fetch emails: {str(e)}")
    finally:
        # 确保连接被正确关闭
        if client:
            try:
                logger.debug("Closing IMAP connection")
                client.logout()
            except Exception as e:
                logger.error(f"Error closing IMAP connection: {str(e)}")
                pass 