generate:
	python3 src/main.py -generate

train:
	python3 src/main.py -train

test:
	python3 src/main.py -test

generate-train:
	python3 src/main.py -generate -train

generate-test:
	python3 src/main.py -generate -test
