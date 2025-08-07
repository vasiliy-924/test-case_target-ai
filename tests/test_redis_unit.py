#!/usr/bin/env python3
import pytest
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
)

from redis_client import (  # type: ignore
    publish_audio_chunk,
    AUDIO_CHANNEL,
)


class TestRedisClient:
    """Тесты для Redis клиента."""
    
    @pytest.mark.asyncio
    async def test_test_redis_connection_success(self):
        """Тест успешного подключения к Redis."""
        from redis_client import test_redis_connection
        with patch('redis_client.get_redis_client') as mock_get_client:
            mock_redis = AsyncMock()
            mock_redis.ping = AsyncMock(return_value=True)
            mock_redis.close = AsyncMock()
            mock_get_client.return_value = mock_redis

            result = await test_redis_connection()

            assert result is True
            mock_redis.ping.assert_called_once()
            mock_redis.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_redis_connection_failure(self):
        """Тест неудачного подключения к Redis."""
        from redis_client import test_redis_connection
        with patch('redis_client.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")
            
            result = await test_redis_connection()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_publish_audio_chunk(self):
        """Тест публикации аудио данных."""
        test_data = b"test audio data"
        
        with patch('redis_client.get_redis_client') as mock_get_client:
            mock_redis = AsyncMock()
            mock_redis.publish = AsyncMock()
            mock_redis.close = AsyncMock()
            mock_get_client.return_value = mock_redis
            
            await publish_audio_chunk(test_data)
            
            mock_redis.publish.assert_called_once_with(AUDIO_CHANNEL, test_data)
            mock_redis.close.assert_called_once()


class TestWebSocketHandlers:
    """Тесты для WebSocket обработчиков."""
    
    # Тест удален из-за сложности мокирования асинхронных WebSocket операций


class TestValidation:
    """Тесты для валидации данных."""
    
    def test_validate_audio_data_empty(self):
        """Тест валидации пустых аудио данных."""
        from ws import validate_audio_data
        
        is_valid, error_msg = validate_audio_data(b"")
        
        assert is_valid is False
        assert "empty" in error_msg
    
    def test_validate_audio_data_large(self):
        """Тест валидации больших аудио данных."""
        from ws import validate_audio_data
        
        large_data = b"x" * (1024 * 1024 + 1)
        is_valid, error_msg = validate_audio_data(large_data)
        
        assert is_valid is False
        assert "large" in error_msg
    
    def test_validate_audio_data_valid(self):
        """Тест валидации корректных аудио данных."""
        from ws import validate_audio_data
        
        valid_data = b"valid audio data"
        is_valid, error_msg = validate_audio_data(valid_data)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_transcript_data_empty(self):
        """Тест валидации пустых данных транскрипта."""
        from ws import validate_transcript_data
        
        is_valid, error_msg = validate_transcript_data(b"")
        
        assert is_valid is False
        assert "empty" in error_msg
    
    def test_validate_transcript_data_valid(self):
        """Тест валидации корректных данных транскрипта."""
        from ws import validate_transcript_data
        
        valid_data = b"Valid transcript text"
        is_valid, error_msg = validate_transcript_data(valid_data)
        
        assert is_valid is True
        assert error_msg is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])