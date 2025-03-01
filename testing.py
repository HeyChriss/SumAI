"""
Example usage of the Chrome Extension Assistant with dynamic website navigation.
"""

import logging
from open_ai_modules import ChromeExtensionAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize the assistant
assistant = ChromeExtensionAssistant()

# Create a single thread for the entire user session
# Initial website is a product page
initial_website = {
    "url": "https://example.com/product-page",
    "content": """
    # Premium Wireless Headphones
    
    **Price**: $129.99
    
    **Description**: These premium wireless headphones offer exceptional sound quality with active noise cancellation. 
    They feature Bluetooth 5.0 connectivity, 30-hour battery life, and a comfortable over-ear design.
    
    **Features**:
    - Active noise cancellation
    - 30-hour battery life
    - Bluetooth 5.0
    - Built-in microphone for calls
    - Quick charge (10 min charge = 5 hours playback)
    """
}

# Create the conversation thread
thread_id = assistant.create_thread(initial_website["url"], initial_website["content"])
print(f"Created thread for: {initial_website['url']}")

# Define token handler for streaming
def handle_token(token: str) -> None:
    print(token, end="", flush=True)

# Simulate a conversation
print("\nUser asks about the initial product page:")
question1 = "What is the price of these headphones?"
print(f"\nYou: {question1}")
print("Assistant: ", end="")
assistant.chat_stream(thread_id, question1, handle_token)

print("\n\nUser asks a follow-up question:")
question2 = "What connectivity features do they have?"
print(f"\nYou: {question2}")
print("Assistant: ", end="")
assistant.chat_stream(thread_id, question2, handle_token)

# Simulate user navigating to a new page
new_website = {
    "url": "https://example.com/about",
    "content": """
    # About Example.com
    
    Example.com was founded in 2010 by Jane Smith with a mission to provide high-quality audio equipment at reasonable prices.
    
    Our headquarters is located in Seattle, Washington, and we have distribution centers in:
    - New York
    - Chicago
    - Los Angeles
    
    We pride ourselves on excellent customer service and a 30-day satisfaction guarantee on all products.
    """
}

print("\n\n[User navigates to a new page]")
print(f"Updating context to: {new_website['url']}")

# Update the context with the new website
assistant.update_website_context(thread_id, new_website["url"], new_website["content"])

# Continue the conversation with the new context
print("\nUser asks about the new page:")
question3 = "When was this company founded?"
print(f"\nYou: {question3}")
print("Assistant: ", end="")
assistant.chat_stream(thread_id, question3, handle_token)

print("\n\nUser asks about something not in the context:")
question4 = "What are your best-selling products?"
print(f"\nYou: {question4}")
print("Assistant: ", end="")
assistant.chat_stream(thread_id, question4, handle_token)

# Simulate going back to the product page
print("\n\n[User navigates back to the product page]")
print(f"Updating context to: {initial_website['url']}")

# Update context back to the initial website
assistant.update_website_context(thread_id, initial_website["url"], initial_website["content"])

# Ask about the original page again
print("\nUser asks about the original page again:")
question5 = "What is the battery life of these headphones?"
print(f"\nYou: {question5}")
print("Assistant: ", end="")
assistant.chat_stream(thread_id, question5, handle_token)

print("\n\nEnd of demonstration")