\
from langchain.memory import ConversationBufferMemory
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
import logging
import json
import os
from langchain.schema.messages import HumanMessage, AIMessage

import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

logger = logging.getLogger(__name__)

# Define the path for the conversation store file in the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
CONVERSATION_STORE_FILE = os.path.join(PROJECT_ROOT, "conversation_store.json")

# Initialize conversation memory
conversation_memories: Dict[str, ConversationBufferMemory] = {}

def save_conversations():
    """Saves the current state of conversation_memories to a JSON file."""
    serializable_memories = {}
    for conv_id, memory in conversation_memories.items():
        serializable_memories[conv_id] = [
            {"type": getattr(msg, 'type', type(msg).__name__.replace('Message', '').lower()), "content": msg.content}
            for msg in getattr(memory.chat_memory, 'messages', [])
        ]
    try:
        with open(CONVERSATION_STORE_FILE, 'w') as f:
            json.dump(serializable_memories, f, indent=4)
        logger.info(f"Conversations saved to {CONVERSATION_STORE_FILE}")
    except IOError as e:
        logger.error(f"Error saving conversations to {CONVERSATION_STORE_FILE}: {e}")

def load_conversations():
    """Loads conversations from the JSON file into conversation_memories."""
    if not os.path.exists(CONVERSATION_STORE_FILE):
        logger.info(f"Conversation store file not found at {CONVERSATION_STORE_FILE}. Starting with empty memories.")
        return

    try:
        with open(CONVERSATION_STORE_FILE, 'r') as f:
            loaded_data = json.load(f)
        
        for conv_id, messages_data in loaded_data.items():
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                output_key="answer",
                return_messages=True
            )
            reconstructed_messages = []
            for msg_data in messages_data:
                msg_type = msg_data.get('type')
                if msg_type == 'human':
                    reconstructed_messages.append(HumanMessage(content=msg_data['content']))
                elif msg_type == 'ai':
                    reconstructed_messages.append(AIMessage(content=msg_data['content']))
                else:
                    # Fallback for unknown types
                    reconstructed_messages.append(HumanMessage(content=msg_data['content']))
            memory.chat_memory.messages = reconstructed_messages
            conversation_memories[conv_id] = memory
        logger.info(f"Conversations loaded from {CONVERSATION_STORE_FILE}")
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading conversations from {CONVERSATION_STORE_FILE}: {e}. Starting with empty memories.")
        conversation_memories.clear()


def get_or_create_memory(conversation_id: Optional[str]) -> Tuple[ConversationBufferMemory, str]:
    """
    Retrieves an existing conversation memory or creates a new one.
    Saves conversations after creation or retrieval of a new one.
    """
    created_new = False
    if conversation_id and conversation_id in conversation_memories:
        memory = conversation_memories[conversation_id]
        logger.info(f"Using existing conversation memory for {conversation_id}")
    else:
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True
        )
        if not conversation_id:
            conversation_id = str(uuid4())
            logger.info(f"Generated new conversation_id: {conversation_id}")
        conversation_memories[conversation_id] = memory
        logger.info(f"Created new conversation memory for {conversation_id}")
        created_new = True
    
    if created_new: # Save only if a new memory was added or a new ID was generated
        save_conversations()
        
    return memory, conversation_id

def get_memory(conversation_id: str) -> Optional[ConversationBufferMemory]:
    """
    Retrieves an existing conversation memory.

    Args:
        conversation_id: The ID of the conversation.

    Returns:
        The ConversationBufferMemory if found, else None.
    """
    return conversation_memories.get(conversation_id)

def list_conversation_ids() -> List[str]:
    """
    Lists all active conversation IDs.

    Returns:
        A list of conversation IDs.
    """
    return list(conversation_memories.keys())

# Load conversations when the module is initialized
load_conversations()
