echo "Cleaning Up."
rm log.txt
rm junkN.txt

echo "Compiling/Running Python."
python  lab4ConnectTest2Host.py

OUT=$?
if [ $OUT -eq 0 ];then
 echo "Testing."
 echo "-- Performing Diff --"
 diff -q junk.txt junkN.txt
 #gedit log.txt &
 echo "----- Complete ------"
else
echo "Python Error."
fi
