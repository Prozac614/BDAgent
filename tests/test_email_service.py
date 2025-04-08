import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from merchant.web.services.email_service import EmailService, EmailMessage

@pytest.fixture
def email_service():
    return EmailService()

@pytest.fixture
def mock_email_message():
    return {
        "status": "success",
        "message_id": "test_message_id",
        "to": "test@example.com",
        "subject": "Test Subject"
    }

def test_send_email(email_service, mock_email_message):
    with patch('emails.Message') as mock_message:
        # Setup mock
        mock_message_instance = MagicMock()
        mock_message_instance.send.return_value = MagicMock(
            status_code=250,
            message_id="test_message_id"
        )
        mock_message.return_value = mock_message_instance

        # Test data
        to_email = "test@example.com"
        subject = "Test Subject"
        html_content = "<p>Test content</p>"
        cc = ["cc@example.com"]
        bcc = ["bcc@example.com"]
        attachments = [{
            "filename": "test.txt",
            "content_type": "text/plain",
            "data": b"test data"
        }]

        # Call the method
        result = email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            cc=cc,
            bcc=bcc,
            attachments=attachments
        )

        # Assertions
        assert result == mock_email_message
        mock_message_instance.send.assert_called_once()

def test_send_customer_engagement_email(email_service, mock_email_message):
    with patch.object(email_service, 'send_email') as mock_send_email:
        # Setup mock
        mock_send_email.return_value = mock_email_message

        # Test data
        to_email = "customer@example.com"
        customer_name = "John Doe"
        content = "Thank you for your inquiry"
        attachments = [{
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "data": b"pdf data"
        }]

        # Call the method
        result = email_service.send_customer_engagement_email(
            to_email=to_email,
            customer_name=customer_name,
            content=content,
            attachments=attachments
        )

        # Assertions
        assert result == mock_email_message
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[1]
        assert call_args['to_email'] == to_email
        assert customer_name in call_args['subject']
        assert content in call_args['html_content']

def test_connect_success(email_service):
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # Setup mock
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance

        # Test data
        email_address = "test@example.com"
        password = "test_password"
        imap_server = "imap.gmail.com"

        # Call the method
        result = email_service.connect(email_address, password, imap_server)

        # Assertions
        assert result is True
        mock_imap.assert_called_once_with(imap_server)
        mock_imap_instance.login.assert_called_once_with(email_address, password)

def test_connect_failure(email_service):
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # Setup mock to raise an exception
        mock_imap.side_effect = Exception("Connection failed")

        # Test data
        email_address = "test@example.com"
        password = "test_password"

        # Call the method
        result = email_service.connect(email_address, password)

        # Assertions
        assert result is False

def test_disconnect(email_service):
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # Setup mock
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance
        email_service.connection = mock_imap_instance

        # Call the method
        email_service.disconnect()

        # Assertions
        mock_imap_instance.close.assert_called_once()
        mock_imap_instance.logout.assert_called_once()

def test_get_inbox_messages(email_service):
    with patch('imaplib.IMAP4_SSL') as mock_imap:
        # Setup mock
        mock_imap_instance = MagicMock()
        mock_imap.return_value = mock_imap_instance
        email_service.connection = mock_imap_instance

        # Mock email data
        mock_email_data = (
            b'From: sender@example.com\r\n'
            b'Subject: Test Subject\r\n'
            b'Date: Thu, 1 Jan 2024 12:00:00 +0000\r\n'
            b'\r\n'
            b'Test content'
        )
        mock_imap_instance.search.return_value = (None, [b'1'])
        mock_imap_instance.fetch.return_value = (None, [(b'1', mock_email_data)])

        # Call the method
        messages = email_service.get_inbox_messages(limit=1)

        # Assertions
        assert len(messages) == 1
        assert isinstance(messages[0], EmailMessage)
        assert messages[0].sender == "sender@example.com"
        assert messages[0].subject == "Test Subject"
        assert "Test content" in messages[0].content
        assert isinstance(messages[0].date, datetime)

def test_get_inbox_messages_not_connected(email_service):
    # Test when not connected to email server
    with pytest.raises(Exception) as exc_info:
        email_service.get_inbox_messages()
    assert str(exc_info.value) == "未连接到邮件服务器" 