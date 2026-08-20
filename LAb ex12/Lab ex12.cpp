#include <stdio.h>
#include <string.h>

char input[100];
int cursor = 0;

// Production rule function prototypes
int E(void);
int E_prime(void);
int T(void);
int T_prime(void);
int F(void);

// E -> T E'
int E() {
    if (T()) {
        if (E_prime()) return 1;
    }
    return 0;
}

// E' -> + T E' | e
int E_prime() {
    if (input[cursor] == '+') {
        cursor++; // consume '+'
        if (T()) {
            if (E_prime()) return 1;
            return 0;
        }
        return 0;
    }
    return 1; // epsilon transition
}

// T -> F T'
int T() {
    if (F()) {
        if (T_prime()) return 1;
    }
    return 0;
}

// T' -> * F T' | e
int T_prime() {
    if (input[cursor] == '*') {
        cursor++; // consume '*'
        if (F()) {
            if (T_prime()) return 1;
            return 0;
        }
        return 0;
    }
    return 1; // epsilon transition
}

// F -> ( E ) | id
int F() {
    if (input[cursor] == '(') {
        cursor++; // consume '('
        if (E()) {
            if (input[cursor] == ')') {
                cursor++; // consume ')'
                return 1;
            }
        }
        return 0;
    } 
    // Match multi-character identifier 'id'
    else if (input[cursor] == 'i' && input[cursor + 1] == 'd') {
        cursor += 2; 
        return 1;
    } 
    // Match single-character shorthand 'i' as 'id'
    else if (input[cursor] == 'i') {
        cursor++; 
        return 1;
    }
    return 0;
}

int main() {
    printf("Enter the input string: ");
    scanf("%s", input);

    cursor = 0;
    
    // The string is valid if parsing completes and input is entirely consumed
    if (E() && input[cursor] == '\0') {
        printf("Result: String is successfully parsed (Valid)\n");
    } else {
        printf("Result: Syntax Error (Invalid String)\n");
    }

    return 0;
}
