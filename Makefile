test:
	pytest

load:
	python src/etl/loader.py

clean:
	python -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"