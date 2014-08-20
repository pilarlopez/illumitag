## Illumitag

The moniker "Illumitag" stands environmental sequence tags performed on the Illumina technology.

This project is a pipeline for 16S rRNA Illumina paired-end amplicon sequencing used in the Limnology department at the Evolution Biology Center of Uppsala University. Publication submitted.

Unfortunately, in the meantime, no other detailed documentation has been written yet but the code is clean and commented. In addition these three descriptive files might help you figure out what is going on:

* documentation/experiment_outline.pdf
* documentation/objects_diagram.pdf
* documentation/pipeline_outline.pdf

## Installing
No automated installation has been developed for the illumitag package.
But following this document and typing these commands on your bash prompt should get you started.
If you cannot get a functional installation set up, contact the authors.

### Step 1: Cloning the repository
Here you will download a copy of the code from github and place it in your home directory.

    $ cd ~
    $ mkdir repos
    $ cd repos
    $ git clone git@github.com:limno/illumitag.git

### Step 2: Modify your search paths
Here you will edit your ``.bashrc`` or ``.bash_profile`` to add a reference to the code you just downloaded.

    $ vim ~/.bash_profile
    export PYTHONPATH="$HOME/repos/illumitag/":$PYTHONPATH

### Step 3: Install your own version of python
Your system probably comes with a version of python installed. But the variations from system to system are too great to rely on any available python. We prefer to just install our own in the home directory.

For this we will be using this excellent project: https://github.com/yyuu/pyenv

To install it you may use this sister project: https://github.com/yyuu/pyenv-installer

Basically you just need to type this command:

    $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

These lines go into your ``.bash_profile``:

    $ vim ~/.bash_profile
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

Relaunch your shell and type these commands to get the right version of python now:

    pyenv install 2.7.6
    pyenv rehash
    pyenv global 2.7.6

### Step 4: Install all required python packages
GEFES uses many third party python libraries. You can get them by running these commands:

    $ pip install sh
    $ pip install decorator
    $ pip install biopython
    $ pip install threadpool
    $ pip install patsy
    $ pip install scipy
    $ pip install matplotlib
    $ pip install pandas
    $ pip install statsmodels
    $ pip install ipython
    $ pip install scikit-learn
    $ pip install rpy2
    $ pip install brewer2mpl
    $ pip install regex
    $ pip install ftputil
    $ pip install names
    $ pip install shell_command
    $ pip install pystache
    $ pip install tabulate
    $ pip install tqdm
    $ pip install scikit-bio==0.1.4

Don't forget to rehash the binary links at the end:

    $ pyenv rehash

### Step 5: Check you have all the required executables

    $ which pandaseq27
    $ which usearch7
    $ which usearch6
    $ which fastqc
    $ which blastn
    $ which classify

### Step 6: Check you have all the required R dependencies

    $ R install 'vegan'

### Step 7: Make a working directory with the raw data linked

    $ cd ~
    $ mkdir ILLUMITAG
    $ cd ILLUMITAG
    $ ln -s /proj/ $HOME/proj

### Step 8: Start typing python commands to analyze your data

    $ cd ~/ILLUMITAG/
    $ ipython -i -c "import illumitag"