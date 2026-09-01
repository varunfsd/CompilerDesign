/**
 * ScopeLab - UI Controller and Visualization Renderer
 */

export class UIController {
    constructor() {
        this.currentResult = null;
        this.selectedScopeId = null;
        this.selectedResolutionId = null;
        this.activeTab = 'overview';
    }

    init() {
        this.cacheDOM();
        this.bindEvents();
        this.initEditorLineNumbers();
    }

    cacheDOM() {
        // Elements
        this.sourceEditor = document.getElementById('source-editor');
        this.lineNumbers = document.getElementById('line-numbers');
        this.presetSelect = document.getElementById('preset-select');
        this.btnAnalyze = document.getElementById('btn-analyze');
        this.btnReset = document.getElementById('btn-reset');
        this.btnClear = document.getElementById('btn-clear');
        this.analysisStatus = document.getElementById('analysis-status');

        // Metrics
        this.statTokens = document.getElementById('stat-tokens');
        this.statScopes = document.getElementById('stat-scopes');
        this.statSymbols = document.getElementById('stat-symbols');
        this.statErrors = document.getElementById('stat-errors');
        this.statWarnings = document.getElementById('stat-warnings');

        // Tabs
        this.tabButtons = document.querySelectorAll('.tab-btn');
        this.tabPanes = document.querySelectorAll('.tab-pane');

        // Views
        this.overviewContent = document.getElementById('overview-content');
        this.symbolTableBody = document.getElementById('symbol-table-body');
        this.scopeFilterSelect = document.getElementById('scope-filter-select');
        this.scopeHierarchyContainer = document.getElementById('scope-hierarchy-container');
        this.scopeDetailPanel = document.getElementById('scope-detail-panel');
        this.resolutionSelect = document.getElementById('resolution-select');
        this.resolutionFlowContainer = document.getElementById('resolution-flow-container');
        this.tokenTableBody = document.getElementById('token-table-body');
        this.tokenFilterInput = document.getElementById('token-filter-input');
        this.diagnosticsList = document.getElementById('diagnostics-list');
        this.recoveryList = document.getElementById('recovery-list');
        this.explanationContent = document.getElementById('explanation-content');
    }

