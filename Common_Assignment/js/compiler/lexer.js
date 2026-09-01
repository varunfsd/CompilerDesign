/**
 * ScopeLab - Lexer (Lexical Analyzer)
 */

import { Token, TokenType, KEYWORDS, TYPE_KEYWORDS } from './tokens.js';

export class Lexer {
    constructor(source) {
        this.source = source || '';
        this.cursor = 0;
        this.line = 1;
        this.column = 1;
        this.tokens = [];
        this.errors = [];
    }

    tokenize() {
        this.tokens = [];
        this.errors = [];
        this.cursor = 0;
        this.line = 1;
        this.column = 1;

        while (!this.isAtEnd()) {
            this.skipWhitespaceAndComments();
            if (this.isAtEnd()) break;

            const char = this.peek();
            const startLine = this.line;
            const startCol = this.column;

            // Numbers (int or float)
            if (this.isDigit(char)) {
                this.readNumber();
            }
            // Strings
            else if (char === '"' || char === "'") {
                this.readString(char);
            }
            // Identifiers / Keywords / Types
            else if (this.isAlpha(char) || char === '_') {
                this.readIdentifierOrKeyword();
            }
            // Operators & Delimiters
            else {
                this.readSymbol();
            }
        }

        this.tokens.push(new Token(TokenType.EOF, '', this.line, this.column, 'special'));
        return {
            tokens: this.tokens,
            errors: this.errors
        };
    }

    isAtEnd() {
        return this.cursor >= this.source.length;
    }

    peek(offset = 0) {
        if (this.cursor + offset >= this.source.length) return '\0';
        return this.source[this.cursor + offset];
    }

    advance() {
        if (this.isAtEnd()) return '\0';
        const char = this.source[this.cursor++];
        if (char === '\n') {
            this.line++;
            this.column = 1;
        } else {
            this.column++;
        }
        return char;
    }

    match(expected) {
        if (this.isAtEnd()) return false;
        if (this.source[this.cursor] !== expected) return false;
        this.advance();
        return true;
    }

    skipWhitespaceAndComments() {
        while (!this.isAtEnd()) {
            const char = this.peek();

            if (char === ' ' || char === '\t' || char === '\r' || char === '\n') {
                this.advance();
            }
            // Single-line comment
            else if (char === '/' && this.peek(1) === '/') {
                this.advance(); // consume '/'
                this.advance(); // consume '/'
                while (!this.isAtEnd() && this.peek() !== '\n') {
                    this.advance();
                }
            }
            // Multi-line comment
            else if (char === '/' && this.peek(1) === '*') {
                this.advance(); // consume '/'
                this.advance(); // consume '*'
                while (!this.isAtEnd()) {
                    if (this.peek() === '*' && this.peek(1) === '/') {
                        this.advance(); // consume '*'
                        this.advance(); // consume '/'
                        break;
                    }
                    this.advance();
                }
            } else {
                break;
            }
        }
    }

    isDigit(char) {
        return char >= '0' && char <= '9';
    }

    isAlpha(char) {
        return (char >= 'a' && char <= 'z') ||
               (char >= 'A' && char <= 'Z');
    }

    isAlphaNumeric(char) {
        return this.isAlpha(char) || this.isDigit(char) || char === '_';
    }

    readNumber() {
        const startLine = this.line;
        const startCol = this.column;
        let numStr = '';
        let isFloat = false;

        while (this.isDigit(this.peek())) {
            numStr += this.advance();
        }

        // Check for fractional part
        if (this.peek() === '.' && this.isDigit(this.peek(1))) {
            isFloat = true;
            numStr += this.advance(); // consume '.'
            while (this.isDigit(this.peek())) {
                numStr += this.advance();
            }
        }

        const type = isFloat ? TokenType.FLOAT_LITERAL : TokenType.INT_LITERAL;
        this.tokens.push(new Token(type, numStr, startLine, startCol, isFloat ? 'float' : 'integer'));
    }

    readString(quoteChar) {
        const startLine = this.line;
        const startCol = this.column;
        this.advance(); // consume opening quote
        let strVal = '';

        while (!this.isAtEnd() && this.peek() !== quoteChar && this.peek() !== '\n') {
            if (this.peek() === '\\') {
                this.advance();
                const escaped = this.advance();
                if (escaped === 'n') strVal += '\n';
                else if (escaped === 't') strVal += '\t';
                else if (escaped === '"') strVal += '"';
                else if (escaped === "'") strVal += "'";
                else strVal += escaped;
            } else {
                strVal += this.advance();
            }
        }

        if (this.peek() === quoteChar) {
            this.advance(); // consume closing quote
            this.tokens.push(new Token(TokenType.STRING_LITERAL, strVal, startLine, startCol, 'string'));
        } else {
            this.errors.push({
                type: 'LEXICAL_ERROR',
                message: `Unterminated string literal starting at line ${startLine}`,
                line: startLine,
                column: startCol
            });
            this.tokens.push(new Token(TokenType.STRING_LITERAL, strVal, startLine, startCol, 'string'));
        }
    }

    readIdentifierOrKeyword() {
        const startLine = this.line;
        const startCol = this.column;
        let word = '';

        while (this.isAlphaNumeric(this.peek())) {
            word += this.advance();
        }

        if (TYPE_KEYWORDS.has(word)) {
            this.tokens.push(new Token(TokenType.TYPE, word, startLine, startCol, 'type'));
        } else if (KEYWORDS.has(word)) {
            this.tokens.push(new Token(TokenType.KEYWORD, word, startLine, startCol, 'keyword'));
        } else {
            this.tokens.push(new Token(TokenType.IDENTIFIER, word, startLine, startCol, 'identifier'));
        }
    }

    readSymbol() {
        const startLine = this.line;
        const startCol = this.column;
        const char = this.advance();

        // 2-character operators
        if (char === '=' && this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.OPERATOR, '==', startLine, startCol, 'operator'));
            return;
        }
        if (char === '!' && this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.OPERATOR, '!=', startLine, startCol, 'operator'));
            return;
        }
        if (char === '<' && this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.OPERATOR, '<=', startLine, startCol, 'operator'));
            return;
        }
        if (char === '>' && this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.OPERATOR, '>=', startLine, startCol, 'operator'));
            return;
        }

        // Single-character operators & delimiters
        switch (char) {
            case '{':
            case '}':
            case '(':
            case ')':
            case ',':
            case ';':
                this.tokens.push(new Token(TokenType.DELIMITER, char, startLine, startCol, 'delimiter'));
                break;
            case '+':
            case '-':
            case '*':
            case '/':
            case '%':
            case '=':
            case '<':
            case '>':
                this.tokens.push(new Token(TokenType.OPERATOR, char, startLine, startCol, 'operator'));
                break;
            default:
                this.errors.push({
                    type: 'LEXICAL_ERROR',
                    message: `Unrecognized character '${char}' at line ${startLine}, column ${startCol}`,
                    line: startLine,
                    column: startCol
                });
                this.tokens.push(new Token(TokenType.UNKNOWN, char, startLine, startCol, 'unknown'));
                break;
        }
    }
}
