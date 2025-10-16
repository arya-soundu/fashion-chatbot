document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const chatWindow = document.getElementById('chat-window');

    const sendMessage = async () => {
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        appendMessage(messageText, 'user');
        userInput.value = '';

        // Disable button to prevent double-sends
        sendBtn.disabled = true;
        userInput.disabled = true;
        sendBtn.textContent = '...';

        try {
            const response = await fetch('/get_response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageText })
            });
            const data = await response.json();
            appendBotResponse(data);
        } catch (error) {
            console.error("Error fetching bot response:", error);
            appendBotResponse({ display_html: "<p>Sorry, I'm having trouble connecting. Please try again later.</p>" });
        } finally {
            // Re-enable button after response
            sendBtn.disabled = false;
            userInput.disabled = false;
            sendBtn.textContent = 'Send';
        }
    };

    const appendMessage = (text, sender) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-bubble ${sender}`;
        const p = document.createElement('p');
        p.textContent = text;
        messageDiv.appendChild(p);
        
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const appendBotResponse = (data) => {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-bubble bot';
        botMessageDiv.innerHTML = data.display_html; 
        
        chatWindow.appendChild(botMessageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});