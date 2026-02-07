/**
 * Main chat UI controller — handles form submission, message rendering,
 * kit display, and sidebar history.
 */

let chatHistory = [];

document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const input = document.getElementById("user-input");
    const display = document.getElementById("chat-display");

    refreshSidebar();

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const query = input.value.trim();
        if (!query) return;

        // Reset history when the user starts a new intent
        const lowerQuery = query.toLowerCase();
        if (lowerQuery.includes("build") || lowerQuery.includes("find") || lowerQuery.includes("kit")) {
            chatHistory = [];
        }

        addMessage("user", query);
        chatHistory.push({ role: "user", content: query });
        input.value = "";

        try {
            const response = await fetch("/api/kit/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    style: query,
                    history: chatHistory,
                }),
            });

            if (!response.ok) throw new Error("API request failed");
            const payload = await response.json();

            // Brief delay so the transition feels natural
            setTimeout(() => {
                if (payload.type === "questions") {
                    handleClarification(payload.data);
                    chatHistory.push({ role: "ai", content: payload.data.join(" ") });
                } else {
                    addMessage("ai", payload.summary || `I've assembled your ${payload.kit_title || "Kit"}:`);
                    renderFullKit(payload);
                    chatHistory = [];
                }
                refreshSidebar();
            }, 750);
        } catch (error) {
            console.error("Pipeline Error:", error);
            addMessage("ai", "Lab connection lost. Try refreshing?");
        }
    });

    /** Append a chat bubble to the display area. */
    function addMessage(sender, msg) {
        const row = document.createElement("div");
        row.className = `d-flex mb-4 pop-animation ${
            sender === "user" ? "justify-content-end" : "justify-content-start"
        }`;

        const bubble = document.createElement("div");
        bubble.className = `p-3 shadow-sm ${sender === "user" ? "msg-user" : "msg-ai"}`;
        bubble.style.maxWidth = "75%";
        bubble.innerHTML = msg;

        row.appendChild(bubble);
        display.appendChild(row);
        display.scrollTo({ top: display.scrollHeight, behavior: "smooth" });
    }

    /** Show follow-up questions from the clarification gate. */
    function handleClarification(questions) {
        let html = "I need a few more details:<ul>";
        questions.forEach((question) => {
            html += `<li>${question}</li>`;
        });
        addMessage("ai", html + "</ul>");
    }

    /** Render every section of a completed kit as product-tile grids. */
    function renderFullKit(data) {
        if (!data.sections) return;

        data.sections.forEach((section) => {
            const header = document.createElement("div");
            header.innerHTML = `
                <div class="mt-4 mb-2">
                    <h6 class="text-uppercase fw-bold text-muted small px-2">${section.name}</h6>
                </div>`;
            display.appendChild(header);

            const grid = document.createElement("div");
            grid.innerHTML = `
                <div class="card border-0 shadow-sm mb-4 pop-animation ai-kit-grid" style="max-width: 90%;">
                    <div class="card-body p-4">
                        <div class="row g-3">
                            ${section.items.map((item) => renderItemTile(item)).join("")}
                        </div>
                    </div>
                </div>`;
            display.appendChild(grid);
        });

        display.scrollTo({ top: display.scrollHeight, behavior: "smooth" });
    }

    /** Build the HTML for a single product tile inside a kit grid. */
    function renderItemTile(item) {
        const imgSrc = item.img_url || item.imageUrl || "https://via.placeholder.com/150?text=No+Image";

        let priceDisplay = item.price || "Check Price";
        if (priceDisplay !== "Check Price" && !priceDisplay.includes("$")) {
            priceDisplay = `$${priceDisplay}`;
        }

        const url = item.buy_url || item.link || "#";

        return `
            <div class="col-6 col-md-4 mb-4">
                <div class="p-3 border rounded-4 bg-white h-100 d-flex flex-column shadow-sm transition-hover">
                    <div class="text-center mb-3" style="height: 120px; overflow: hidden;">
                        <img src="${imgSrc}" class="img-fluid h-100" style="object-fit: contain;"
                             onerror="this.src='https://via.placeholder.com/150?text=Product+Image'">
                    </div>

                    <span class="fw-bold smallest d-block mb-1 text-truncate" title="${item.name}">
                        ${item.name}
                    </span>
                    <p class="text-muted smallest mb-2 text-truncate-2" style="font-size: 0.65rem;">
                        ${item.description || ""}
                    </p>

                    <div class="mt-auto d-flex justify-content-between align-items-center pt-2 border-top">
                        <span class="fw-bold small text-primary">${priceDisplay}</span>
                        <a href="${url}" target="_blank" class="btn btn-sm btn-dark rounded-circle shadow-sm">
                            <i class="bi bi-arrow-up-right"></i>
                        </a>
                    </div>
                </div>
            </div>`;
    }

    /** Reload the left-hand sidebar with the user's kit history. */
    async function refreshSidebar() {
        const response = await fetch("/api/kit/history");
        const data = await response.json();
        const list = document.getElementById("chat-sidebar-list");

        list.innerHTML = data.map((kit) => `
            <button class="list-group-item list-group-item-action border-0 rounded-3 mb-1 py-2 text-truncate history-item"
                    data-kit-id="${kit._id}">
                <i class="bi bi-clock-history me-2"></i> ${kit.kit_name || "Untitled Project"}
            </button>
        `).join("");

        document.querySelectorAll(".history-item").forEach((button) => {
            button.addEventListener("click", async () => {
                const kitId = button.getAttribute("data-kit-id");
                const res = await fetch(`/api/kit/${kitId}`);
                const kitData = await res.json();

                const chatDisplay = document.getElementById("chat-display");
                chatDisplay.innerHTML = "";
                renderFullKit(kitData);
            });
        });
    }
});