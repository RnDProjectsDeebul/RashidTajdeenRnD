dataset:
	python3 src/main.py

test:
	behave tests/sample_test.feature

train:
	python3 src/train.py

validate:
	python3 src/validate.py