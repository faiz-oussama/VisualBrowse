const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

let currentLanguage = 'en-US';
recognition.lang = currentLanguage;
recognition.interimResults = false; 
recognition.continuous = false;

const startButton = document.getElementById('start');

// Add language switching functionality
document.querySelectorAll('.ht-setting-list li').forEach(li => {
    li.addEventListener('click', (e) => {
        e.preventDefault();
        currentLanguage = li.dataset.lang;
        recognition.lang = currentLanguage;
        document.getElementById('currentLang').textContent = 
            currentLanguage === 'en-US' ? 'English' : 'العربية';
        
        // Update active state
        document.querySelector('.ht-setting-list li.active').classList.remove('active');
        li.classList.add('active');
    });
});

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