# Built-in modules #
import subprocess, sys

# Required modules #
modules = ['Bio', 'sh', 'patsy', 'pandas', 'statsmodels', 'fastqident', 'rpy2', 'matplotlib', 'threadpool']

# Required executables #
executables = ['pandaseq27', 'usearch7', 'usearch6', 'fastqc']

################################################################################
# We might be missing some executables #
def check_executable(tool_name):
    """Raises an exception if the executable *tool_name* is not found."""
    result = subprocess.call(['which', tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result != 0:
        message = "The executable '%s' cannot be found in your $PATH" % tool_name
        raise Exception(message)

def check_executables():
    for exe in executables: check_executable(exe)

################################################################################
# We might be missing some modules #
def check_module(mod_name):
    """Raises an exception if the module *mod_name* is not found."""
    try:
        __import__(mod_name)
    except ImportError as e:
        if str(e) != 'No module named %s' % mod_name: raise e
        print 'You do not seem to have the "%s" package properly installed.' \
              ' Either you never installed it or your $PYTHONPATH is not set up correctly.' \
              ' For more instructions see the README file. (%s)' % (mod_name, e)
        sys.exit()

def check_modules():
    for mod_name in modules: check_module(mod_name)
