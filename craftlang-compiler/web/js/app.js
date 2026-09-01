/**
 * Main Application Orchestrator for CraftLang Compiler Workbench.
 */

document.addEventListener("DOMContentLoaded", () => {
    const editor = new EditorManager();
    const visualizer = new VisualizerManager();

    // DOM Elements
    const exampleSelect = document.getElementById("exampleSelect");
    const btnCompile = document.getElementById("btnCompile");
    const btnRun = document.getElementById("btnRun");
    const btnClear = document.getElementById("btnClear");
    const diagnosticsBar = document.getElementById("diagnosticsBar");
    const diagSeverityBadge = document.getElementById("diagSeverityBadge");
    const diagStage = document.getElementById("diagStage");
    const diagLocation = document.getElementById("diagLocation");
    const diagMessage = document.getElementById("diagMessage");

    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    // AST View Toggles
    const btnAstDiagramView = document.getElementById("btnAstDiagramView");
    const btnAstJsonView = document.getElementById("btnAstJsonView");
    const astDiagramContainer = document.getElementById("astDiagramContainer");
    const astJsonContainer = document.getElementById("astJsonContainer");
    const astJsonOutput = document.getElementById("astJsonOutput");

    // Codegen Toggles
    const btnShowLLVM = document.getElementById("btnShowLLVM");
    const btnShowAsm = document.getElementById("btnShowAsm");
    const llvmView = document.getElementById("llvmView");
    const asmView = document.getElementById("asmView");
    const llvmOutput = document.getElementById("llvmOutput");
    const asmOutput = document.getElementById("asmOutput");
    const btnCopyCodegen = document.getElementById("btnCopyCodegen");

    // Console & Metrics
    const consoleOutput = document.getElementById("consoleOutput");
    const execStatus = document.getElementById("execStatus");
    const execSteps = document.getElementById("execSteps");
    const compileTime = document.getElementById("compileTime");
    const btnClearConsole = document.getElementById("btnClearConsole");

    // CFG Accordion
    const cfgToggle = document.getElementById("cfgToggle");
    const cfgBody = document.getElementById("cfgBody");

    let currentExamples = [];
    let latestCompilationResult = null;

    // -------------------------------------------------------------
    // Initialization
    // -------------------------------------------------------------
    async function init() {
        setupTabs();
        setupEvents();
        await loadExamples();
    }

    // -------------------------------------------------------------
    // Tab Management
    // -------------------------------------------------------------
    function setupTabs() {
        tabButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-tab");

                tabButtons.forEach(b => b.classList.remove("active"));
                tabPanes.forEach(p => p.classList.remove("active"));

                btn.classList.add("active");
                const pane = document.getElementById(targetTab);
                if (pane) pane.classList.add("active");
            });
        });
    }

    function switchToTab(tabId) {
        const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
        if (btn) btn.click();
    }

    // -------------------------------------------------------------
    // Examples Loading
    // -------------------------------------------------------------
    async function loadExamples() {
        try {
            const resp = await fetch("/api/examples");
            const data = await resp.json();
            currentExamples = data.examples || [];

            exampleSelect.innerHTML = currentExamples.map((ex, i) => `
                <option value="${ex.id}">${ex.title}</option>
            `).join("");

            if (currentExamples.length > 0) {
                exampleSelect.value = currentExamples[0].id;
                editor.setValue(currentExamples[0].code);
                // Trigger initial auto-compilation
                await handleCompile(true);
            }
        } catch (err) {
            console.error("Failed to load preset examples:", err);
            exampleSelect.innerHTML = `<option value="">Default Example</option>`;
        }
    }

    // -------------------------------------------------------------
    // Event Handlers Setup
    // -------------------------------------------------------------
    function setupEvents() {
        // Preset example change
        exampleSelect.addEventListener("change", () => {
            const selected = currentExamples.find(e => e.id === exampleSelect.value);
            if (selected) {
                editor.setValue(selected.code);
                handleCompile(true);
            }
        });

        // Action Buttons
        btnCompile.addEventListener("click", () => handleCompile(false));
        btnRun.addEventListener("click", () => handleCompile(true));
        btnClear.addEventListener("click", () => {
            editor.clear();
            hideDiagnostics();
            clearResults();
        });

        // AST view switcher
        btnAstDiagramView.addEventListener("click", () => {
            btnAstDiagramView.classList.add("btn-active");
            btnAstJsonView.classList.remove("btn-active");
            astDiagramContainer.classList.remove("hidden");
            astJsonContainer.classList.add("hidden");
        });

        btnAstJsonView.addEventListener("click", () => {
            btnAstJsonView.classList.add("btn-active");
            btnAstDiagramView.classList.remove("btn-active");
            astJsonContainer.classList.remove("hidden");
            astDiagramContainer.classList.add("hidden");
        });

        // Codegen switcher
        btnShowLLVM.addEventListener("click", () => {
            btnShowLLVM.classList.add("btn-active");
            btnShowAsm.classList.remove("btn-active");
            llvmView.classList.remove("hidden");
            asmView.classList.add("hidden");
        });

        btnShowAsm.addEventListener("click", () => {
            btnShowAsm.classList.add("btn-active");
            btnShowLLVM.classList.remove("btn-active");
            asmView.classList.remove("hidden");
            llvmView.classList.add("hidden");
        });

        // Copy Codegen
        btnCopyCodegen.addEventListener("click", () => {
            const isLLVM = !llvmView.classList.contains("hidden");
            const textToCopy = isLLVM ? llvmOutput.textContent : asmOutput.textContent;
            navigator.clipboard.writeText(textToCopy);
            btnCopyCodegen.textContent = "Copied!";
            setTimeout(() => btnCopyCodegen.textContent = "Copy Target Code", 1500);
        });

        // CFG Accordion toggle
        cfgToggle.addEventListener("click", () => {
            cfgBody.classList.toggle("hidden");
            const icon = cfgToggle.querySelector(".accordion-icon");
            if (icon) icon.textContent = cfgBody.classList.contains("hidden") ? "▶" : "▼";
        });

        // Clear console
        btnClearConsole.addEventListener("click", () => {
            consoleOutput.textContent = "";
        });
    }

    // -------------------------------------------------------------
    // Compilation & Execution Pipeline Caller
    // -------------------------------------------------------------
    async function handleCompile(executeInVM = true) {
        const source = editor.getValue();
        if (!source.trim()) {
            showDiagnostic({
                severity: "WARNING",
                stage: "Editor",
                line: 1,
                column: 1,
                formatted: "Source code editor is empty. Please enter CraftLang source code."
            });
            return;
        }

        btnCompile.disabled = true;
        btnRun.disabled = true;

        try {
            const resp = await fetch("/api/compile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ source: source, execute: executeInVM })
            });

            const result = await resp.json();
            latestCompilationResult = result;

            if (result.success) {
                hideDiagnostics();
                displayCompilationResults(result, executeInVM);
            } else {
                displayErrors(result.diagnostics);
            }
        } catch (err) {
            console.error("API error during compilation:", err);
            showDiagnostic({
                severity: "FATAL",
                stage: "Network / Server",
                line: 1,
                column: 1,
                formatted: `Failed to communicate with compiler backend: ${err.message}`
            });
        } finally {
            btnCompile.disabled = false;
            btnRun.disabled = false;
        }
    }

    // -------------------------------------------------------------
    // Rendering Results across all tabs
    // -------------------------------------------------------------
    function displayCompilationResults(result, executed) {
        // 1. Tokens
        visualizer.renderTokens(result.tokens);

        // 2. AST Diagram & JSON
        visualizer.renderMermaid("astMermaidOutput", result.ast_mermaid);
        astJsonOutput.textContent = JSON.stringify(result.ast_json, null, 2);

        // 3. Symbol Table
        visualizer.renderSymbols(result.symbols_flat);

        // 4. Three-Address Code
        document.getElementById("rawTacOutput").textContent = result.tac_raw_text || "// No TAC generated";
        document.getElementById("optTacOutput").textContent = result.tac_optimized_text || "// No optimized TAC";
        document.getElementById("rawTacCount").textContent = `${result.tac_raw.length} insts`;
        document.getElementById("optTacCount").textContent = `${result.tac_optimized.length} insts`;
        visualizer.renderMermaid("cfgMermaidOutput", result.cfg_optimized_mermaid || result.cfg_raw_mermaid);

        // 5. Optimization Passes Timeline
        visualizer.renderOptimizations(result.optimization_steps);

        // 6. Codegen (LLVM & Assembly)
        llvmOutput.textContent = result.llvm_ir || "; No LLVM IR";
        asmOutput.textContent = result.assembly || "# No Assembly";

        // 7. Console & Runtime Output
        compileTime.textContent = `${result.compilation_time_ms} ms`;

        if (result.execution_result) {
            const exec = result.execution_result;
            execSteps.textContent = `${exec.steps_executed}`;
            if (exec.success) {
                execStatus.textContent = "Success";
                execStatus.className = "metric-value badge-success";
                consoleOutput.textContent = exec.output || "(Program exited cleanly with no output)";
            } else {
                execStatus.textContent = "Runtime Error";
                execStatus.className = "metric-value badge-error";
                consoleOutput.textContent = `[Runtime Error]: ${exec.error_message}\n\nStdout so far:\n${exec.output}`;
            }
            visualizer.renderMemory(exec.final_variables);
            if (executed) {
                switchToTab("tab-console");
            }
        }
    }

    function displayErrors(diagnostics) {
        if (!diagnostics || diagnostics.length === 0) return;
        const diag = diagnostics[0];
        showDiagnostic(diag);
    }

    function showDiagnostic(diag) {
        diagnosticsBar.classList.remove("hidden");
        diagSeverityBadge.textContent = diag.severity || "ERROR";
        diagSeverityBadge.className = `badge ${diag.severity === 'WARNING' ? '' : 'badge-error'}`;
        diagStage.textContent = diag.stage || "Compiler";
        diagLocation.textContent = `Line ${diag.line || 1}, Col ${diag.column || 1}`;
        diagMessage.textContent = diag.formatted || diag.message || "Unknown error";
    }

    function hideDiagnostics() {
        diagnosticsBar.classList.add("hidden");
    }

    function clearResults() {
        visualizer.renderTokens([]);
        visualizer.renderSymbols([]);
        visualizer.renderOptimizations([]);
        visualizer.renderMemory({});
        document.getElementById("rawTacOutput").textContent = "";
        document.getElementById("optTacOutput").textContent = "";
        llvmOutput.textContent = "";
        asmOutput.textContent = "";
        consoleOutput.textContent = "Press 'Run Program' or 'Compile' to start.";
    }

    init();
});
