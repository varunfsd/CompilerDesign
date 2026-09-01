/**
 * Visualizer & Rendering Engine for AST, CFG, Tokens, Symbols, and Optimizations.
 */

class VisualizerManager {
    constructor() {
        if (window.mermaid) {
            mermaid.initialize({
                startOnLoad: false,
                theme: "dark",
                themeVariables: {
                    primaryColor: "#1e293b",
                    primaryTextColor: "#f8fafc",
                    primaryBorderColor: "#38bdf8",
                    lineColor: "#64748b",
                    secondaryColor: "#0f172a",
                    tertiaryColor: "#1e1b4b"
                },
                flowchart: {
                    useMaxWidth: false,
                    htmlLabels: true,
                    curve: "basis"
                }
            });
        }
    }

    async renderMermaid(containerId, chartDefinition) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!chartDefinition || chartDefinition.trim() === "") {
            container.innerHTML = `<div class="empty-state">No graph available for this stage</div>`;
            return;
        }

        try {
            const uniqueId = `mermaid_${Date.now()}`;
            const { svg } = await mermaid.render(uniqueId, chartDefinition);
            container.innerHTML = svg;
        } catch (err) {
            console.error("Mermaid Render Error:", err);
            container.innerHTML = `<pre class="code-block">${chartDefinition}</pre>`;
        }
    }

    renderTokens(tokens) {
        const tbody = document.getElementById("tokensTableBody");
        const countLabel = document.getElementById("tokenCountLabel");
        if (!tbody) return;

        countLabel.textContent = `${tokens.length} Tokens generated`;

        if (!tokens || tokens.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No tokens generated</td></tr>`;
            return;
        }

        tbody.innerHTML = tokens.map((t, idx) => `
            <tr>
                <td>${idx + 1}</td>
                <td><span class="badge badge-token">${t.type}</span></td>
                <td><strong>${this.escapeHtml(t.value || t.raw || '')}</strong></td>
                <td>${t.line}</td>
                <td>${t.column}</td>
                <td>${t.length}</td>
            </tr>
        `).join("");
    }

    renderSymbols(symbols) {
        const tbody = document.getElementById("symbolsTableBody");
        const countLabel = document.getElementById("symbolCountLabel");
        if (!tbody) return;

        countLabel.textContent = `${symbols.length} Scoped Symbols`;

        if (!symbols || symbols.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="table-empty">No symbols registered</td></tr>`;
            return;
        }

        tbody.innerHTML = symbols.map(s => `
            <tr>
                <td><strong>${this.escapeHtml(s.name)}</strong></td>
                <td><span class="badge">${s.category}</span></td>
                <td><span class="badge badge-success">${this.escapeHtml(s.type)}</span></td>
                <td>${s.scope_name}</td>
                <td>${s.scope_level}</td>
                <td>${s.line}</td>
            </tr>
        `).join("");
    }

    renderOptimizations(steps) {
        const container = document.getElementById("optStepsContainer");
        if (!container) return;

        if (!steps || steps.length === 0) {
            container.innerHTML = `<div class="empty-state">No optimization passes recorded</div>`;
            return;
        }

        container.innerHTML = steps.map((step, idx) => `
            <div class="opt-card">
                <div class="opt-card-header">
                    <span class="opt-pass-name">Pass ${idx + 1}: ${step.pass_name}</span>
                    <span class="badge ${step.has_changed ? 'badge-success' : ''}">
                        ${step.has_changed ? '⚡ Applied Changes' : '✓ Unchanged'}
                    </span>
                </div>
                <div class="opt-pass-desc">${step.description}</div>
                ${step.changes_made && step.changes_made.length > 0 ? `
                    <ul class="opt-changes-list">
                        ${step.changes_made.map(c => `<li>• ${this.escapeHtml(c)}</li>`).join("")}
                    </ul>
                ` : ''}
            </div>
        `).join("");
    }

    renderMemory(variables) {
        const tbody = document.getElementById("memoryTableBody");
        if (!tbody) return;

        const entries = Object.entries(variables || {});
        if (entries.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="table-empty">No active variables in memory</td></tr>`;
            return;
        }

        tbody.innerHTML = entries.map(([name, val]) => `
            <tr>
                <td><strong>${this.escapeHtml(name)}</strong></td>
                <td>${this.escapeHtml(String(val))}</td>
                <td><span class="badge">${typeof val}</span></td>
            </tr>
        `).join("");
    }

    escapeHtml(str) {
        if (typeof str !== "string") return str;
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

window.VisualizerManager = VisualizerManager;
