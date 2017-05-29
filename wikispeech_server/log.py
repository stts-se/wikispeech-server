import sys

log_level = "error"

def log(level, msg):

    levels = ["debug", "info", "warning", "error", "fatal"]
    if level in levels:
        l = levels.index(level)
    else:
        raise ValueError("Level %s not in %s" % (level, levels))

    if log_level in levels:
        ll = levels.index(log_level)
    else:
        raise ValueError("Level %s not in %s" % (log_level, levels))

        
    if l >= ll:
        print(msg)

def debug(msg):
    log("debug","DEBUG: "+str(msg))

def info(msg):
    log("info","INFO: "+str(msg))

def warn(msg):
    log("warning","WARNING: "+str(msg))

def error(msg):
    log("error", "ERROR: "+str(msg))

def fatal(msg):
    log("fatal", "FATAL: "+str(msg))
    sys.exit(1)
