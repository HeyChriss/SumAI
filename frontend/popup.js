// Global variables to store thread information
let currentThreadId = null;
let currentWebsiteUrl = null;
let recognition;

// Initialize when the popup opens
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Get current tab URL
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        currentWebsiteUrl = tabs[0].url;
        
        // Create a thread with the current website
        await createOrUpdateThread(currentWebsiteUrl);
        
        // Initialization complete message
        Reply("How can I help you today?");
        
        // Set up listeners for URL changes
        setupTabListeners();
        
        // Ensure scrolling works properly
        setupScrolling();

        // Initialize speech recognition
        setupSpeechRecognition();
        
        // Focus on input field when popup opens
        document.getElementById('prompt').focus();

    } catch (error) {
        console.error("Initialization error:", error);
        Reply("Sorry, I couldn't connect to the website. Please try again later.");
    }
});

// Set up listeners for tab/URL changes
function setupTabListeners() {
    // Listen for tab updates (URL changes)
    chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
        if (changeInfo.url) {
            // URL has changed
            currentWebsiteUrl = changeInfo.url;
            Reply(`I notice you've navigated to a new page. Let me analyze it...`);
            
            try {
                await createOrUpdateThread(currentWebsiteUrl);
                Reply("I'm ready to answer questions about this new page.");
            } catch (error) {
                console.error("Error updating thread for new URL:", error);
                Reply("I had trouble analyzing this new page. Please try refreshing.");
            }
        }
    });
}

// Set up scrolling for the chat box
function setupScrolling() {
    const chatBox = document.getElementById('chatBox');
    
    // Add custom styling for scroll behavior
    chatBox.style.overflowY = 'auto';
    chatBox.style.maxHeight = 'calc(100% - 80px)'; // Adjust based on your UI
    
    // Ensure we scroll to the bottom on new messages
    const observer = new MutationObserver(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    });
    
    observer.observe(chatBox, { childList: true });
}

// SVG icons for mic and send button
const sendSvg = `<svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="size-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
        />
      </svg>`;
      
const micSvg = `<svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="size-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"
        />
      </svg>`;

// Set up speech recognition functionality
function setupSpeechRecognition() {
    const submitBtn = document.getElementById('submitBtn');
    const userInput = document.getElementById('prompt');
    
    // Set initial button to mic if input is empty
    updateButtonIcon();
    
    // Toggle button based on input
    userInput.addEventListener("input", updateButtonIcon);
    
    // Initialize speech recognition if available
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false; // Stop after one sentence
        recognition.interimResults = true; // Get results as you're talking
        recognition.lang = 'en-US'; // Set language

        recognition.onstart = () => {
            console.log('Speech recognition started');
            userInput.placeholder = 'Speak...';
            userInput.disabled = true; // Disable input while listening
            submitBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 text-red-500">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>`;
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            updateButtonIcon();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            userInput.disabled = false;
            userInput.placeholder = 'Summarize this webpage for me...';
            updateButtonIcon();
        };

        recognition.onend = () => {
            console.log('Speech recognition ended');
            userInput.disabled = false;
            userInput.placeholder = 'Summarize this webpage for me...';
            updateButtonIcon();
        };
        
        // Make the button stop recognition if clicked during active listening
        submitBtn.addEventListener("click", () => {
            if (userInput.disabled) {
                // If recognition is active, stop it
                recognition.stop();
                return;
            }
            
            if (userInput.value.trim()) {
                handleUserInput();
            } else {
                startSpeechRecognition();
            }
        });
    } else {
        console.warn('Speech recognition not supported in this browser.');
        submitBtn.addEventListener("click", handleUserInput);
    }
}

// Helper function to update button icon based on input state
function updateButtonIcon() {
    const userInput = document.getElementById('prompt');
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.innerHTML = userInput.value.trim() ? sendSvg : micSvg;
}

