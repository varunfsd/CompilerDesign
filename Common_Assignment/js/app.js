/**
 * ScopeLab - Main Application Entry Point
 */

import { Lexer } from './compiler/lexer.js';
import { Parser } from './compiler/parser.js';
import { RecoveryManager } from './compiler/errorRecovery.js';
import { ScopeManager } from './compiler/scope.js';
import { SymbolTable } from './compiler/symbolTable.js';
import { SemanticAnalyzer } from './compiler/semanticAnalyzer.js';
import { PRESETS } from './presets.js';
import { UIController } from './ui.js';

export class ScopeLabApp {
    constructor() {
        this.ui = new UIController();
        this.recoveryManager = new RecoveryManager();
        this.scopeManager = new ScopeManager();
        this.symbolTable = new SymbolTable();
        this.analyzer = new SemanticAnalyzer(this.scopeManager, this.symbolTable, this.recoveryManager);
    }

    init() {
        this.ui.init();
        this.populatePresets();
        this.bindEvents();

        // Load default example & auto-run analysis
        this.loadPreset('default_scope_violation');
        this.runAnalysis();
    }

    populatePresets() {
        if (!this.ui.presetSelect) return;
        let optionsHtml = '';
        PRESETS.forEach(p => {
            optionsHtml += `<option value="${p.id}">${p.name}</option>`;
        });
        this.ui.presetSelect.innerHTML = optionsHtml;
    }

    bindEvents() {
        // Analyze Button
        if (this.ui.btnAnalyze) {
            this.ui.btnAnalyze.addEventListener('click', () => {
                this.runAnalysis();
            });
        }

        // Reset Button
        if (this.ui.btnReset) {
            this.ui.btnReset.addEventListener('click', () => {
                const currentPresetId = this.ui.presetSelect.value || 'default_scope_violation';
                this.loadPreset(currentPresetId);
                this.runAnalysis();
            });
        }

        // Clear Button
        if (this.ui.btnClear) {
            this.ui.btnClear.addEventListener('click', () => {
                this.ui.sourceEditor.value = '';
                this.ui.updateLineNumbers();
                this.runAnalysis();
            });
        }

        // Preset Change
        if (this.ui.presetSelect) {
            this.ui.presetSelect.addEventListener('change', (e) => {
                this.loadPreset(e.target.value);
                this.runAnalysis();
            });
        }

        // Keyboard Shortcut: Ctrl+Enter / Cmd+Enter to Analyze
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.runAnalysis();
            }
        });
    }

    loadPreset(presetId) {
        const preset = PRESETS.find(p => p.id === presetId) || PRESETS[0];
        if (preset && this.ui.sourceEditor) {
            this.ui.sourceEditor.value = preset.code;
            this.ui.presetSelect.value = preset.id;
            this.ui.updateLineNumbers();
        }
    }

    runAnalysis() {
        const sourceCode = this.ui.sourceEditor.value;

        // Reset recovery manager
        this.recoveryManager.reset();

        // 1. Lexical Analysis
        const lexer = new Lexer(sourceCode);
        const lexResult = lexer.tokenize();

        // Merge lexical errors into recovery events if any
        lexResult.errors.forEach(err => {
            this.recoveryManager.recordPanicMode(
                'Lexical Scanner Error',
                err.message,
                err.line,
                err.column,
                'token boundary',
                1
            );
        });

        // 2. Parsing & AST Construction
        const parser = new Parser(lexResult.tokens, this.recoveryManager);
        const parseResult = parser.parse();

        // 3. Semantic Analysis & Symbol Table Generation
        const semanticResult = this.analyzer.analyze(parseResult.ast);

        // Merge parser syntax errors into diagnostics list
        parseResult.syntaxErrors.forEach(err => {
            semanticResult.diagnostics.unshift({
                severity: err.type === 'SYNTAX_WARNING' ? 'WARNING' : 'ERROR',
                category: 'Syntax Error',
                title: 'Syntax Error',
                message: err.message,
                line: err.line,
                column: err.column,
                recoveryTechnique: 'Phrase-Level / Panic Mode recovery active.'
            });
        });

        // 4. Render to UI
        this.ui.renderAll(semanticResult, lexResult.tokens);
    }
}

// Instantiate on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.scopeLabApp = new ScopeLabApp();
    window.scopeLabApp.init();
});
