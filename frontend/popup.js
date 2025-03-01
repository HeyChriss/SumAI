const userInput = document.getElementById("prompt");
const chatBox = document.getElementById("chatBox");
const submitBtn = document.getElementById("submitBtn");

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

submitBtn.innerHTML = micSvg;
const sendButton = () => {
  const sendButton = document.querySelector("button");
  const textInput = document.querySelector("inputField");

  if (textInput.value == null) {
    return;
  } else {
    getRequestAI();
  }
};

const getRequestAI = async (input) => {
  try {
    const response = await fetch("apiURL", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.log("Error fetching from api");
      return -1;
    }

    data = await response.json();
  } catch (error) {
    console.error(error);
  }
};

// this is to activate the input as soon as the user clicks on the extension icon
document.addEventListener("DOMContentLoaded", () => {
  userInput.focus();
});
userInput.addEventListener("input", () => {
  submitBtn.innerHTML = userInput.value.trim() ? sendSvg : micSvg;
});

// Listen for both Enter key and button click
userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleUserInput();
  }
});

submitBtn.addEventListener("click", () => {
  if (userInput.value.trim()) {
    handleUserInput();
  } else {
    startSpeechRecognition();
  }
});

async function handleUserInput() {
  const userText = userInput.value.trim();

  if (userText) {
    const userPrompt = document.createElement("div");
    userPrompt.className = "flex justify-end";
    userPrompt.innerHTML = `<p class="inline-flex max-w-sm bg-blue-500 text-white p-3 rounded-lg rounded-br-none self-end chat-bubble drop-shadow-lg">${userText}</p>`;
    chatBox.appendChild(userPrompt);
    userInput.value = "";
    submitBtn.innerHTML = micSvg;

    await sleep(1000);
    Reply("Sorry! Sum it up AI is under construction");
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function Reply(message) {
  const AIReply = document.createElement("div");
  AIReply.className = "flex justify-start";
  AIReply.innerHTML = `<p class="inline-flex max-w-sm bg-gray-50 p-3 rounded-lg rounded-bl-none self-start chat-bubble drop-shadow-lg">${message}</p>`;
  chatBox.appendChild(AIReply);

  setTimeout(() => {
    AIReply.classList.add("animate-fadeIn");
  }, 100);
}

let recognition;
const webkitSpeechRecognition =
  window.webkitSpeechRecognition || window.SpeechRecognition;

//speech Recognition from https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
  if ("webkitSpeechRecognition" in window) {
  recognition = new webkitSpeechRecognition();
  recognition.continuous = false; // Stop after one sentence
  recognition.interimResults = true; // type as you're talking
  recognition.lang = "en-US"; // Set language

  recognition.onstart = () => {
    console.log("Speech recognition started");
    submitBtn.innerHTML = micSvg;
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    submitBtn.innerHTML = sendSvg;
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    submitBtn.innerHTML = micSvg; // Reset to mic icon
  };

  recognition.onend = () => {
    console.log("Speech recognition ended");
    submitBtn.innerHTML = micSvg;
  };
} else {
  console.warn("Speech recognition not supported in this browser.");
}

async function startSpeechRecognition() {
  try {
    // Request microphone access
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    if (recognition) {
      userInput.placeholder = "Speak...";
      recognition.start();
    }
  } catch (error) {
    console.error("Microphone access denied:", error);
    alert(
      "Microphone access is required for speech recognition. Please allow access in your browser settings."
    );
  }
}