// Function to start speech recognition with standard web API
async function startSpeechRecognition() {
    if (!recognition) {
        Reply("Speech recognition is not supported in this browser.");
        return;
    }
    
    try {
        // Standard web API for requesting microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("Microphone access granted");
        
        // Start recognition
        recognition.start();
    } catch (error) {
        console.error('Microphone access error:', error);
        
        // Provide specific error messages
        if (error.name === "NotAllowedError") {
            Reply("Microphone access was denied. Please allow access in your browser settings.");
        } else if (error.name === "NotFoundError") {
            Reply("No microphone found. Please check your device.");
        } else if (error.name === "NotReadableError") {
            Reply("The microphone is being used by another application.");
        } else {
            Reply(`Microphone error: ${error.name}. Please try again.`);
        }
    }
}

// Create or update thread with current website
async function createOrUpdateThread(websiteUrl) {
    try {
        // Replace with your actual backend API URL
        const backendUrl = "http://127.0.0.1:5000/create_thread";
        
        const response = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ website_url: websiteUrl })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Store the thread ID
        currentThreadId = data.thread_id;
        console.log("Thread created/updated:", currentThreadId);
        return data;
    } catch (error) {
        console.error("Error creating/updating thread:", error);
        throw error;
    }
}

// Send message to AI and get streaming response
async function sendMessageToAI(userMessage) {
    try {
        if (!currentThreadId) {
            throw new Error("No active thread. Please reload the extension.");
        }
        
        // Replace with your actual backend API URL - using stream endpoint
        const backendUrl = "http://127.0.0.1:5000/chat_stream";
        
        const response = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                thread_id: currentThreadId,
                message: userMessage
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return response; // Return the response for streaming
    } catch (error) {
        console.error("Error sending message to AI:", error);
        throw error;
    }
}

// Add event listener for Enter key press
document.getElementById('prompt').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent default form submission behavior
        handleUserInput();
    }
});

// Process user input and get AI response with streaming
async function handleUserInput() {
    const userInput = document.getElementById('prompt');
    const chatBox = document.getElementById('chatBox');
    const userText = userInput.value.trim();

    if (userText) {
        // Display user message
        const userPrompt = document.createElement('div');
        userPrompt.className = 'flex justify-end';
        userPrompt.innerHTML = `<p class="inline-flex max-w-sm bg-blue-500 text-white p-3 rounded-lg rounded-br-none self-end chat-bubble drop-shadow-lg">${userText}</p>`;
        chatBox.appendChild(userPrompt);
        
        // Clear input field and update button icon
        userInput.value = '';
        updateButtonIcon();
        
        // Create AI response container
        const AIReply = document.createElement('div');
        AIReply.className = 'flex justify-start';
        AIReply.innerHTML = `<p id="currentReply" class="inline-flex max-w-sm bg-gray-50 p-3 rounded-lg rounded-bl-none self-start">...</p>`;
        chatBox.appendChild(AIReply);
        
        // Get response element for updating
        const replyElement = AIReply.querySelector('#currentReply');
        
        try {
            // Get streaming response from AI
            const response = await sendMessageToAI(userText);
            
            // Set up streaming with ReadableStream
            if (response.body) {
                // Modern streaming with ReadableStream
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let responseText = '';
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    responseText += chunk;
                    replyElement.textContent = responseText;
                    
                    // Scroll to bottom with each new chunk
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            } else {
                // Fallback to non-streaming
                const data = await response.json();
                replyElement.textContent = data.response || "No response received";
            }
        } catch (error) {
            replyElement.textContent = "Sorry, I encountered an error. Please try again.";
        }
        
        // Generate a new ID for the reply element (remove the temporary ID)
        replyElement.removeAttribute('id');
        
        // Scroll to bottom of chat
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Focus back on input for next message
        userInput.focus();
    }
}

// Display AI message (for non-streaming messages)
function Reply(message) {
    const chatBox = document.getElementById('chatBox');
    const AIReply = document.createElement('div');
    AIReply.className = 'flex justify-start';
    AIReply.innerHTML = `<p class="inline-flex max-w-sm bg-gray-50 p-3 rounded-lg rounded-bl-none self-start chat-bubble drop-shadow-lg">${message}</p>`;
    chatBox.appendChild(AIReply);
    
    // Auto-scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Add fade-in animation
    setTimeout(function() {
        AIReply.classList.add('animate-fadeIn');
    }, 100);
}

// Helper function for sleep/delay
function Sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}