    bindEvents() {
        // Tab switching
        this.tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.dataset.tab;
                this.switchTab(targetTab);
            });
        });

        // Editor input
        this.sourceEditor.addEventListener('input', () => {
            this.updateLineNumbers();
            this.clearEditorHighlights();
        });

        this.sourceEditor.addEventListener('scroll', () => {
            this.lineNumbers.scrollTop = this.sourceEditor.scrollTop;
        });

        // Tab key support in textarea
        this.sourceEditor.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.sourceEditor.selectionStart;
                const end = this.sourceEditor.selectionEnd;
                this.sourceEditor.value = this.sourceEditor.value.substring(0, start) + '    ' + this.sourceEditor.value.substring(end);
                this.sourceEditor.selectionStart = this.sourceEditor.selectionEnd = start + 4;
                this.updateLineNumbers();
            }
        });

        // Filter events
        if (this.scopeFilterSelect) {
            this.scopeFilterSelect.addEventListener('change', (e) => {
                this.renderSymbolTable(this.currentResult, e.target.value);
            });
        }

        if (this.tokenFilterInput) {
            this.tokenFilterInput.addEventListener('input', (e) => {
                this.renderTokens(this.currentResult, e.target.value);
            });
        }

        if (this.resolutionSelect) {
            this.resolutionSelect.addEventListener('change', (e) => {
                this.selectedResolutionId = e.target.value;
                this.renderExplainResolution(this.currentResult);
            });
        }
    }

    initEditorLineNumbers() {
        this.updateLineNumbers();
    }

    updateLineNumbers(errorLines = new Set()) {
        const lines = this.sourceEditor.value.split('\n');
        const count = lines.length || 1;
        let html = '';

        for (let i = 1; i <= count; i++) {
            const hasError = errorLines.has(i);
            html += `<div class="line-number ${hasError ? 'line-error' : ''}" data-line="${i}">${i}</div>`;
        }

        this.lineNumbers.innerHTML = html;
    }

    highlightEditorLine(line) {
        if (!line) return;
        const lineNums = this.lineNumbers.querySelectorAll('.line-number');
        lineNums.forEach(el => {
            if (parseInt(el.dataset.line, 10) === line) {
                el.classList.add('active-highlight');
            } else {
                el.classList.remove('active-highlight');
            }
        });

        // Scroll editor to line
        const lineHeight = 21; // approximate line height in px
        this.sourceEditor.scrollTop = (line - 3) * lineHeight;
    }

    clearEditorHighlights() {
        const lineNums = this.lineNumbers.querySelectorAll('.line-number');
        lineNums.forEach(el => el.classList.remove('active-highlight'));
    }

    switchTab(tabId) {
        this.activeTab = tabId;
        this.tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });
        this.tabPanes.forEach(pane => {
            pane.classList.toggle('active', pane.id === `tab-${tabId}`);
        });
    }

    renderAll(result, tokens) {
        this.currentResult = result;
        this.currentTokens = tokens;

        const errorCount = result.diagnostics.filter(d => d.severity === 'ERROR').length;
        const warningCount = result.diagnostics.filter(d => d.severity === 'WARNING').length;

        // 1. Update Metrics
        this.statTokens.textContent = tokens ? tokens.length : 0;
        this.statScopes.textContent = result.scopes.length;
        this.statSymbols.textContent = result.symbolTable.length;
        this.statErrors.textContent = errorCount;
        this.statWarnings.textContent = warningCount;

        // Status badge
        if (errorCount === 0) {
            this.analysisStatus.innerHTML = `<span class="badge badge-success">✓ Analysis Succeeded (0 errors, ${warningCount} warnings)</span>`;
        } else {
            this.analysisStatus.innerHTML = `<span class="badge badge-error">✕ Analysis Completed with ${errorCount} error${errorCount > 1 ? 's' : ''}</span>`;
        }

        // Line number error markers
        const errorLines = new Set(result.diagnostics.filter(d => d.severity === 'ERROR').map(d => d.line));
        this.updateLineNumbers(errorLines);

        // 2. Render Tab Contents
        this.renderOverview(result);
        this.renderSymbolTable(result);
        this.renderScopeHierarchy(result);
        this.renderExplainResolution(result);
        this.renderTokens(tokens);
        this.renderDiagnostics(result);
        this.renderEducationalExplanation(result);
    }

    // --- Tab 1: Overview ---
    renderOverview(result) {
        const errorCount = result.diagnostics.filter(d => d.severity === 'ERROR').length;
        const scopeErrors = result.diagnostics.filter(d => d.category === 'Scope Error');

        let html = `
            <div class="overview-grid">
                <div class="overview-section">
                    <div class="section-header">
                        <span class="section-title">Compiler Pipeline Summary</span>
                        <span class="section-badge">${result.scopes.length} Scopes Active</span>
                    </div>
                    <div class="pipeline-flow">
                        <div class="pipeline-stage complete">
                            <span class="stage-step">1</span>
                            <span class="stage-name">Lexical Analysis</span>
                            <span class="stage-detail">${this.currentTokens ? this.currentTokens.length : 0} tokens</span>
                        </div>
                        <div class="pipeline-stage complete">
                            <span class="stage-step">2</span>
                            <span class="stage-name">Parsing & AST</span>
                            <span class="stage-detail">Recursive Descent</span>
                        </div>
                        <div class="pipeline-stage complete">
                            <span class="stage-step">3</span>
                            <span class="stage-name">Scope & Symbol Table</span>
                            <span class="stage-detail">${result.symbolTable.length} symbols recorded</span>
                        </div>
                        <div class="pipeline-stage ${errorCount > 0 ? 'stage-error' : 'complete'}">
                            <span class="stage-step">4</span>
                            <span class="stage-name">Semantic Check</span>
                            <span class="stage-detail">${errorCount > 0 ? `${errorCount} violation(s)` : 'Passed clean'}</span>
                        </div>
                    </div>
                </div>

                <div class="overview-section">
                    <div class="section-header">
                        <span class="section-title">Scope Hierarchy Summary</span>
                        <span class="action-link" onclick="window.scopeLabApp.ui.switchTab('scopes')">View Interactive Tree →</span>
                    </div>
                    <div class="ascii-tree-box">
                        <pre class="ascii-tree">${this.generateAsciiTree(result.scopes[0])}</pre>
                    </div>
                </div>
            </div>

            <div class="overview-section mt-16">
                <div class="section-header">
                    <span class="section-title">Primary Diagnostic & Action</span>
                </div>
                ${result.diagnostics.length === 0 ? `
                    <div class="clean-state-box">
                        <span class="clean-icon">✓</span>
                        <div class="clean-text">
                            <strong>All Semantic Checks Passed</strong>
                            <p>All variables and functions adhere to lexical scoping rules. No type mismatches or redeclarations detected.</p>
                        </div>
                    </div>
                ` : `
                    <div class="diagnostic-summary-card">
                        ${result.diagnostics.slice(0, 2).map(diag => `
                            <div class="diag-item ${diag.severity.toLowerCase()}">
                                <div class="diag-badge-row">
                                    <span class="badge badge-${diag.severity.toLowerCase()}">${diag.severity}</span>
                                    <span class="diag-loc">Line ${diag.line}:${diag.column}</span>
                                    <span class="diag-cat">${diag.category}</span>
                                </div>
                                <div class="diag-title">${diag.title}: ${this.escapeHtml(diag.message)}</div>
                                ${diag.declaredInScope ? `
                                    <div class="diag-meta-grid">
                                        <div><span class="meta-label">Declared in:</span> <span class="meta-val">${diag.declaredInScope}</span></div>
                                        <div><span class="meta-label">Used in:</span> <span class="meta-val">${diag.usedInScope || 'Current'}</span></div>
                                    </div>
                                ` : ''}
                                ${diag.recoveryTechnique ? `
                                    <div class="diag-recovery-box">
                                        <span class="rec-label">Recovery Action:</span> ${diag.recoveryTechnique}
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                `}
            </div>
        `;

        this.overviewContent.innerHTML = html;
    }

    // --- Tab 2: Symbol Table ---
    renderSymbolTable(result, filterScope = 'ALL') {
        if (!result) return;

        // Populate scope filter dropdown
        let filterOptions = `<option value="ALL">All Scopes (${result.symbolTable.length} symbols)</option>`;
        result.scopes.forEach(sc => {
            const count = result.symbolTable.filter(s => s.scopeId === sc.id).length;
            const selected = filterScope === sc.id ? 'selected' : '';
            filterOptions += `<option value="${sc.id}" ${selected}>${sc.name} (Level ${sc.level}) [${count}]</option>`;
        });
        if (this.scopeFilterSelect) {
            this.scopeFilterSelect.innerHTML = filterOptions;
        }

        const filteredSymbols = filterScope === 'ALL'
            ? result.symbolTable
            : result.symbolTable.filter(s => s.scopeId === filterScope);

        if (filteredSymbols.length === 0) {
            this.symbolTableBody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No symbols declared in selected scope.</td></tr>`;
            return;
        }

        let html = '';
        filteredSymbols.forEach(sym => {
            const isFuncOrProc = sym.type.startsWith('function') || sym.type.startsWith('procedure');
            html += `
                <tr class="symbol-row" onclick="window.scopeLabApp.ui.highlightEditorLine(${sym.declarationLine})">
                    <td class="font-mono font-bold text-accent">${this.escapeHtml(sym.name)}</td>
                    <td><span class="type-tag ${sym.type}">${this.escapeHtml(sym.type)}</span></td>
                    <td class="font-mono">${this.escapeHtml(sym.scopeName)}</td>
                    <td class="text-center font-mono">${sym.scopeLevel}</td>
                    <td class="font-mono text-muted">0x${sym.memoryLocation.toString(16).toUpperCase()} (${sym.memoryLocation})</td>
                    <td class="text-center">${sym.isParameter ? '<span class="badge badge-param">Yes</span>' : '<span class="text-muted">No</span>'}</td>
                    <td class="font-mono text-muted">${sym.declarationLine}:${sym.declarationCol}</td>
                    <td class="text-center">
                        <span class="ref-count ${sym.references.length > 0 ? 'ref-active' : 'ref-zero'}" title="${sym.references.map(r => `Line ${r.line} in ${r.scopeName}`).join(', ')}">
                            ${sym.references.length} ref${sym.references.length === 1 ? '' : 's'}
                        </span>
                    </td>
                </tr>
            `;
        });

        this.symbolTableBody.innerHTML = html;
    }

    // --- Tab 3: Scope Hierarchy ---
    renderScopeHierarchy(result) {
        if (!result || result.scopes.length === 0) return;

        const rootScope = result.scopes[0];
        let treeHtml = `<div class="scope-tree-root">${this.renderScopeTreeNode(rootScope, result)}</div>`;
        this.scopeHierarchyContainer.innerHTML = treeHtml;

        // Bind click on nodes
        const scopeNodes = this.scopeHierarchyContainer.querySelectorAll('.scope-node');
        scopeNodes.forEach(node => {
            node.addEventListener('click', (e) => {
                e.stopPropagation();
                const scopeId = node.dataset.scopeId;
                this.selectScope(scopeId, result);
            });
        });

        // Default select root or first function
        const defaultSelect = result.scopes[1] ? result.scopes[1].id : rootScope.id;
        this.selectScope(this.selectedScopeId || defaultSelect, result);
    }

    renderScopeTreeNode(scope, result) {
        const symbolCount = scope.symbols.size;
        const isSelected = this.selectedScopeId === scope.id;

        let typeBadge = 'GLOBAL';
        if (scope.type === 'FUNCTION') typeBadge = 'FUNC';
        else if (scope.type === 'PROCEDURE') typeBadge = 'PROC';
        else if (scope.type === 'BLOCK') typeBadge = 'BLOCK';

        let html = `
            <div class="scope-tree-item">
                <div class="scope-node ${isSelected ? 'selected' : ''}" data-scope-id="${scope.id}">
                    <div class="scope-node-header">
                        <span class="scope-badge scope-${typeBadge.toLowerCase()}">${typeBadge}</span>
                        <span class="scope-title">${this.escapeHtml(scope.name)}</span>
                        <span class="scope-level-tag">L${scope.level}</span>
                    </div>
                    <div class="scope-meta-preview">
                        ${symbolCount} symbol${symbolCount === 1 ? '' : 's'} • Lines ${scope.startLine}-${scope.endLine}
                    </div>
                </div>
        `;

        if (scope.children && scope.children.length > 0) {
            html += `<div class="scope-children">`;
            scope.children.forEach(child => {
                html += this.renderScopeTreeNode(child, result);
            });
            html += `</div>`;
        }

        html += `</div>`;
        return html;
    }

    selectScope(scopeId, result) {
        this.selectedScopeId = scopeId;
        const scope = result.scopes.find(s => s.id === scopeId);
        if (!scope) return;

        // Update selected class in tree
        const nodes = this.scopeHierarchyContainer.querySelectorAll('.scope-node');
        nodes.forEach(n => n.classList.toggle('selected', n.dataset.scopeId === scopeId));

        // Accessible variables calculation
        const accessible = scope.getAccessibleSymbols();
        const localSymbols = scope.getLocalSymbols();

        let parentChain = [];
        let curr = scope.parent;
        while (curr) {
            parentChain.push(`${curr.name} (L${curr.level})`);
            curr = curr.parent;
        }

        let detailHtml = `
            <div class="scope-inspector">
                <div class="inspector-header">
                    <div class="inspector-title">
                        <h3>${this.escapeHtml(scope.name)}</h3>
                        <span class="scope-level-pill">Scope Level ${scope.level}</span>
                    </div>
                    <div class="inspector-actions">
                        <button class="btn btn-xs btn-outline" onclick="window.scopeLabApp.ui.filterSymbolTableByScope('${scope.id}')">Filter Symbol Table</button>
                    </div>
                </div>

                <div class="inspector-info-grid">
                    <div class="info-cell">
                        <span class="info-label">Parent Scope</span>
                        <span class="info-value">${scope.parent ? `${scope.parent.name} (L${scope.parent.level})` : 'None (Root Global)'}</span>
                    </div>
                    <div class="info-cell">
                        <span class="info-label">Lexical Chain</span>
                        <span class="info-value">${parentChain.length > 0 ? parentChain.join(' → ') : 'Root Scope'}</span>
                    </div>
                    <div class="info-cell">
                        <span class="info-label">Source Lines</span>
                        <span class="info-value font-mono">Lines ${scope.startLine} – ${scope.endLine}</span>
                    </div>
                </div>

                <div class="symbols-section mt-12">
                    <div class="sub-header">Locally Declared Symbols (${localSymbols.length})</div>
                    ${localSymbols.length === 0 ? `
                        <p class="text-muted text-sm italic">No symbols declared locally in this scope block.</p>
                    ` : `
                        <div class="symbol-tags-list">
                            ${localSymbols.map(sym => `
                                <div class="symbol-chip" onclick="window.scopeLabApp.ui.highlightEditorLine(${sym.declarationLine})">
                                    <span class="chip-name">${sym.name}</span>
                                    <span class="chip-type">${sym.type}</span>
                                    <span class="chip-addr">0x${sym.memoryLocation.toString(16).toUpperCase()}</span>
                                    ${sym.isParameter ? '<span class="chip-param">param</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>

                <div class="accessible-section mt-16">
                    <div class="sub-header">Variables Accessible (Lexical Scope Inheritance)</div>
                    <div class="accessible-table-wrap">
                        <table class="data-table text-sm">
                            <thead>
                                <tr>
                                    <th>Variable</th>
                                    <th>Type</th>
                                    <th>Inherited From</th>
                                    <th>Level</th>
                                    <th>Memory</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${accessible.map(item => `
                                    <tr>
                                        <td class="font-mono font-bold text-accent">${item.symbol.name}</td>
                                        <td><span class="type-tag ${item.symbol.type}">${item.symbol.type}</span></td>
                                        <td>${item.declaredInScope}</td>
                                        <td>L${item.declaredAtLevel}</td>
                                        <td class="font-mono text-muted">0x${item.symbol.memoryLocation.toString(16).toUpperCase()}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        this.scopeDetailPanel.innerHTML = detailHtml;
    }

    filterSymbolTableByScope(scopeId) {
        this.switchTab('symbols');
        if (this.scopeFilterSelect) {
            this.scopeFilterSelect.value = scopeId;
            this.renderSymbolTable(this.currentResult, scopeId);
        }
    }

    // --- Tab 4: Explain Resolution ---
    renderExplainResolution(result) {
        if (!result || !this.resolutionSelect) return;

        // Populate dropdown
        if (result.resolutions.length === 0) {
            this.resolutionSelect.innerHTML = `<option value="">No variable lookups in program</option>`;
            this.resolutionFlowContainer.innerHTML = `<p class="text-muted p-16">No variable references detected in expressions or statements.</p>`;
            return;
        }

        let selectOptions = '';
        result.resolutions.forEach((res, idx) => {
            const selected = (this.selectedResolutionId === res.id || (!this.selectedResolutionId && idx === 0)) ? 'selected' : '';
            const statusIcon = res.resolved ? '✓' : '✕';
            selectOptions += `<option value="${res.id}" ${selected}>${statusIcon} Identifier '${res.identifier}' at line ${res.usageLine} (${res.usageScope})</option>`;
        });
        this.resolutionSelect.innerHTML = selectOptions;

        // Determine active resolution
        const activeRes = result.resolutions.find(r => r.id === this.selectedResolutionId) || result.resolutions[0];
        if (!activeRes) return;
        this.selectedResolutionId = activeRes.id;

        // Render step by step upward resolution path
        let stepsHtml = '';
        activeRes.lookupPath.forEach((step, idx) => {
            const isLast = idx === activeRes.lookupPath.length - 1;
            stepsHtml += `
                <div class="res-step-card ${step.found ? 'step-found' : 'step-not-found'}">
                    <div class="step-badge">Step ${idx + 1}</div>
                    <div class="step-content">
                        <div class="step-header">
                            <span class="step-scope-name">${this.escapeHtml(step.scopeName)}</span>
                            <span class="step-level">Level ${step.scopeLevel}</span>
                        </div>
                        <div class="step-result">
                            ${step.found ? `
                                <span class="badge badge-success">✓ Found '${activeRes.identifier}'</span>
                                <span class="step-detail">Declared at line ${step.symbol.declarationLine}, Type: <code>${step.symbol.type}</code>, Memory: <code>0x${step.symbol.memoryLocation.toString(16).toUpperCase()}</code></span>
                            ` : `
                                <span class="badge badge-neutral">✕ Not found in local symbols</span>
                                ${!isLast ? `<span class="step-arrow">Climbing up parent pointer →</span>` : ''}
                            `}
                        </div>
                    </div>
                </div>
            `;
            if (!isLast) {
                stepsHtml += `<div class="res-arrow-connector">↓</div>`;
            }
        });

        let outcomeHtml = '';
        if (activeRes.status === 'SUCCESS') {
            outcomeHtml = `
                <div class="res-outcome-card outcome-success">
                    <div class="outcome-title">
                        <span class="outcome-icon">✓</span>
                        <span>Resolution Succeeded</span>
                    </div>
                    <div class="outcome-body">
                        <p>Identifier <code>${activeRes.identifier}</code> was successfully bound to its declaration in <strong>${activeRes.declaredScope}</strong>.</p>
                        <div class="outcome-spec-grid mt-8">
                            <div><span class="text-muted">Type:</span> <strong>${activeRes.resolvedSymbol.type}</strong></div>
                            <div><span class="text-muted">Scope Level:</span> <strong>${activeRes.resolvedSymbol.scopeLevel}</strong></div>
                            <div><span class="text-muted">Memory Address:</span> <strong>0x${activeRes.resolvedSymbol.memoryLocation.toString(16).toUpperCase()} (${activeRes.resolvedSymbol.memoryLocation})</strong></div>
                            <div><span class="text-muted">Declaration Line:</span> <strong>Line ${activeRes.resolvedSymbol.declarationLine}:${activeRes.resolvedSymbol.declarationCol}</strong></div>
                        </div>
                    </div>
                </div>
            `;
        } else if (activeRes.status === 'SCOPE_VIOLATION') {
            outcomeHtml = `
                <div class="res-outcome-card outcome-error">
                    <div class="outcome-title">
                        <span class="outcome-icon">✕</span>
                        <span>Scope Violation Detected</span>
                    </div>
                    <div class="outcome-body">
                        <p><strong>'${activeRes.identifier}'</strong> is not accessible from <strong>${activeRes.usageScope}</strong>.</p>
                        <p class="text-sm mt-4 text-muted">${activeRes.note}</p>
                        <div class="educational-note-box mt-8">
                            <strong>Why this happened:</strong>
                            <p>Variables declared inside a block or child function are discarded from the active scope chain when that block terminates. The current statement is in an outer scope, so searching up the parent chain never encounters the closed inner scope.</p>
                        </div>
                    </div>
                </div>
            `;
        } else {
            outcomeHtml = `
                <div class="res-outcome-card outcome-error">
                    <div class="outcome-title">
                        <span class="outcome-icon">✕</span>
                        <span>Undeclared Identifier</span>
                    </div>
                    <div class="outcome-body">
                        <p>Identifier <strong>'${activeRes.identifier}'</strong> was searched through all enclosing scopes up to Global Scope and was never declared.</p>
                    </div>
                </div>
            `;
        }

        let containerHtml = `
            <div class="explain-resolution-view">
                <div class="resolution-summary-strip">
                    <div><span class="text-muted">Resolving:</span> <strong class="font-mono text-accent">${activeRes.identifier}</strong></div>
                    <div><span class="text-muted">Usage Site:</span> <strong>Line ${activeRes.usageLine}:${activeRes.usageColumn}</strong></div>
                    <div><span class="text-muted">Current Scope:</span> <strong>${activeRes.usageScope}</strong></div>
                    <button class="btn btn-xs btn-outline" onclick="window.scopeLabApp.ui.highlightEditorLine(${activeRes.usageLine})">Jump to Line</button>
                </div>

                <div class="resolution-steps-timeline mt-16">
                    ${stepsHtml}
                </div>

                <div class="mt-16">
                    ${outcomeHtml}
                </div>
            </div>
        `;

        this.resolutionFlowContainer.innerHTML = containerHtml;
    }

    // --- Tab 5: Tokens ---
    renderTokens(tokens, filterText = '') {
        if (!tokens || tokens.length === 0) {
            this.tokenTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No tokens available.</td></tr>`;
            return;
        }

        const filter = (filterText || '').toLowerCase().trim();
        const filtered = tokens.filter(t => {
            if (!filter) return true;
            return t.type.toLowerCase().includes(filter) ||
                   t.value.toLowerCase().includes(filter) ||
                   t.category.toLowerCase().includes(filter);
        });

        let html = '';
        filtered.forEach((tok, idx) => {
            html += `
                <tr class="token-row" onclick="window.scopeLabApp.ui.highlightEditorLine(${tok.line})">
                    <td class="font-mono text-muted text-center">${idx + 1}</td>
                    <td><span class="badge badge-token badge-${tok.category}">${tok.type}</span></td>
                    <td class="font-mono font-bold">${this.escapeHtml(tok.value === '' ? 'EOF' : tok.value)}</td>
                    <td class="font-mono text-muted">${tok.line}:${tok.column}</td>
                    <td class="text-muted">${tok.category}</td>
                </tr>
            `;
        });

        this.tokenTableBody.innerHTML = html;
    }

    // --- Tab 6: Diagnostics & Recovery ---
    renderDiagnostics(result) {
        if (!result) return;

        // Diagnostics List
        if (result.diagnostics.length === 0) {
            this.diagnosticsList.innerHTML = `
                <div class="clean-state-card">
                    <div class="clean-icon-large">✓</div>
                    <h4>Zero Semantic Errors</h4>
                    <p>Program adheres to all lexical scoping rules and static type constraints.</p>
                </div>
            `;
        } else {
            let diagHtml = '';
            result.diagnostics.forEach(diag => {
                const isError = diag.severity === 'ERROR';
                diagHtml += `
                    <div class="diagnostic-card ${isError ? 'card-error' : 'card-warning'}" onclick="window.scopeLabApp.ui.highlightEditorLine(${diag.line})">
                        <div class="diag-header-bar">
                            <span class="badge badge-${diag.severity.toLowerCase()}">${diag.severity}</span>
                            <span class="diag-line-badge">Line ${diag.line}:${diag.column}</span>
                            <span class="diag-category-badge">${diag.category}</span>
                            <button class="btn btn-xs btn-ghost ml-auto">Jump to Line ↗</button>
                        </div>
                        <div class="diag-main-content">
                            <h4 class="diag-heading">${this.escapeHtml(diag.title)}</h4>
                            <p class="diag-msg">${this.escapeHtml(diag.message)}</p>

                            ${diag.declaredInScope ? `
                                <div class="diag-scope-context-box">
                                    <div class="context-item">
                                        <span class="ctx-lbl">Declared in:</span>
                                        <span class="ctx-val">${this.escapeHtml(diag.declaredInScope)}</span>
                                    </div>
                                    <div class="context-item">
                                        <span class="ctx-lbl">Used in:</span>
                                        <span class="ctx-val">${this.escapeHtml(diag.usedInScope || 'Current Scope')}</span>
                                    </div>
                                </div>
                            ` : ''}

                            ${diag.recoveryTechnique ? `
                                <div class="diag-recovery-action">
                                    <strong>Recovery Applied:</strong> ${this.escapeHtml(diag.recoveryTechnique)}
                                </div>
                            ` : ''}

                            ${diag.suggestedFix ? `
                                <div class="diag-fix-suggestion">
                                    <strong>Suggested Fix:</strong> ${this.escapeHtml(diag.suggestedFix)}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            this.diagnosticsList.innerHTML = diagHtml;
        }

        // Recovery Events List
        if (result.recoveryEvents && result.recoveryEvents.length > 0) {
            let recHtml = '';
            result.recoveryEvents.forEach(ev => {
                recHtml += `
                    <div class="recovery-event-card">
                        <div class="rec-header">
                            <span class="badge badge-neutral">${ev.technique}</span>
                            <span class="rec-time font-mono">Line ${ev.line}:${ev.column}</span>
                        </div>
                        <div class="rec-title"><strong>${this.escapeHtml(ev.title)}</strong></div>
                        <p class="rec-desc text-sm text-muted">${this.escapeHtml(ev.description)}</p>
                        <div class="rec-action-box font-mono text-xs mt-4">
                            ↳ ${this.escapeHtml(ev.actionTaken)}
                        </div>
                    </div>
                `;
            });
            this.recoveryList.innerHTML = recHtml;
        } else {
            this.recoveryList.innerHTML = `<p class="text-muted text-sm p-12">No parsing synchronization or phrase-level corrections were needed.</p>`;
        }
    }

    // --- Tab 7: Educational Explanation & Viva ---
    renderEducationalExplanation(result) {
        const scopeErrors = result.diagnostics.filter(d => d.category === 'Scope Error');
        const hasScopeViolation = scopeErrors.length > 0;
        const errVar = hasScopeViolation ? (scopeErrors[0].symbolName || 'y') : 'y';

        let html = `
            <div class="viva-guide-container">
                <div class="explanation-hero">
                    <h3 class="font-bold text-lg">Compiler Analysis Explanation: What Happened?</h3>
                    <p class="text-muted mt-4">
                        A detailed breakdown of lexical scoping rules, symbol table lookups, and memory management for this compilation run.
                    </p>
                </div>

                ${hasScopeViolation ? `
                    <div class="explanation-box-featured mt-16">
                        <div class="feature-badge">Core Scope Violation Analysis</div>
                        <h4 class="text-base font-bold mt-8">Why is variable '<code>${errVar}</code>' out of scope?</h4>
                        <div class="explanation-paragraphs text-sm leading-relaxed mt-8">
                            <p>1. <strong>Block Lifetime:</strong> In block-structured languages (like C, C++, and Java), an inner block <code>{ ... }</code> creates a distinct child scope.</p>
                            <p class="mt-4">2. <strong>Lexical De-allocation:</strong> When the parser leaves the closing brace <code>}</code> at line 10, the inner block scope is exited. The activation frame for that block is popped, and its local symbols (<code>${errVar}</code>, <code>z</code>) are removed from the active lookup chain.</p>
                            <p class="mt-4">3. <strong>Return Statement Lookup:</strong> The statement <code>return x + ${errVar};</code> is located at line 12 in the enclosing function <code>calculate()</code>. When resolving <code>${errVar}</code>, the compiler searches:</p>
                            <div class="lookup-trace-mini font-mono mt-8 mb-8">
                                calculate() Scope (Level 1) → Not Found<br>
                                &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
                                Global Scope (Level 0) → Not Found<br>
                                &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
                                Error: '${errVar}' was declared in closed Block Scope (Level 2) and is inaccessible.
                            </div>
                            <p>4. <strong>Suggested Resolution:</strong> If <code>${errVar}</code> is required in the function return statement, declare <code>int ${errVar};</code> in the <code>calculate()</code> scope before the nested block.</p>
                        </div>
                    </div>
                ` : `
                    <div class="explanation-box-featured mt-16">
                        <div class="feature-badge">Clean Scope Analysis</div>
                        <h4 class="text-base font-bold mt-8">Valid Scope Hierarchy & Variable Shadowing</h4>
                        <p class="text-sm mt-4 text-muted">All variable references in the current program successfully resolved along the static lexical ancestor chain without scope leaks or type violations.</p>
                    </div>
                `}

                <div class="viva-questions-section mt-24">
                    <h3 class="section-title text-base font-bold mb-12">Compiler Design Viva Questions & Concepts</h3>
                    <div class="qa-cards-grid">
                        <div class="qa-card">
                            <div class="qa-q">Q1: What is the difference between Static (Lexical) Scoping and Dynamic Scoping?</div>
                            <div class="qa-a">
                                <strong>Static/Lexical Scoping:</strong> Variable bindings are determined at compile time based purely on the spatial nesting of code blocks in the source text. (Implemented by ScopeLab).<br>
                                <strong>Dynamic Scoping:</strong> Variable bindings are resolved at runtime based on the most recent active call stack frame.
                            </div>
                        </div>

                        <div class="qa-card">
                            <div class="qa-q">Q2: How does a compiler implement Nested Symbol Tables?</div>
                            <div class="qa-a">
                                Typically using a <strong>Tree of Hash Tables</strong> or a <strong>Leveled Scope Stack</strong>. Each scope node maintains a hash map of local identifiers and a pointer to its enclosing <code>parent</code> scope. Lookups start at the current active scope pointer and traverse upward to the root (Global).
                            </div>
                        </div>

                        <div class="qa-card">
                            <div class="qa-q">Q3: What is Variable Shadowing?</div>
                            <div class="qa-a">
                                When a variable declared within an inner scope has the exact same name as a variable in an outer scope. The inner declaration temporarily hides/shadows the outer variable for the duration of the inner scope's lifetime.
                            </div>
                        </div>

                        <div class="qa-card">
                            <div class="qa-q">Q4: What is the difference between Panic Mode and Phrase-Level Recovery?</div>
                            <div class="qa-a">
                                <strong>Panic Mode:</strong> Discards incoming tokens until a synchronization token (e.g., <code>;</code>, <code>}</code>) is found to re-align the parser.<br>
                                <strong>Phrase-Level:</strong> Performs small local repairs, such as inserting a virtual semicolon or replacing a bad token with a valid placeholder to preserve AST integrity.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.explanationContent.innerHTML = html;
    }

    generateAsciiTree(scope, prefix = '', isLast = true) {
        if (!scope) return '';
        let str = prefix + (prefix === '' ? '' : (isLast ? '└── ' : '├── ')) + `${scope.name} (Level ${scope.level})\n`;
        const children = scope.children || [];
        for (let i = 0; i < children.length; i++) {
            const child = children[i];
            const childIsLast = i === children.length - 1;
            const newPrefix = prefix + (prefix === '' ? '' : (isLast ? '    ' : '│   '));
            str += this.generateAsciiTree(child, newPrefix, childIsLast);
        }
        return str;
    }

    escapeHtml(text) {
        if (text === null || text === undefined) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}
