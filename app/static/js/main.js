// 1. Keep history global
let chatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const display = document.getElementById('chat-display');

    refreshSidebar();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault(); 
        
        const query = input.value.trim();
        if (!query) return;

        // 2. MANUAL RESET: If the user wants a new build, clear the old loop data
        if (query.toLowerCase().includes("build") || query.toLowerCase().includes("find") || query.toLowerCase().includes("kit")) {
            chatHistory = []; 
        }

        addMessage('user', query);
        chatHistory.push({ role: 'user', content: query });
        input.value = '';

        try {
            // Inside your submit listener in main.js
const res = await fetch('/api/kit/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        style: query,
        history: chatHistory // Ensure this matches your global variable name!
    })
});

            if (!res.ok) throw new Error('API failed');
            const payload = await res.json();

            setTimeout(() => {
                if (payload.type === 'questions') {
                    handleClarification(payload.data);
                    // Add AI's questions to history
                    chatHistory.push({ role: 'ai', content: payload.data.join(' ') });
                } 
                else {
                    // This handles 'final_kit' or any other successful build
                    addMessage('ai', payload.summary || `I've assembled your ${payload.kit_title || 'Kit'}:`);
                    renderFullKit(payload);
                    chatHistory = []; // Reset once the kit is done
                }
                refreshSidebar();
            }, 750);

        } catch (err) {
            console.error("Pipeline Error:", err);
            addMessage('ai', "Lab connection lost. Try refreshing?");
        }
    });

    // --- Helper Functions ---
    function addMessage(who, msg) {
        const row = document.createElement('div');
        row.className = `d-flex mb-4 pop-animation ${who === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
        const bubble = document.createElement('div');
        bubble.className = `p-3 shadow-sm ${who === 'user' ? 'msg-user' : 'msg-ai'}`;
        bubble.style.maxWidth = '75%';
        bubble.innerHTML = msg; 
        row.appendChild(bubble);
        display.appendChild(row);
        display.scrollTo({ top: display.scrollHeight, behavior: 'smooth' });
    }

    function handleClarification(questions) {
        let html = "I need a few more details:<ul>";
        questions.forEach(q => html += `<li>${q}</li>`);
        addMessage('ai', html + "</ul>");
    }

    function renderFullKit(data) {
        if (!data.sections) return;
        data.sections.forEach(section => {
            const header = document.createElement('div');
            header.innerHTML = `<div class="mt-4 mb-2"><h6 class="text-uppercase fw-bold text-muted small px-2">${section.name}</h6></div>`;
            display.appendChild(header);

            const grid = document.createElement('div');
            grid.innerHTML = `
                <div class="card border-0 shadow-sm mb-4 pop-animation ai-kit-grid" style="max-width: 90%;">
                    <div class="card-body p-4">
                        <div class="row g-3">${section.items.map(i => renderItemTile(i)).join('')}</div>
                    </div>
                </div>`;
            display.appendChild(grid);
        });
        display.scrollTo({ top: display.scrollHeight, behavior: 'smooth' });
    }

    function renderItemTile(item) {
    // 1. DATA NORMALIZATION: Handle both 'img_url' and 'imageUrl'
    const imgSrc = item.img_url || item.imageUrl || 'https://via.placeholder.com/150?text=No+Image';
    
    // 2. PRICE CLEANUP: Don't double-up on '$' if it's already there
    let priceDisplay = item.price || 'Check Price';
    if (priceDisplay !== 'Check Price' && !priceDisplay.includes('$')) {
        priceDisplay = `$${priceDisplay}`;
    }

    const url = item.buy_url || item.link || '#';

    return `
        <div class="col-6 col-md-4 mb-4">
            <div class="p-3 border rounded-4 bg-white h-100 d-flex flex-column shadow-sm transition-hover">
                <div class="text-center mb-3" style="height: 120px; overflow: hidden;">
                    <img src="${imgSrc}" class="img-fluid h-100" style="object-fit: contain;" 
                         onerror="this.src='https://via.placeholder.com/150?text=Product+Image'">
                </div>
                
                <span class="fw-bold smallest d-block mb-1 text-truncate" title="${item.name}">${item.name}</span>
                <p class="text-muted smallest mb-2 text-truncate-2" style="font-size: 0.65rem;">${item.description || ''}</p>
                
                <div class="mt-auto d-flex justify-content-between align-items-center pt-2 border-top">
                    <span class="fw-bold small text-primary">${priceDisplay}</span>
                    <a href="${url}" target="_blank" class="btn btn-sm btn-dark rounded-circle shadow-sm">
                        <i class="bi bi-arrow-up-right"></i>
                    </a>
                </div>
            </div>
        </div>`;
}
async function refreshSidebar() {
    const r = await fetch('/api/kit/history');
    const data = await r.json();
    const list = document.getElementById('chat-sidebar-list');
    
    list.innerHTML = data.map(k => `
        <button class="list-group-item list-group-item-action border-0 rounded-3 mb-1 py-2 text-truncate history-item" 
                data-kit-id="${k._id}">
            <i class="bi bi-clock-history me-2"></i> ${k.kit_name || 'Untitled Project'}
        </button>
    `).join('');

    // Attach listeners to history items
    document.querySelectorAll('.history-item').forEach(btn => {
        btn.addEventListener('click', async () => {
            const kitId = btn.getAttribute('data-kit-id');
            const res = await fetch(`/api/kit/${kitId}`);
            const kitData = await res.json();
            
            // Clear current view and render the old kit
            const display = document.getElementById('chat-display');
            display.innerHTML = ''; 
            renderFullKit(kitData);
        });
    });
}
});