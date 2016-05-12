import os,sys
def multiply(n):
    if n==0 or n==1:
        return 1
    return n*multiply(n-1)


def add(n):
    if n<=0:
        return 0
    if n>0:
        return n+add(n-1)
if __name__=="__main__":
    input =  raw_input("enter number:\n") or "Jack"
    print input