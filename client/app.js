function getBathValue() {
    var uiBathrooms = document.getElementsByName("uiBathrooms");
    for(var i in uiBathrooms) {
      if(uiBathrooms[i].checked) {
          return parseInt(i)+1;
      }
    }
    return -1; // Invalid Value
  }
  
  function getBHKValue() {
    var uiBHK = document.getElementsByName("uiBHK");
    for(var i in uiBHK) {
      if(uiBHK[i].checked) {
          return parseInt(i)+1;
      }
    }
    return -1; // Invalid Value
  }
  
  function onClickedEstimatePrice() {
    console.log("Estimate price button clicked");
    var sqft = document.getElementById("uiSqft");
    var bhk = getBHKValue();
    var bathrooms = getBathValue();
    var location = document.getElementById("uiLocations");
    var estPrice = document.getElementById("uiEstimatedPrice");
  
    var url = "http://127.0.0.1:5000/predict_home_price"; 
  
    $.post(url, {
        total_sqft: parseFloat(sqft.value),
        bhk: bhk,
        bath: bathrooms,
        location: location.value
    },function(data, status) {
        console.log(data.estimated_price);
        estPrice.innerHTML = "<h2>" + data.estimated_price.toString() + " Lakh</h2>";
        console.log(status);
    });
  }
  
  function onPageLoad() {
    console.log( "document loaded" );
    var url = "http://127.0.0.1:5000/get_location_names"; 
    $.get(url,function(data, status) {
        console.log("got response for get_location_names request");
        if(data) {
            var locations = data.locations;
            var uiLocations = document.getElementById("uiLocations");
            $('#uiLocations').empty();
            for(var i in locations) {
                var opt = new Option(locations[i]);
                $('#uiLocations').append(opt);
            }
        }
    });
  }
  
  window.onload = onPageLoad;
  function addMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `p-4 rounded-xl ${isUser ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white ml-12' : 'bg-gray-50 mr-12'}`;
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Send message function
  async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
  
    // Add user message to chat
    addMessage(message, true);
    messageInput.value = '';
  
    try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
  
        const data = await response.json();
        
        if (data.success) {
            // Add bot response to chat
            addMessage(data.response);
        } else {
            addMessage('Sorry, I encountered an error: ' + data.error);
        }
    } catch (error) {
        addMessage('Sorry, I encountered an error: ' + error.message);
    }
  }
  
  // Handle Enter key in message input
  document.getElementById('messageInput')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
  });
  
  // Add loading state handling
  function setLoadingState(loading) {
    const button = document.querySelector('#chatInterface button');
    const input = document.getElementById('messageInput');
    
    button.disabled = loading;
    input.disabled = loading;
    button.innerHTML = loading ? `
        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    ` : 'Send';
  }
  // Chatbot functionality
document.addEventListener('DOMContentLoaded', () => {
  const chatbotIcon = document.getElementById('chatbot-icon');
  const chatPanel = document.getElementById('chat-panel');
  const closeChat = document.getElementById('close-chat');
  const sendMessageBtn = document.getElementById('send-message');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');

  // Show chat panel when icon is clicked
  chatbotIcon.addEventListener('click', () => {
      chatPanel.style.display = 'flex';
  });

  // Close chat panel
  closeChat.addEventListener('click', () => {
      chatPanel.style.display = 'none';
  });

  // Function to add messages to chat
  function addMessage(message, isUser = false) {
      const messageDiv = document.createElement('div');
      messageDiv.style.cssText = `
          background-color: ${isUser ? '#7c3aed' : '#f0f0f0'};
          color: ${isUser ? 'white' : 'black'};
          padding: 10px;
          border-radius: 10px;
          margin-bottom: 10px;
          max-width: 80%;
          align-self: ${isUser ? 'flex-end' : 'flex-start'};
      `;
      messageDiv.textContent = message;
      chatMessages.appendChild(messageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Send message functionality
  function sendMessage() {
      const message = chatInput.value.trim();
      if (!message) return;

      // Add user message
      addMessage(message, true);
      chatInput.value = '';

      // Send message to backend
      try {
          fetch('http://127.0.0.1:5000/chat', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({ message: message })
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  addMessage(data.response);
              } else {
                  addMessage('Sorry, I encountered an error processing your request.');
              }
          })
          .catch(error => {
              console.error('Chat error:', error);
              addMessage('Sorry, there was a problem connecting to the chat service.');
          });
      } catch (error) {
          console.error('Chat error:', error);
          addMessage('Sorry, there was a problem sending your message.');
      }
  }

  // Event listeners for sending messages
  sendMessageBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
  });
});