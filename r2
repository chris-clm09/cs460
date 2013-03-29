echo "Cleaning Up."
rm log.txt

echo "Compiling/Running Python."
python  lab4ConnectTest2Host.py

OUT=$?
if [ $OUT -eq 0 ];then
# echo "Testing."
# echo "-- Performing Diff --"
# echo "----- Complete ------"
echo "Done."
else
echo "Python Error."
fi
