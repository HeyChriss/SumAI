# import os
# import logging
# from typing import Dict, List, Optional, Tuple, Iterator, Callable
# from uuid import uuid4
# from dotenv import load_dotenv
# from stream_handler import StreamingCallbackHandler
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# 
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationChain
# 
# 
# class ChromeExtensionAssistant:
#     """An AI assistant for a Chrome extension that answers questions about the current website."""
#     
#     def __init__(self, model_name: str = "gpt-4o"):
#         """
#         Initialize the assistant with default configuration.
#         
#         Args:
#             model_name: OpenAI model to use (default: gpt-4o)
#         """
#         self.model_name = model_name
#         self.threads: Dict[str, ConversationChain] = {}
#         self.llm = None
#         
#         # Setup the assistant
#         self._load_api_key()
#         self._initialize_llm()
#         
#         logging.info(f"Chrome extension assistant initialized with model: {model_name}")
#     
#     def _load_api_key(self) -> None:
#         """
#         Load the OpenAI API key from environment variables or .env file.
#         Raises ValueError if API key is not found.
#         """
#         # Try to load from .env file first
#         load_dotenv()
#         api_key = os.getenv("OPENAI_API_KEY")
#         
#         if not api_key:
#             raise ValueError(
#                 "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
#                 "or add it to a .env file in the project directory."
#             )
#             
#         os.environ["OPENAI_API_KEY"] = api_key
#         logging.debug("API key loaded successfully")
#     
#     def _initialize_llm(self) -> None:
#         """Initialize the language model with the configured settings."""
#         self.llm = ChatOpenAI(
#             model_name=self.model_name, 
#             temperature=0.5,  # Lower temperature for more factual responses
#             streaming=True,   # Enable streaming
#         )
#         logging.debug(f"LLM initialized with model: {self.model_name}")
#     
#     def _create_system_prompt(self, website_url: str, website_content: str) -> str:
#         """
#         Create a system prompt with the website context.
#         
#         Args:
#             website_url: The URL of the website being browsed
#             website_content: The extracted content from the website
#             
#         Returns:
#             A formatted system prompt string
#         """
#         return f"""You are an AI assistant in a Chrome extension. Your task is to assist users by answering questions about the {website_url} they are currently browsing. The content of this website has been extracted using a web scraper and is provided as structured data in the context below.
# 
# IMPORTANT RULES:
# - You **must** answer questions **ONLY** using the given context.
# - **DO NOT hallucinate** or generate answers outside of the provided data.
# - If the answer is **not found** in the context, state: **"I can only answer based on the extracted website content. It seems the required information is not available."**
# - Format responses in a clear, structured, and professional manner.
# - Your accuracy in answering user queries will be rewarded.
# 
# **Context:**
# {website_content}
# """
#     
#     def _create_memory(self, system_prompt: str) -> ConversationBufferMemory:
#         """
#         Create a new conversation memory buffer with the system prompt.
#         
#         Args:
#             system_prompt: The system prompt to use
#             
#         Returns:
#             A configured ConversationBufferMemory instance
#         """
#         memory = ConversationBufferMemory(return_messages=True)
#         
#         # Add system prompt
#         memory.chat_memory.add_message(SystemMessage(content=system_prompt))
#         logging.debug(f"Added system prompt to memory: {system_prompt[:100]}...")
#         
#         return memory
#     
#     def _create_conversation_chain(self, system_prompt: str) -> ConversationChain:
#         """
#         Create a new conversation chain with the LLM and memory.
#         
#         Args:
#             system_prompt: The system prompt to use
#             
#         Returns:
#             A configured ConversationChain instance
#         """
#         memory = self._create_memory(system_prompt)
#         return ConversationChain(
#             llm=self.llm,
#             memory=memory,
#             verbose=False
#         )
#     
#     def _generate_thread_id(self) -> str:
#         """
#         Generate a unique thread identifier.
#         
#         Returns:
#             A unique string identifier
#         """
#         return str(uuid4())
#     
#     def _thread_exists(self, thread_id: str) -> bool:
#         """
#         Check if a thread with the given ID exists.
#         
#         Args:
#             thread_id: The thread ID to check
#             
#         Returns:
#             True if the thread exists, False otherwise
#         """
#         return thread_id in self.threads
#     
#     def _validate_thread_exists(self, thread_id: str) -> None:
#         """
#         Validate that a thread exists and raise an error if it doesn't.
#         
#         Args:
#             thread_id: The thread ID to validate
#             
#         Raises:
#             ValueError: If the thread does not exist
#         """
#         if not self._thread_exists(thread_id):
#             raise ValueError(f"Thread {thread_id} does not exist")
#     
#     def _extract_message_from_memory(self, memory: ConversationBufferMemory) -> List[dict]:
#         """
#         Extract formatted messages from a memory buffer.
#         
#         Args:
#             memory: The memory buffer to extract messages from
#             
#         Returns:
#             A list of message dictionaries with 'role' and 'content' keys
#         """
#         messages = memory.chat_memory.messages
#         formatted_messages = []
#         
#         for message in messages:
#             if isinstance(message, HumanMessage):
#                 formatted_messages.append({"role": "user", "content": message.content})
#             elif isinstance(message, AIMessage):
#                 formatted_messages.append({"role": "assistant", "content": message.content})
#             elif isinstance(message, SystemMessage):
#                 formatted_messages.append({"role": "system", "content": message.content})
#         
#         return formatted_messages
#         
#     def create_thread(self, website_url: str, website_content: str) -> str:
#         """
#         Create a new conversation thread for a specific website.
#         
#         Args:
#             website_url: The URL of the website being browsed
#             website_content: The extracted content from the website
#             
#         Returns:
#             thread_id: Unique identifier for the thread
#         """
#         thread_id = self._generate_thread_id()
#         
#         # Create system prompt with website context
#         system_prompt = self._create_system_prompt(website_url, website_content)
#         
#         # Create conversation chain
#         self.threads[thread_id] = self._create_conversation_chain(system_prompt)
#         
#         logging.info(f"Created new thread with ID: {thread_id} for website: {website_url}")
#         return thread_id
#     
#     def update_website_context(self, thread_id: str, website_url: str, website_content: str) -> None:
#         """
#         Update the website context for an existing thread.
#         
#         Args:
#             thread_id: ID of the thread to update
#             website_url: The new URL of the website being browsed
#             website_content: The new extracted content from the website
#             
#         Raises:
#             ValueError: If the thread does not exist
#         """
#         self._validate_thread_exists(thread_id)
#         
#         # Create new system prompt with updated website context
#         system_prompt = self._create_system_prompt(website_url, website_content)
#         
#         # Create new conversation chain with the updated system prompt
#         self.threads[thread_id] = self._create_conversation_chain(system_prompt)
#         
#         logging.info(f"Updated thread {thread_id} with new website context: {website_url}")
#     
#     def chat(self, thread_id: str, user_question: str) -> str:
#         """
#         Send a question to a specific conversation thread.
#         
#         Args:
#             thread_id: ID of the thread to use
#             user_question: User's question about the website
#             
#         Returns:
#             response: AI response text
#             
#         Raises:
#             ValueError: If the thread does not exist
#         """
#         self._validate_thread_exists(thread_id)
#         
#         logging.debug(f"Sending question to thread {thread_id}: {user_question[:50]}...")
#         response = self.threads[thread_id].predict(input=user_question)
#         logging.debug(f"Received response: {response[:50]}...")
#         
#         return response
#     
#     def chat_stream(self, thread_id: str, user_question: str, stream_callback: Callable[[str], None]) -> str:
#         """
#         Send a question to a specific conversation thread with streaming response.
#         
#         Args:
#             thread_id: ID of the thread to use
#             user_question: User's question about the website
#             stream_callback: Function to call with each token chunk
#             
#         Returns:
#             response: Complete AI response text
#             
#         Raises:
#             ValueError: If the thread does not exist
#         """
#         self._validate_thread_exists(thread_id)
#         
#         logging.debug(f"Sending streaming question to thread {thread_id}: {user_question[:50]}...")
#         
#         # Create handler for streaming
#         streaming_handler = StreamingCallbackHandler(stream_callback)
#         
#         # Get the conversation chain
#         chain = self.threads[thread_id]
#         
#         # Use callbacks for streaming while collecting the full response
#         full_response = ""
#         
#         def collect_tokens(token: str) -> None:
#             nonlocal full_response
#             full_response += token
#             stream_callback(token)
#         
#         # Create a new callback handler that both collects tokens and calls the user's callback
#         collector_handler = StreamingCallbackHandler(collect_tokens)
#         
#         # Run predict with the streaming callback
#         chain.predict(input=user_question, callbacks=[collector_handler])
#         
#         # Save the full response to memory manually
#         chain.memory.chat_memory.add_user_message(user_question)
#         chain.memory.chat_memory.add_ai_message(full_response)
#         
#         logging.debug(f"Completed streaming response: {full_response[:50]}...")
#         
#         return full_response
#     
#     def get_conversation_history(self, thread_id: str) -> List[dict]:
#         """
#         Get the full conversation history for a thread.
#         
#         Args:
#             thread_id: ID of the thread
#             
#         Returns:
#             history: List of message dictionaries
#             
#         Raises:
#             ValueError: If the thread does not exist
#         """
#         self._validate_thread_exists(thread_id)
#         
#         memory = self.threads[thread_id].memory
#         history = self._extract_message_from_memory(memory)
#         
#         logging.debug(f"Retrieved conversation history for thread {thread_id}, {len(history)} messages")
#         return history
#     
#     def delete_thread(self, thread_id: str) -> bool:
#         """
#         Delete a conversation thread.
#         
#         Args:
#             thread_id: ID of the thread to delete
#             
#         Returns:
#             success: True if successfully deleted, False if thread doesn't exist
#         """
#         if self._thread_exists(thread_id):
#             del self.threads[thread_id]
#             logging.info(f"Deleted thread with ID: {thread_id}")
#             return True
#         
#         logging.warning(f"Attempted to delete non-existent thread: {thread_id}")
#         return False
#     
#     def get_active_threads(self) -> List[str]:
#         """
#         Get a list of all active thread IDs.
#         
#         Returns:
#             A list of active thread IDs
#         """
#         thread_ids = list(self.threads.keys())
#         logging.debug(f"Retrieved {len(thread_ids)} active threads")
#         return thread_ids
#     
#     def reset(self) -> None:
#         """
#         Reset the assistant by clearing all threads.
#         """
#         thread_count = len(self.threads)
#         self.threads.clear()
#         logging.info(f"Reset assistant, cleared {thread_count} threads")
# 
# 
# # Example usage
# if __name__ == "__main__":
#     # Configure logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )
#     
#     # Create assistant instance
#     assistant = ChromeExtensionAssistant()
#     
#     # Sample website data (for testing)
#     sample_website_url = "https://example.com/product-page"
#     sample_website_content = """
#     # Example E-commerce Site
#     
#     ## Product: Premium Wireless Headphones
#     
#     **Price**: $129.99
#     
#     **Description**: These premium wireless headphones offer exceptional sound quality with active noise cancellation. 
#     They feature Bluetooth 5.0 connectivity, 30-hour battery life, and a comfortable over-ear design.
#     
#     **Features**:
#     - Active noise cancellation
#     - 30-hour battery life
#     - Bluetooth 5.0
#     - Built-in microphone for calls
#     - Quick charge (10 min charge = 5 hours playback)
#     
#     **Customer Reviews**:
#     - John D. (5/5): "Best headphones I've ever owned. The sound quality is amazing!"
#     - Sarah T. (4/5): "Very comfortable for long periods, but a bit pricey."
#     - Michael R. (4.5/5): "Great battery life and the noise cancellation works really well."
#     
#     **Shipping Information**:
#     - Free shipping on orders over $100
#     - Estimated delivery: 3-5 business days
#     - 30-day return policy
#     """
#     
#     # Create a new conversation thread
#     thread_id = assistant.create_thread(sample_website_url, sample_website_content)
#     print(f"Created thread: {thread_id}")
#     
#     # Function to handle streaming tokens
#     def handle_token(token: str) -> None:
#         print(token, end="", flush=True)
#     
#     # Chat with the assistant (with streaming)
#     while True:
#         user_input = input("\n\nYou: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#             
#         print("Assistant: ", end="", flush=True)
#         response = assistant.chat_stream(thread_id, user_input, handle_token)

