import pytest
from unittest.mock import Mock, patch
from merchant.crew import MerchantCrew

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_key")
    monkeypatch.setenv("SERPER_API_KEY", "test_key")

@pytest.fixture
def crew(mock_env):
    return MerchantCrew()

def test_crew_initialization(crew):
    assert crew.researcher is not None
    assert crew.writer is not None

@pytest.mark.asyncio
async def test_find_prospects(crew):
    with patch('merchant.crew.Crew') as MockCrew:
        mock_crew = Mock()
        mock_crew.kickoff.return_value = '[{"name": "Test", "email": "test@example.com"}]'
        MockCrew.return_value = mock_crew
        
        result = await crew.find_prospects("tech", "Shanghai", 1)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "name" in result[0]
        assert "email" in result[0]

@pytest.mark.asyncio
async def test_generate_engagement(crew):
    with patch('merchant.crew.Crew') as MockCrew:
        mock_crew = Mock()
        mock_crew.kickoff.return_value = '{"content": "Test", "subject": "Test", "next_action": "Test"}'
        MockCrew.return_value = mock_crew
        
        history = [
            {"created_at": "2024-01-01", "type": "email", "content": "Initial contact"}
        ]
        
        result = await crew.generate_engagement("John", "Test Corp", history)
        assert isinstance(result, dict)
        assert "content" in result
        assert "subject" in result
        assert "next_action" in result

@pytest.mark.asyncio
async def test_generate_initial_contact(crew):
    with patch('merchant.crew.Crew') as MockCrew:
        mock_crew = Mock()
        mock_crew.kickoff.return_value = '{"content": "Test", "subject": "Test"}'
        MockCrew.return_value = mock_crew
        
        result = await crew.generate_initial_contact("John", "Test Corp")
        assert isinstance(result, dict)
        assert "content" in result
        assert "subject" in result 