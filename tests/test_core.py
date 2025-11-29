import pytest
import os
from core.memory.manager import MemoryManager

@pytest.mark.asyncio
async def test_memory_manager():
    db_path = "test_history.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    manager = MemoryManager(db_path=db_path)
    await manager.init_db()
    
    # Create conversation
    conv_id = await manager.create_conversation("Test Chat")
    assert conv_id is not None
    
    # Add messages
    await manager.add_message(conv_id, "user", "Hello")
    await manager.add_message(conv_id, "assistant", "Hi there")
    
    # Get messages
    msgs = await manager.get_messages(conv_id)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Hello"
    assert msgs[1]["content"] == "Hi there"
    
    # List conversations
    convs = await manager.list_conversations()
    assert len(convs) == 1
    assert convs[0]["title"] == "Test Chat"
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
