import sys
import syslog


logger = "stderr"
log_level = "warning"


level_map = {
    "fatal": syslog.LOG_CRIT,
    "error": syslog.LOG_ERR,
    "warning": syslog.LOG_WARNING,
    "info": syslog.LOG_INFO,
    "debug": syslog.LOG_DEBUG
    }


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

        if logger == "stderr":
            sys.stderr.write(msg+"\n")
        elif logger == "stdout":
            print(msg)
        elif logger == "syslog":            
            syslog_level = level_map[level]        
            syslog.syslog(syslog_level, msg)
        else:
            with open(logger,"a") as out:
                out.write(msg+"\n")
                

def debug(msg):
    log("debug","DEBUG: "+str(msg))

def info(msg):
    log("info","INFO: "+str(msg))

def warn(msg):
    log("warning","WARNING: "+str(msg))
def warning(msg):
    log("warning","WARNING: "+str(msg))

def error(msg):
    log("error", "ERROR: "+str(msg))

def fatal(msg):
    log("fatal", "FATAL: "+str(msg))
    sys.exit(1)
