document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatDisplay = document.getElementById('chat-display');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // 1. Immediately show user message
        appendMessage('user', text);
        userInput.value = '';

        try {
            // 2. Fetch from your Flask API
            const response = await fetch('/api/kit/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ style: text })
            });
            const data = await response.json();

            // 3. Show AI response
            setTimeout(() => {
                appendMessage('ai', `Got it! I've put together a ${data.kit_name} within your budget.`);
            }, 600); // Slight delay for a more natural feel

        } catch (err) {
            appendMessage('ai', "Sorry, I'm having trouble connecting right now.");
        }
    });

    function appendMessage(sender, text) {
        const wrapper = document.createElement('div');
        // 'chat-bubble-anim' triggers the slow pop-up
        wrapper.className = `d-flex mb-4 chat-bubble-anim ${sender === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
        
        const bubble = document.createElement('div');
        bubble.className = `p-3 shadow-sm ${sender === 'user' ? 'user-bubble' : 'ai-bubble'}`;
        bubble.style.maxWidth = '75%';
        bubble.innerText = text;

        wrapper.appendChild(bubble);
        chatDisplay.appendChild(wrapper);
        
        // Smooth scroll to bottom
        chatDisplay.scrollTo({ top: chatDisplay.scrollHeight, behavior: 'smooth' });
    }
    function appendKitCard(kitData) {
    const chatDisplay = document.getElementById('chat-display');

    // Filter items into categories based on the 'type' field from our AI/Mock data
    const essentials = kitData.items.filter(item => item.type === 'essential');
    const extras = kitData.items.filter(item => item.type === 'extra');

    const cardHtml = `
        <div class="card border-0 shadow-sm mb-4 chat-bubble-anim ai-bubble-container" style="max-width: 90%;">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0">${kitData.kit_name}</h5>
                    <span class="badge bg-dark rounded-pill px-3">$${kitData.total_price}</span>
                </div>
                <p class="text-muted small mb-4">${kitData.description || "Your custom curated look is ready."}</p>

                <h6 class="text-uppercase text-primary fw-bold small mb-3 ls-1">Essentials</h6>
                <div class="row g-3 mb-4">
                    ${essentials.map(item => renderItemCard(item)).join('')}
                </div>

                ${extras.length > 0 ? `
                    <h6 class="text-uppercase text-muted fw-bold small mb-3 ls-1">Extras</h6>
                    <div class="row g-3">
                        ${extras.map(item => renderItemCard(item)).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    const wrapper = document.createElement('div');
    wrapper.className = 'd-flex mb-3 justify-content-start';
    wrapper.innerHTML = cardHtml;
    chatDisplay.appendChild(wrapper);
    
    chatDisplay.scrollTo({ top: chatDisplay.scrollHeight, behavior: 'smooth' });
}

// Helper to render individual item cards within the grid
function renderItemCard(item) {
    return `
        <div class="col-6 col-md-4">
            <div class="p-3 border rounded-4 bg-light h-100 d-flex flex-column">
                <span class="fw-bold small d-block mb-1">${item.name}</span>
                <span class="text-muted smallest mb-2">${item.color}</span>
                <div class="mt-auto d-flex justify-content-between align-items-center">
                    <span class="fw-bold">$${item.price}</span>
                    <a href="https://www.google.com/search?tbm=shop&q=${encodeURIComponent(item.name + ' ' + item.color)}" 
                       target="_blank" class="btn btn-link p-0 text-dark">
                        <i class="bi bi-arrow-up-right-circle fs-5"></i>
                    </a>
                </div>
            </div>
        </div>
    `;
}

async function loadChatHistory() {
    try {
        const response = await fetch('/api/kit/history');
        const kits = await response.json();
        const sidebar = document.querySelector('.list-group');
        
        if (kits.length > 0) {
            sidebar.innerHTML = kits.map(kit => `
                <button class="list-group-item list-group-item-action border-0 rounded-3 text-muted small mb-1">
                    <i class="bi bi-archive me-2"></i> ${kit.kit_name} - $${kit.total_price}
                </button>
            `).join('');
        }
    } catch (err) {
        console.error("Could not load database items:", err);
    }
}

// Function to render a detailed comparison for things like Tents
function appendComparisonCard(product) {
    const chatDisplay = document.getElementById('chat-display');
    const cardHtml = `
        <div class="card border-0 shadow-sm mb-4 chat-bubble-anim" style="max-width: 85%;">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="fw-bold mb-0">${product.name}</h5>
                    <span class="badge bg-success rounded-pill">$${product.price}</span>
                </div>
                <p class="small text-muted mb-3">${product.description}</p>
                
                <div class="row g-2 mb-3">
                    <div class="col-6">
                        <div class="p-2 rounded-3 bg-light border-start border-success border-4">
                            <p class="smallest fw-bold text-success mb-1">PROS</p>
                            <ul class="smallest p-0 list-unstyled mb-0">
                                ${product.pros.map(p => `<li>• ${p}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="p-2 rounded-3 bg-light border-start border-danger border-4">
                            <p class="smallest fw-bold text-danger mb-1">CONS</p>
                            <ul class="smallest p-0 list-unstyled mb-0">
                                ${product.cons.map(c => `<li>• ${c}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>

                <a href="${product.buy_url}" target="_blank" class="btn btn-dark w-100 btn-pill">
                    Buy Now <i class="bi bi-bag-check ms-2"></i>
                </a>
            </div>
        </div>`;
    const wrapper = document.createElement('div');
    wrapper.className = 'd-flex mb-3 justify-content-start';
    wrapper.innerHTML = cardHtml;
    chatDisplay.appendChild(wrapper);
    chatDisplay.scrollTo({ top: chatDisplay.scrollHeight, behavior: 'smooth' });
}

// Call this when the page loads
document.addEventListener('DOMContentLoaded', loadChatHistory);
});