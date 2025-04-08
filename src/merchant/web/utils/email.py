import imaplib
from typing import Tuple

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
        # 创建IMAP4连接
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
        
        # 尝试登录
        imap.login(email, password)
        
        # 登录成功，关闭连接
        imap.logout()
        
        return True, "Connection successful"
    except imaplib.IMAP4.error as e:
        return False, f"IMAP error: {str(e)}"
    except Exception as e:
        return False, f"Connection error: {str(e)}" 