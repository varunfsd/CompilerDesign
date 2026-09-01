/**
 * ScopeLab - Token Definitions and Types
 */

export const TokenType = {
    // Keywords
    KEYWORD: 'KEYWORD',
    TYPE: 'TYPE',

    // Identifiers & Literals
    IDENTIFIER: 'IDENTIFIER',
    INT_LITERAL: 'INT_LITERAL',
    FLOAT_LITERAL: 'FLOAT_LITERAL',
    STRING_LITERAL: 'STRING_LITERAL',

    // Operators
    OPERATOR: 'OPERATOR',

    // Delimiters
    DELIMITER: 'DELIMITER',

    // Special
    EOF: 'EOF',
    UNKNOWN: 'UNKNOWN'
};

export const KEYWORDS = new Set([
    'global',
    'function',
    'procedure',
    'return',
    'print',
    'if',
    'else',
    'while',
    'for'
]);

export const TYPE_KEYWORDS = new Set([
    'int',
    'float',
    'string',
    'void'
]);

export class Token {
    constructor(type, value, line, column, category = '') {
        this.type = type;
        this.value = value;
        this.line = line;
        this.column = column;
        this.category = category || type.toLowerCase();
    }

    toString() {
        return `[Line ${this.line}:${this.column}] ${this.type} ('${this.value}')`;
    }
}
