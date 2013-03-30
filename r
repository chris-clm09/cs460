echo "Cleaning Up."
rm log.txt
rm junkN.txt
rm junk125.225.53.1P*

echo "Compiling Python."
python lab3ConnectText.py

OUT=$?
if [ $OUT -eq 0 ];then
 echo "Testing."
 echo "-- Performing Diff --"
 #diff -q junk.txt junkN.txt
 find . -name "junk125.225.53.1P*"| xargs diff -q --to-file=junk.txt
 #gedit log.txt &
 echo "----- Complete ------"
else
echo "Python Error."
fi
