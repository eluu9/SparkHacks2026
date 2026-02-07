let chatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const display = document.getElementById('chat-display');
    const loadingBubble = document.getElementById('loading-bubble');

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = input.value.trim();
            if (!query) return;

            // Reset history for new builds
            if (query.toLowerCase().indexOf("build") !== -1 || query.toLowerCase().indexOf("kit") !== -1) {
                chatHistory = [];
            }

            // 1. Show User Message
            addMessage('user', query);
            chatHistory.push({ role: 'user', content: query });
            input.value = '';

            // 2. Show Loading
            if (loadingBubble) {
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
                console.log("DEBUG Payload:", payload);

                // 3. Hide Loading
                if (loadingBubble) loadingBubble.classList.add('d-none');

                if (!res.ok) throw new Error(payload.error || 'API failed');

                // --- ROBUST LOGIC FOR SES ENVIRONMENTS ---
                
                // Case A: Questions (Clarification)
                if (payload.type === 'questions') {
                    // Safety check for data
                    const qData = payload.data || payload.questions || [];
                    handleClarification(qData);
                    
                    // Save to history (JSON stringify is safe)
                    chatHistory.push({ role: 'ai', content: JSON.stringify(qData) });
                } 
                // Case B: Final Kit
                else if (payload.type === 'final_kit' || payload.sections) {
                    addMessage('ai', payload.summary || "Here is your kit:");
                    renderFullKit(payload);
                    chatHistory = []; 
                }
                // Case C: Fallback
                else {
                    addMessage('ai', payload.response || "I received data but I'm not sure how to display it.");
                }

            } catch (err) {
                console.error("Pipeline Error:", err);
                if (loadingBubble) loadingBubble.classList.add('d-none');
                addMessage('ai', "⚠️ Connection lost. Please try again.");
            }
        });
    }

    // --- Helper Functions ---

    function scrollToBottom() {
        if(display) display.scrollTo({ top: display.scrollHeight, behavior: 'smooth' });
    }

    function addMessage(who, msg) {
        // Determine styling
        const align = who === 'user' ? 'justify-content-end' : 'justify-content-start';
        const bgClass = who === 'user' ? 'msg-user' : 'msg-ai';
        const width = who === 'user' ? '75%' : '85%';
        const radius = who === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px';

        const html = `
            <div class="d-flex mb-4 ${align}">
                <div class="p-3 shadow-sm ${bgClass}" style="max-width: ${width}; border-radius: ${radius};">
                    ${msg}
                </div>
            </div>
        `;

        // Direct Injection Strategy (Bypasses node manipulation issues)
        if (loadingBubble) {
            loadingBubble.insertAdjacentHTML('beforebegin', html);
        } else {
            display.innerHTML += html;
        }
        scrollToBottom();
    }

    function handleClarification(questions) {
        let listHtml = "";
        
        // STANDARD FOR LOOP (Avoids SES 'forEach' issues)
        if (questions && questions.length > 0) {
            for (let i = 0; i < questions.length; i++) {
                listHtml += `<li class="mb-2">${questions[i]}</li>`;
            }
            
            const finalHtml = `
                <p class="mb-2 fw-bold">I need a few details to get this right:</p>
                <ul class="mb-0 ps-3">${listHtml}</ul>
            `;
            addMessage('ai', finalHtml);
        } else {
            addMessage('ai', String(questions));
        }
    }

    function renderFullKit(data) {
        if (!data.sections) return;
        
        let fullHtml = "";
        
        // Loop Sections
        for (let s = 0; s < data.sections.length; s++) {
            const section = data.sections[s];
            
            // Build Grid Items
            let gridItems = "";
            for (let i = 0; i < section.items.length; i++) {
                const item = section.items[i];
                const img = item.img_url || item.imageUrl || 'https://via.placeholder.com/150';
                const price = item.price || 'Check Price';
                const link = item.buy_url || item.link || '#';
                
                gridItems += `
                <div class="col-6 col-md-4">
                    <div class="card h-100 border shadow-sm">
                        <div class="card-img-top p-3 d-flex align-items-center justify-content-center" style="height: 120px;">
                            <img src="${img}" class="img-fluid" style="max-height: 100%; object-fit: contain;">
                        </div>
                        <div class="card-body p-2">
                            <h6 class="card-title text-truncate fw-bold small">${item.name}</h6>
                            <div class="d-flex justify-content-between align-items-center mt-1">
                                <span class="text-primary small fw-bold">${price}</span>
                                <a href="${link}" target="_blank" class="btn btn-sm btn-outline-dark rounded-circle"><i class="bi bi-arrow-up-right"></i></a>
                            </div>
                        </div>
                    </div>
                </div>`;
            }

            fullHtml += `
                <div class="mt-4 mb-3 pb-1 border-bottom"><h6 class="fw-bold small">${section.name}</h6></div>
                <div class="row g-3 mb-4">${gridItems}</div>
            `;
        }

        const wrapperHtml = `
            <div class="d-flex mb-4 w-100">
                <div class="w-100 px-2">${fullHtml}</div>
            </div>
        `;

        if (loadingBubble) {
            loadingBubble.insertAdjacentHTML('beforebegin', wrapperHtml);
        } else {
            display.innerHTML += wrapperHtml;
        }
        scrollToBottom();
    }
});