export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

. venv/bin/activate

python list_generator.py
python index_generator.py
python queries_processor.py
python search_runner.py