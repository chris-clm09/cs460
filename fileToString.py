import sys

def fileToString(afile):
    with open (afile, "r") as myfile:
        data=myfile.read()
        return str(data)
    
    
if __name__ == '__main__':
    print 'Printing: ', sys.argv[1]
    print fileToString(sys.argv[1])