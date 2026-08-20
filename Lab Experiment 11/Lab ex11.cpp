#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX 50

struct Symbol {
    char name[30];
    char type[20];  // e.g., int, float, char
    int address;
} table[MAX];

int count = 0;

// Search for a symbol by name
int search(char name[]) {
    for (int i = 0; i < count; i++) {
        if (strcmp(table[i].name, name) == 0) {
            return i; // Found
        }
    }
    return -1; // Not found
}

// Insert a new symbol into the table
void insert() {
    if (count >= MAX) {
        printf("Error: Symbol Table is full!\n");
        return;
    }

    char name[30], type[20];
    int address;

    printf("Enter Symbol Name: ");
    scanf("%s", name);

    if (search(name) != -1) {
        printf("Error: Symbol '%s' already exists in the symbol table!\n", name);
        return;
    }

    printf("Enter Data Type (e.g., int, float): ");
    scanf("%s", type);
    printf("Enter Memory Address: ");
    scanf("%d", &address);

    strcpy(table[count].name, name);
    strcpy(table[count].type, type);
    table[count].address = address;
    count++;

    printf("Symbol added successfully!\n");
}

// Display all symbols
void display() {
    if (count == 0) {
        printf("\nSymbol Table is empty!\n");
        return;
    }

    printf("\n-----------------------------------------\n");
    printf("| %-12s | %-10s | %-8s |\n", "Symbol Name", "Data Type", "Address");
    printf("-----------------------------------------\n");
    for (int i = 0; i < count; i++) {
        printf("| %-12s | %-10s | %-8d |\n", table[i].name, table[i].type, table[i].address);
    }
    printf("-----------------------------------------\n");
}

// Search operation wrapper
void search_symbol() {
    char name[30];
    printf("Enter Symbol Name to Search: ");
    scanf("%s", name);

    int idx = search(name);
    if (idx != -1) {
        printf("Symbol Found -> Name: %s | Type: %s | Address: %d\n", 
               table[idx].name, table[idx].type, table[idx].address);
    } else {
        printf("Symbol '%s' not found!\n", name);
    }
}

// Modify an existing symbol
void modify() {
    char name[30];
    printf("Enter Symbol Name to Modify: ");
    scanf("%s", name);

    int idx = search(name);
    if (idx == -1) {
        printf("Symbol '%s' not found!\n", name);
        return;
    }

    printf("Enter New Data Type: ");
    scanf("%s", table[idx].type);
    printf("Enter New Address: ");
    scanf("%d", &table[idx].address);

    printf("Symbol updated successfully!\n");
}

int main() {
    int choice;

    while (1) {
        printf("\n=== SYMBOL TABLE OPERATIONS ===\n");
        printf("1. Insert Symbol\n");
        printf("2. Display Table\n");
        printf("3. Search Symbol\n");
        printf("4. Modify Symbol\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1: insert(); break;
            case 2: display(); break;
            case 3: search_symbol(); break;
            case 4: modify(); break;
            case 5: exit(0);
            default: printf("Invalid choice! Try again.\n");
        }
    }

    return 0;
}
