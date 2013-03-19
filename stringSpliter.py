import sys

def stringSpliter(string, numChar):
    i      = 0
    pieces = []
    
    while i < len(string):
        pieces.append(string[i:i+numChar])
        i += numChar
        
    return pieces


if __name__ == '__main__':
    print stringSpliter(sys.argv[1], 5)