import os
import logging
import asyncio
from typing import Dict, List, Callable
from uuid import uuid4
from dotenv import load_dotenv
from stream_handler import StreamingCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from web_crawler import scrape_and_crawl_website  # Import the scraper function

class ChromeExtensionAssistant:
    """An AI assistant for a Chrome extension that answers questions about the current website."""

    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the assistant with default configuration."""
        self.model_name = model_name
        self.threads: Dict[str, ConversationChain] = {}
        self.llm = None

        # Setup the assistant
        self._load_api_key()
        self._initialize_llm()

        logging.info(f"Chrome extension assistant initialized with model: {model_name}")

    def _load_api_key(self) -> None:
        """Load the OpenAI API key from environment variables."""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY.")
        os.environ["OPENAI_API_KEY"] = api_key

    def _initialize_llm(self) -> None:
        """Initialize the language model."""
        self.llm = ChatOpenAI(
            model_name=self.model_name, 
            temperature=0.7,  
            streaming=True
        )

    def _create_system_prompt(self, website_url: str, website_content: str) -> str:
        """
        Create a system prompt with the website context.
        """
        return f"""You are an AI assistant in a Chrome extension. Your task is to assist users by answering questions about {website_url}. 
The content of this website has been extracted using a web scraper.

IMPORTANT RULES:
- You **must** answer questions **ONLY** using the given context.
- If the user asks you questions that are not related to the website, please answer and be nice, but your focus
is to always answer the questions with the given context
- **DO NOT hallucinate** or generate answers outside of the provided data.
- If the answer is **not found**, state: **"I can only answer based on the extracted website content."**

