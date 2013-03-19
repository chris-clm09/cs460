//////////////////////////////////////////////////////
READ ME
/////////////////////////////////////////////////////

To run a connection test call:
python lab3ConnecitonTest.py

This test requires there to be a file called 'junk.txt',
this file is read and sent over the virtual network.
It is then saved as 'junkN.txt'.

To generate a 'junk.txt' file call:
python junkGenerator.py <number of lines in file>

If you then would like run the following:
./r

This will run the simulation and compare the two files
using diff.  Diff will display if the two files are
different.  If they are it is most likley becuase
a connection faild etc.
