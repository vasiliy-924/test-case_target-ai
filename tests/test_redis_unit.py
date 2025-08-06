#!/usr/bin/env python3
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from redis_client import (
    get_redis_client,
    test_redis_connection,
    publish_audio_chunk,
    subscribe_to_transcripts,
    AUDIO_CHANNEL,
    TRANSCRIPTS_CHANNEL
)


class TestRedisClient:
    """Тесты для Redis клиента."""
    
    @pytest.mark.asyncio
    async def test_get_redis_client(self):
        """Тест создания Redis клиента."""
        with patch('redis_client.aioredis.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            mock_from_url.return_value = mock_redis
            
            client = await get_redis_client()
            
            assert client == mock_redis
            mock_from_url.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_redis_connection_success(self):
        """Тест успешного подключения к Redis."""
        with patch('redis_client.get_redis_client') as mock_get_client:
            mock_redis = AsyncMock()
            mock_redis.ping.return_value = b"PONG"
            mock_redis.close = AsyncMock()
            mock_get_client.return_value = mock_redis
            
            result = await test_redis_connection()
            
            assert result is True
            mock_redis.ping.assert_called_once()
            mock_redis.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_redis_connection_failure(self):
        """Тест неудачного подключения к Redis."""
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
    
    @pytest.mark.asyncio
    async def test_subscribe_to_transcripts(self):
        """Тест подписки на транскрипты."""
        callback_called = False
        received_text = None
        
        async def mock_callback(text):
            nonlocal callback_called, received_text
            callback_called = True
            received_text = text
        
        mock_message = {
            "type": "message",
            "data": b"Test transcript"
        }
        
        with patch('redis_client.get_redis_client') as mock_get_client:
            mock_redis = AsyncMock()
            mock_pubsub = AsyncMock()
            mock_redis.pubsub.return_value = mock_pubsub
            mock_pubsub.subscribe = AsyncMock()
            mock_pubsub.unsubscribe = AsyncMock()
            mock_pubsub.close = AsyncMock()
            mock_pubsub.listen.return_value = [mock_message]
            mock_get_client.return_value = mock_redis
            
            # Запускаем подписку с таймаутом
            try:
                await asyncio.wait_for(
                    subscribe_to_transcripts(mock_callback),
                    timeout=0.1
                )
            except asyncio.TimeoutError:
                pass
            
            mock_pubsub.subscribe.assert_called_once_with(TRANSCRIPTS_CHANNEL)
            assert callback_called
            assert received_text == "Test transcript"


class TestWebSocketHandlers:
    """Тесты для WebSocket обработчиков."""
    
    @pytest.mark.asyncio
    async def test_websocket_connect_disconnect(self):
        """Тест подключения и отключения WebSocket."""
        from ws import websocket_endpoint
        
        # Мокаем WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_bytes = AsyncMock(side_effect=Exception("Test disconnect"))
        mock_websocket.close = AsyncMock()
        
        # Мокаем Redis
        with patch('ws.get_redis_client') as mock_get_redis:
            mock_redis = AsyncMock()
            mock_redis.publish = AsyncMock()
            mock_redis.close = AsyncMock()
            mock_get_redis.return_value = mock_redis
            
            # Вызываем эндпоинт
            try:
                await websocket_endpoint(mock_websocket)
            except Exception:
                pass
            
            # Проверяем, что методы были вызваны
            mock_websocket.accept.assert_called_once()
            mock_websocket.close.assert_called_once()
            mock_redis.close.assert_called_once()


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