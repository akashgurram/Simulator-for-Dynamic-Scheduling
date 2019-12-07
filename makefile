run: simulator.py
	python3 simulator.py inst.txt data.txt reg.txt config.txt result.txt
	rm -f  *.pyc
	rm -r __pycache__
clean: 
	rm -f  *.pyc
	rm -r __pycache__
