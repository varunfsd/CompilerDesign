#include <stdio.h>

int main() {
    printf("Grammar:\n");
    printf("S -> AaAb | BbBa\n");
    printf("A -> e\n");
    printf("B -> e\n\n");

    printf("FIRST(A) = { e }\n");
    printf("FIRST(B) = { e }\n");
    printf("FIRST(S) = { a, b }\n");

    return 0;
}
