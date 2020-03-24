import re
import importlib.util

def import_module(directory, module_name):
                
    #print("Importing module '%s'" % module_name)

    #HB 200218
    #Add directory to sys.path
    #if not directory in sys.path:
    #    sys.path.insert(0,directory)
    #print(sys.path)
    #Import the module..
    #mod = import_module(module_name)
    #The above doesn't work in all cases..
    
    #HB 200218 This seems to work.. 
    #import importlib.util
    module_file = "%s/%s.py" % (directory, re.sub("\.", "/", "%s" % (module_name)))
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    return mod

