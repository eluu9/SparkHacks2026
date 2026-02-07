let chatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const display = document.getElementById('chat-display');
    const loadingBubble = document.getElementById('loading-bubble');

    if(chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            const query = input.value.trim();
            if (!query) return;

            if (query.toLowerCase().includes("build") || query.toLowerCase().includes("kit")) {
                chatHistory = []; 
            }

            addMessage('user', query);
            chatHistory.push({ role: 'user', content: query });
            input.value = '';

            if(loadingBubble) {
                loadingBubble.classList.remove('d-none');
                scrollToBottom();
            }

            try {
                const res = await fetch('/api/kit/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ style: query, history: chatHistory })
                });

                const payload = await res.json();
                
                // Hide Loading
                if(loadingBubble) loadingBubble.classList.add('d-none');
                if (!res.ok) throw new Error(payload.error || 'API failed');

                if (payload.type === 'questions') {
                    handleClarification(payload.data);
                    chatHistory.push({ role: 'ai', content: payload.data.join(' ') });
                } else {
                    addMessage('ai', payload.summary || `I've assembled your ${payload.kit_title}:`);
                    renderFullKit(payload);
                    chatHistory = []; 
                }

            } catch (err) {
                console.error(err);
                if(loadingBubble) loadingBubble.classList.add('d-none');
                addMessage('ai', "⚠️ Connection lost. Please try again.");
            }
        });
    }

    function scrollToBottom() {
        display.scrollTo({ top: display.scrollHeight, behavior: 'smooth' });
    }

    function addMessage(who, msg) {
        const row = document.createElement('div');
        row.className = `d-flex mb-4 pop-animation ${who === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
        const bubble = document.createElement('div');
        bubble.className = `p-3 shadow-sm ${who === 'user' ? 'msg-user' : 'msg-ai'}`;
        if(who === 'user') bubble.style.maxWidth = '75%'; else bubble.style.maxWidth = '85%';
        bubble.innerHTML = msg; 
        
        if(loadingBubble && display.contains(loadingBubble)) {
            display.insertBefore(row, loadingBubble);
        } else {
            display.appendChild(row);
        }
        scrollToBottom();
    }

    function handleClarification(questions) {
        let html = "<p>I need a few details:</p><ul>";
        questions.forEach(q => html += `<li>${q}</li>`);
        html += "</ul>";
        addMessage('ai', html);
    }

    function renderFullKit(data) {
        if (!data.sections) return;
        const kitContainer = document.createElement('div');
        
        data.sections.forEach(section => {
            const header = document.createElement('div');
            header.innerHTML = `<div class="mt-4 mb-3 pb-1 border-bottom"><h6 class="text-uppercase fw-bold small">${section.name}</h6></div>`;
            kitContainer.appendChild(header);

            const grid = document.createElement('div');
            grid.className = 'row g-3 mb-4';
            grid.innerHTML = section.items.map(i => {
                const price = i.price && !String(i.price).includes('$') ? `$${i.price}` : (i.price || 'Check Price');
                return `
                <div class="col-6 col-md-4">
                    <div class="card h-100 border shadow-sm">
                        <div class="card-img-top p-3 d-flex align-items-center justify-content-center" style="height: 140px;">
                            <img src="${i.img_url || 'https://via.placeholder.com/150'}" class="img-fluid" style="max-height: 100%; object-fit: contain;">
                        </div>
                        <div class="card-body p-3">
                            <h6 class="card-title text-truncate fw-bold small">${i.name}</h6>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <span class="fw-bold text-primary small">${price}</span>
                                <a href="${i.buy_url || '#'}" target="_blank" class="btn btn-sm btn-outline-dark rounded-circle"><i class="bi bi-arrow-up-right"></i></a>
                            </div>
                        </div>
                    </div>
                </div>`;
            }).join('');
            kitContainer.appendChild(grid);
        });

        const row = document.createElement('div');
        row.className = 'd-flex mb-4 pop-animation justify-content-start w-100';
        const wrapper = document.createElement('div');
        wrapper.className = 'w-100 px-2'; 
        wrapper.appendChild(kitContainer);
        row.appendChild(wrapper);

        if(loadingBubble && display.contains(loadingBubble)) {
            display.insertBefore(row, loadingBubble);
        } else {
            display.appendChild(row);
        }
        scrollToBottom();
    }
});