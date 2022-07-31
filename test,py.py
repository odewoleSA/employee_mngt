B = [10,-5,-1,-1,10]

def solution(A):
    # write your code in Python 3.6
    Alen = len(A) - 1
    for i in A:
        if i < 0:
            A[Alen] = i
        else:
            pass

    return A


solution(B)


Compilation successful.

Example test:   [10, -10, -1, -1, 10]
WRONG ANSWER (got 5 expected 1)

Example test:   [-1, -1, -1, 1, 1, 1, 1]
WRONG ANSWER (got 7 expected 3)

Example test:   [5, -2, -3, 1]
WRONG ANSWER (got 4 expected 0)



# B = [10,-5,-1,-1,10]

def solution(A):
    # write your code in Python 3.6
    Alen = len(A) - 1
    move = 0
    for i in A:
        if i < 0:
            A[Alen] = i
        else:
            pass
        move = move + 1

    return move