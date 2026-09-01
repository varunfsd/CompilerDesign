/**
 * Source Code Editor Management (Line numbers, tab key, cursor tracker)
 */

class EditorManager {
    constructor() {
        this.textarea = document.getElementById("codeEditor");
        this.lineNumbers = document.getElementById("lineNumbers");
        this.cursorStatus = document.getElementById("cursorPosition");
        this.init();
    }

    init() {
        if (!this.textarea) return;

        // Line numbers sync
        this.textarea.addEventListener("input", () => this.updateLineNumbers());
        this.textarea.addEventListener("scroll", () => this.syncScroll());

        // Tab key support & auto-indent
        this.textarea.addEventListener("keydown", (e) => this.handleKeyDown(e));

        // Cursor position tracking
        this.textarea.addEventListener("keyup", () => this.updateCursorPosition());
        this.textarea.addEventListener("click", () => this.updateCursorPosition());

        this.updateLineNumbers();
    }

    updateLineNumbers() {
        const lines = this.textarea.value.split("\n");
        const count = lines.length || 1;
        let numbersHtml = "";
        for (let i = 1; i <= count; i++) {
            numbersHtml += `${i}\n`;
        }
        this.lineNumbers.textContent = numbersHtml;
    }

    syncScroll() {
        this.lineNumbers.scrollTop = this.textarea.scrollTop;
    }

    updateCursorPosition() {
        const text = this.textarea.value.substring(0, this.textarea.selectionStart);
        const lines = text.split("\n");
        const curLine = lines.length;
        const curCol = lines[lines.length - 1].length + 1;
        this.cursorStatus.textContent = `Ln ${curLine}, Col ${curCol}`;
    }

    handleKeyDown(e) {
        if (e.key === "Tab") {
            e.preventDefault();
            const start = this.textarea.selectionStart;
            const end = this.textarea.selectionEnd;

            // Insert 4 spaces
            this.textarea.value = this.textarea.value.substring(0, start) + "    " + this.textarea.value.substring(end);
            this.textarea.selectionStart = this.textarea.selectionEnd = start + 4;
            this.updateLineNumbers();
            this.updateCursorPosition();
        }
    }

    getValue() {
        return this.textarea.value;
    }

    setValue(code) {
        this.textarea.value = code;
        this.updateLineNumbers();
        this.updateCursorPosition();
    }

    clear() {
        this.setValue("");
    }
}

window.EditorManager = EditorManager;
