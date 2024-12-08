const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = 'en-US';
recognition.interimResults = false; 
recognition.continuous = false;

const startButton = document.getElementById('start');

startButton.addEventListener('click', () => {
    recognition.start();
});

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    // Create a form dynamically
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = '/search';
    
    // Create input for transcript
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'query';
    input.value = transcript;
    
    // Add input to form
    form.appendChild(input);
    document.body.appendChild(form);
    
    // Submit form automatically
    form.submit();
};