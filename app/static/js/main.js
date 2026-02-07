document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const display = document.getElementById('chat-display');

    refreshSidebar();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;

        addMessage('user', query);
        input.value = '';

        try {
            const res = await fetch('/api/kit/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ style: query })
            });

            if (!res.ok) throw new Error('API failed');
            const payload = await res.json();

            setTimeout(() => {
                // SCENARIO 1: Clarification Gate is active
                if (payload.type === 'questions') {
                    handleClarification(payload.data);
                } 
                // SCENARIO 2: Deep-dive comparison (e.g., specialized gear)
                else if (payload.type === 'comparison') {
                    showComparison(payload);
                } 
                // SCENARIO 3: Full agentic Kit from your kit_service
                else {
                    addMessage('ai', payload.summary || `I've built the ${payload.kit_title} for you:`);
                    renderFullKit(payload);
                }
                refreshSidebar();
            }, 750);

        } catch (err) {
            console.error(err);
            addMessage('ai', "Server error. Check login status?");
        }
    });

    function addMessage(who, msg) {
        const row = document.createElement('div');
        row.className = `d-flex mb-4 pop-animation ${who === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
        const bubble = document.createElement('div');
        bubble.className = `p-3 shadow-sm ${who === 'user' ? 'msg-user' : 'msg-ai'}`;
        bubble.style.maxWidth = '75%';
        bubble.innerHTML = msg; // Changed to innerHTML to support list items from the Gate
        row.appendChild(bubble);
        display.appendChild(row);
        display.scrollTo({ top: display.scrollHeight, behavior: 'smooth' });
    }

    // Handles Scenario 1: Questions from planner_service
    function handleClarification(questions) {
        let html = "I need a few more details to get this right:<ul>";
        questions.forEach(q => html += `<li>${q}</li>`);
        addMessage('ai', html + "</ul>");
    }

    // Handles Scenario 3: Iterates through the sections in your kit.schema.json
    function renderFullKit(data) {
        if (!data.sections) return;

        data.sections.forEach(section => {
            const sectionHtml = `
                <div class="mt-4 mb-2">
                    <h6 class="text-uppercase fw-bold text-muted small px-2">${section.name}</h6>
                </div>
            `;
            const div = document.createElement('div');
            div.innerHTML = sectionHtml;
            display.appendChild(div);

            const gridHtml = `
                <div class="card border-0 shadow-sm mb-4 pop-animation ai-kit-grid" style="max-width: 90%;">
                    <div class="card-body p-4">
                        <div class="row g-3">${section.items.map(i => renderItemTile(i)).join('')}</div>
                    </div>
                </div>`;
            renderRawHtml(gridHtml);
        });
    }

    function renderItemTile(item) {
        // prioritize buy_url from search_service, fallback to Google Shopping
        const url = item.buy_url || `https://www.google.com/search?tbm=shop&q=${encodeURIComponent(item.name)}`;
        const price = item.price ? `$${item.price}` : 'View Price';

        return `
            <div class="col-6 col-md-4">
                <div class="p-3 border rounded-4 bg-light h-100 d-flex flex-column">
                    <span class="fw-bold smallest d-block mb-1 text-truncate">${item.name}</span>
                    <p class="text-muted smallest mb-2 text-truncate-2" style="font-size: 0.65rem;">${item.description}</p>
                    <div class="mt-auto d-flex justify-content-between align-items-center pt-2">
                        <span class="fw-bold small text-primary">${price}</span>
                        <a href="${url}" target="_blank" class="text-dark">
                            <i class="bi bi-arrow-up-right-circle fs-5"></i>
                        </a>
                    </div>
                </div>
            </div>`;
    }

    function showComparison(item) {
        const html = `
            <div class="card border-0 shadow-sm mb-4 pop-animation" style="max-width: 85%; border-radius: 20px;">
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="fw-bold mb-0">${item.name}</h5>
                        <span class="badge bg-success rounded-pill">$${item.price}</span>
                    </div>
                    <p class="small text-muted mb-3">${item.description}</p>
                    <div class="row g-2 mb-3">
                        <div class="col-6">
                            <div class="p-2 rounded-3 bg-light border-start border-success border-4 h-100">
                                <p class="smallest fw-bold text-success mb-1">THE GOOD</p>
                                <ul class="smallest p-0 list-unstyled mb-0">${item.pros.map(p => `<li>• ${p}</li>`).join('')}</ul>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-2 rounded-3 bg-light border-start border-danger border-4 h-100">
                                <p class="smallest fw-bold text-danger mb-1">THE BAD</p>
                                <ul class="smallest p-0 list-unstyled mb-0">${item.cons.map(c => `<li>• ${c}</li>`).join('')}</ul>
                            </div>
                        </div>
                    </div>
                    <a href="${item.buy_url}" target="_blank" class="btn btn-dark w-100 pill-btn">Get It Now <i class="bi bi-cart4 ms-2"></i></a>
                </div>
            </div>`;
        renderRawHtml(html);
    }

    function renderRawHtml(raw) {
        const div = document.createElement('div');
        div.className = 'd-flex mb-3 justify-content-start';
        div.innerHTML = raw;
        display.appendChild(div);
        display.scrollTo({ top: display.scrollHeight, behavior: 'smooth' });
    }

    async function refreshSidebar() {
        try {
            const r = await fetch('/api/kit/history');
            const data = await r.json();
            const list = document.getElementById('chat-sidebar-list');
            if (data && data.length > 0) {
                const historyHtml = data.map(k => `
                    <button class="list-group-item list-group-item-action border-0 rounded-3 text-muted small mb-1 py-2 text-truncate">
                        <i class="bi bi-clock-history me-2"></i> ${k.kit_name}
                    </button>
                `).join('');
                list.innerHTML = `
                    <button class="list-group-item list-group-item-action border-0 rounded-3 active bg-light text-dark fw-bold mb-2 py-2">
                        <i class="bi bi-plus-circle me-2"></i> Start Fresh
                    </button>
                    ${historyHtml}`;
            }
        } catch (err) {
            console.log(err);
        }
    }
});