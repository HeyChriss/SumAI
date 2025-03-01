from langchain_core.callbacks.base import BaseCallbackHandler
from typing import Dict, List, Optional, Tuple, Iterator, Callable

class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses."""
    
    def __init__(self, stream_callback: Callable[[str], None]):
        """
        Initialize the streaming callback handler.
        
        Args:
            stream_callback: Function to call with each token chunk
        """
        self.stream_callback = stream_callback
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Process a new token from the LLM.
        
        Args:
            token: The token string
            **kwargs: Additional arguments
        """
        self.stream_callback(token)