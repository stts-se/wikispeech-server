log_level = "error"

def log(level, msg):
    if level == "debug":
        l = 0
    if level == "info":
        l = 1
    if level == "warning":
        l = 2
    if level == "error":
        l = 3
    if log_level == "debug":
        ll = 0
    if log_level == "info":
        ll = 1
    if log_level == "warning":
        ll = 2
    if log_level == "error":
        ll = 3
        
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