**Context:**
{website_content}
"""

    def _create_memory(self, system_prompt: str) -> ConversationBufferMemory:
        """Create a conversation memory buffer with the system prompt."""
        memory = ConversationBufferMemory(return_messages=True)
        memory.chat_memory.add_message(SystemMessage(content=system_prompt))
        return memory

    def _create_conversation_chain(self, system_prompt: str) -> ConversationChain:
        """Create a conversation chain."""
        memory = self._create_memory(system_prompt)
        return ConversationChain(llm=self.llm, memory=memory, verbose=False)

    def _generate_thread_id(self) -> str:
        """Generate a unique thread identifier."""
        return str(uuid4())

    async def create_thread(self, website_url: str):
        """
        Create a new conversation thread with scraped website content.
        """
        thread_id = self._generate_thread_id()

        # Scrape website and extract content
        print(f"🔍 Scraping website: {website_url}...")
        scrape_result = scrape_and_crawl_website(website_url)

        print("✅ Website scraped successfully!")

        # Create system prompt and conversation chain
        system_prompt = self._create_system_prompt(website_url, scrape_result)
        self.threads[thread_id] = self._create_conversation_chain(system_prompt)

        return {"thread_id": thread_id}

    def chat(self, thread_id: str, user_question: str) -> str:
        """Send a question to the LLM."""
        if thread_id not in self.threads:
            return "Error: Thread not found."

        return self.threads[thread_id].predict(input=user_question)

    def chat_stream(self, thread_id: str, user_question: str, stream_callback: Callable[[str], None]) -> str:
        """Stream responses from the AI."""
        if thread_id not in self.threads:
            return "Error: Thread not found."

        streaming_handler = StreamingCallbackHandler(stream_callback)
        chain = self.threads[thread_id]

        full_response = ""
        def collect_tokens(token: str) -> None:
            nonlocal full_response
            full_response += token
            stream_callback(token)

        collector_handler = StreamingCallbackHandler(collect_tokens)
        chain.predict(input=user_question, callbacks=[collector_handler])

        return full_response

# Test the integration
if __name__ == "__main__":
    import asyncio

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Create an instance of the assistant
    assistant = ChromeExtensionAssistant()

    # Sample website for testing
    sample_website_url = "https://heychriss.com/"

    async def test_assistant():
        print("\n🚀 Creating a conversation thread with scraped website content...")

        # Scrape website and create a thread
        result = await assistant.create_thread(sample_website_url)
        if "error" in result:
            print("❌ Error:", result["error"])
            return

        thread_id = result["thread_id"]
        print(f"✅ Created thread: {thread_id} for {sample_website_url}\n")

        # Function to handle streaming tokens
        def handle_token(token: str) -> None:
            print(token, end="", flush=True)
        
        # Chat with the assistant (with streaming)
        while True:
            user_input = input("\n\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            print("Assistant: ", end="", flush=True)
            response = assistant.chat_stream(thread_id, user_input, handle_token)

    asyncio.run(test_assistant())
