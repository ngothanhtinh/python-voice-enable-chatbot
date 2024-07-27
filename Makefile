install:
	#install
	python.exe -m pip install --upgrade pip && \
		pip install --upgrade wheel && \
			pip install -r requirements.txt
		