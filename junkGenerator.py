import sys

def generate(num=100):
    aFile = open("junk.txt", "wr")
    
    for i in range(0,num):
        aFile.write(str(i) + "This is another greate line of junk!\n")


if __name__ == '__main__':
    generate(int(sys.argv[1]))
