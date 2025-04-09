from imapclient import IMAPClient
import email
from email.header import decode_header
import ssl

# 连接到163邮箱IMAP服务器
def connect_to_email(user, password):
    # 创建SSL上下文
    context = ssl.create_default_context()
    
    # 连接到IMAP服务器
    server = IMAPClient('imap.163.com', ssl_context=context)
    
    # 登录
    server.login(user, password)
    
    # 发送IMAP ID信息
    id_info = {
        "name": "Python IMAP Client",
        "version": "1.0.0",
        "vendor": "Custom Client",
        "support-email": user
    }
    
    # 使用id命令发送ID信息
    server.id_(id_info)
    
    return server

# 列出所有可用的邮箱
def list_mailboxes(server):
    print("正在列出所有可用的邮箱...")
    folders = server.list_folders()
    print("可用的邮箱:")
    for folder in folders:
        print(folder)
    return folders

# 获取邮件
def fetch_emails(server):
    # 列出所有可用的邮箱
    folders = list_mailboxes(server)
    
    # 尝试选择收件箱
    print("尝试选择收件箱...")
    
    # 尝试不同的方法选择收件箱
    inbox_found = False
    
    # 方法1: 直接使用INBOX
    print("方法1: 直接使用INBOX")
    try:
        server.select_folder('INBOX')
        print("成功选择INBOX")
        inbox_found = True
    except Exception as e:
        print(f"无法选择INBOX: {e}")
    
    # 方法2: 使用/INBOX
    if not inbox_found:
        print("方法2: 使用/INBOX")
        try:
            server.select_folder('/INBOX')
            print("成功选择/INBOX")
            inbox_found = True
        except Exception as e:
            print(f"无法选择/INBOX: {e}")
    
    # 方法3: 从邮箱列表中查找收件箱
    if not inbox_found:
        print("方法3: 从邮箱列表中查找收件箱")
        for folder in folders:
            if folder[2] == 'INBOX':
                print(f"找到收件箱: {folder}")
                try:
                    server.select_folder(folder[2])
                    print(f"成功选择邮箱: {folder[2]}")
                    inbox_found = True
                    break
                except Exception as e:
                    print(f"无法选择邮箱 {folder[2]}: {e}")
    
    # 方法4: 尝试使用其他邮箱
    if not inbox_found:
        print("方法4: 尝试使用其他邮箱")
        for folder in folders:
            try:
                server.select_folder(folder[2])
                print(f"成功选择邮箱: {folder[2]}")
                inbox_found = True
                break
            except Exception as e:
                print(f"无法选择邮箱 {folder[2]}: {e}")
    
    if not inbox_found:
        print("无法找到可用的邮箱，请检查您的邮箱设置")
        return
    
    # 搜索邮件
    print("正在搜索邮件...")
    messages = server.search(['ALL'])
    
    # 如果没有邮件，直接返回
    if not messages:
        print("收件箱中没有邮件")
        return
    
    print(f"找到 {len(messages)} 封邮件，显示最近的5封...")
    
    # 取回最近的5封邮件
    for msg_id in messages[-5:]:
        msg_data = server.fetch([msg_id], ['RFC822'])
        for msg_id, data in msg_data.items():
            msg = email.message_from_bytes(data[b'RFC822'])
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')
            print(f'主题: {subject}')

# 主函数
if __name__ == "__main__":
    user = input("请输入您的邮箱地址: ")
    password = input("请输入您的邮箱密码: ")
    
    try:
        print("正在连接到邮箱服务器...")
        server = connect_to_email(user, password)
        print("连接成功！")
        fetch_emails(server)
        server.logout()
        print("已安全退出连接")
    except Exception as e:
        print(f"连接错误: {e}")
        print("提示: 请确保您使用的是授权码而不是邮箱密码。")
        print("您可以在163邮箱设置中生成授权码: 设置 -> POP3/SMTP/IMAP -> 开启IMAP服务 -> 生成授权码")