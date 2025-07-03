#include <stdio.h>

int main() {
    int i, n;

    int t1 = 0, t2 = 1;

    int n_term = t1 + t2;
    n = 10;
    for (i = 3; i <= n; i++) {
        t1 = t2;
        t2 = n_term;
        n_term = t1 + t2;
    }

    return t2;
}