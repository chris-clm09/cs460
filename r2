echo "Cleaning Up."
rm log.txt

echo "Compiling/Running Python."
python  lab4ConnectTest2Host.py

OUT=$?
if [ $OUT -eq 0 ];then
 echo "Testing."
 echo "-- Performing Diff --"
 find . -name "junk125.225.53.1P*"| xargs diff -q --to-file=junk.txt
 echo "----- Complete ------"
echo "Done."
else
echo "Python Error."
fi
