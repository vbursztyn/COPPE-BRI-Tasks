#1. Task 2: BASIC 4-MODULE SEARCH ENGINE + OPTIONAL STEMMING + EVALUATOR MODULE
Author: Victor S. Bursztyn (vbursztyn@cos.ufrj.br | vsb@poli.ufrj.br | vbursztyn@gmail.com).

#2. Requirements:

I. To have Python's Virtualenv installed. In case it is not, you need to comment line 4 (". venv/bin/activate") of BATCH_RUN.sh in order to perform it. Also, all required libs shall be installed alternatively (refer to requirement III).

II. To create a standard Virtualenv called "venv" at this location. Once Virtualenv is installed, you can do it by simply calling in command line, from this project's folder: "virtualenv venv".

III. To install all required libs. Right after requirement II, enter in command line: ". venv/bin/activate". Then install all dependencies by calling: "pip install -r requirements.txt". Make sure to be connected to the internet, and that it finishes successfully.

#3. Execution possibilities:

I. Performing "bash BATCH_RUN.sh" will subsequently a) enter local virtual environment; b) call 1_list_generator.py; c) call 2_index_generator.py; d) call 3_queries_processor.py; and e) call 4_search_runner.py. Feel free to edit *.CFG file in case you need to reconfigure any modules.

II. Also, you can reset results by calling "bash BATCH_RESET.sh".

III. Finally, you can call "bash BATCH_EVAL.sh" to perform all evaluation methods. This particular module displays its results on standard output.