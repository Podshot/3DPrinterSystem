import json
import os
import directories

if __name__ != "__main__":
    if os.environ.get("PORT") is not None:
        return
    fp = open(os.path.join(directories.base_directory, "config.cfg"))
    data = json.load(fp)
    fp.close()
    for (key, value) in data.iteritems():
        os.environ[key] = value
    
