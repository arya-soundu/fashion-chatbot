// Wait until the entire HTML document is loaded and ready.
document.addEventListener("DOMContentLoaded", () => {
    // Get references to the essential HTML elements
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatWindow = document.getElementById('chat-window');

    /**
     * Handles the main logic of sending a message and receiving a response.
     */
    const sendMessage = async () => {
        // Get the user's message and trim any whitespace
        const messageText = userInput.value.trim();

        // If the message is empty, do nothing
        if (messageText === '') return;

        // 1. Display the user's own message in the chat window
        appendMessage(messageText, 'user');
        // Clear the input field for the next message
        userInput.value = '';

        try {
            // 2. Send the message to the Flask server
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                // The user's message is sent in a JSON object
                body: JSON.stringify({ message: messageText })
            });
            const data = await response.json();
            
            // 3. Display the bot's final response
            appendBotResponse(data);

        } catch (error) {
            // If there's a network or server error, display a message
            console.error("Error fetching bot response:", error);
            appendBotResponse({ display_html: "<p>Sorry, I'm having trouble connecting. Please try again later.</p>" });
        }
    };

    /**
     * Creates and adds a simple text bubble for the user's message.
     * @param {string} text - The message text.
     * @param {string} sender - The sender ('user' or 'bot').
     */
    const appendMessage = (text, sender) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-bubble ${sender}`;
        // Using textContent is safer for user input to prevent HTML injection
        const p = document.createElement('p');
        p.textContent = text;
        messageDiv.appendChild(p);
        
        chatWindow.appendChild(messageDiv);
        // Automatically scroll to the latest message
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    /**
     * Creates and adds a bubble for the bot's response, which may contain complex HTML.
     * @param {object} data - The JSON data received from the server.
     */
    const appendBotResponse = (data) => {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-bubble bot';
        
        // Directly insert the pre-formatted HTML from the server
        botMessageDiv.innerHTML = data.display_html; 
        
        chatWindow.appendChild(botMessageDiv);
        // Automatically scroll to the latest message
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    // --- Event Listeners ---

    // Trigger sendMessage when the Send button is clicked
    sendBtn.addEventListener('click', sendMessage);

    // Trigger sendMessage when the Enter key is pressed in the input field
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});