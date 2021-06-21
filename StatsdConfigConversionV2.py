import json
import re
import string
STATSD_LOC = "./Config/statsd.conf"

#This function is intended to build upon what was learned from StatsdConfigConversionV1.py by using a more dynamic approach 
#Turns whole conf file into json (not just graph)


#WHAT IS UP WITH NULL VALUE AT END?

obj_storage = dict()
statsd = open(STATSD_LOC, "r+") # read thru line by line
config_file = statsd.readlines()

line_ptr = 0

def unlister():
    """ Takes a dictionary and a key. If the dictionary-key set contains a list with only a single, the entry will
        be converted to contain a single element not contained in a list.
        Receives: Dictionary and String
        Returns: Reformatted Dictionary
    """

def parse_line(line):
    """ Takes a line of file input, removes special characters, and tokenizes it.
        Receives: String var representing single line of file.
        Outputs: List of Strings that contain all tokens of a line, delimited by spaces
    """
    line = line.replace('\n','') # removes new line
    ret = [i for i in re.split(r' +(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line) if i != ''] #tokenizes
    if len(ret) > 0 and ret[0][0] == '#': # only handles full line comments... how remove from *[code] #comment* format lines
        ret = []
    return ret

# Should return one whole object (and work recursively for nested objects)
def get_obj():
    """ Function which should activate any time a new dictionary is created. Iterates over a dictionary and can iterate
        over dictionaries in dictionaries. All changes made are reflected in global scope.

        Receives: N/A
        Returns: N/A
    
    """
    # 1. Enters loop, creates object of key-value pairs
    # 2. Iterates over each row, taking name and value
    # 3. If value is another dictionary (represented by '{'), recurse
    # 4. Break when obj ends in '}'
    
    local_obj_storage = dict()
    global line_ptr

    file_line = config_file[line_ptr]
    line_ptr += 1
    curr_line = parse_line(file_line)

    while(line_ptr <= len(config_file)):

        if (len(curr_line)==0):
            pass

        elif (curr_line[0]=='}'): # escape clause
            return local_obj_storage

        elif (file_line.count('{') > 0 and len(curr_line)==3 and not curr_line[0] in local_obj_storage): # Recurse, create new dict entry, titled field
            local_obj_storage.update({curr_line[0] : {curr_line[1]:[get_obj()]}})

        elif (file_line.count('{') > 0 and len(curr_line)==3 and curr_line[0] in local_obj_storage): # Recurse, update existing dict entry, titled field
            local_obj_storage[curr_line[0]][curr_line[1]]=[get_obj()]

        elif (file_line.count('{') > 0 and len(curr_line)== 2 and not curr_line[0] in local_obj_storage): # Recurse, create new dict entry, untitled field (like LINE)
            local_obj_storage.update({curr_line[0] : [get_obj()]})

        elif (file_line.count('{') > 0 and len(curr_line)== 2 and curr_line[0] in local_obj_storage): # Recurse, add to existing dict entry, untitled field (like LINE)
            local_obj_storage[curr_line[0]].append(get_obj())

        elif (curr_line[0] in local_obj_storage): # No recurse, if already exists append to list
            local_obj_storage[curr_line[0]].append(curr_line[1])

        else: # New standard key-val pair initiates into list
            local_obj_storage.update({curr_line[0]:[curr_line[1]]})

        # continue
        file_line = config_file[line_ptr]
        line_ptr+=1
        curr_line = parse_line(file_line)

def convert_file():
    """ Control function which iterates over the surface level of the source config file. All changes made
        occur at global scope.

        Receives: None (although it uses several globals)
        Returns: A dictionary which reflects the structure of the config file
    """
    # 1. Create comprehensive Dict into which object-key pairs can be stored 
    # 2. Iterate thru file, line by line, paying attention to '{', skipping comments
    # 3. When new object opens, take name and assign object to dictionary
    # 4. End when file runs out
    # 5. Output Dict

    global line_ptr
    final_obj_storage = dict()

    file_line = config_file[line_ptr]
    line_ptr+=1
    curr_line = parse_line(file_line)
    
    while(line_ptr < len(config_file)-1):
        
        if (line_ptr == 9951):
            print('Made it to the end')

        if (len(curr_line)==0):
            pass

        elif (curr_line.count('{') > 0 and curr_line[0] not in final_obj_storage): # recurse, add name to dict
            final_obj_storage.update({curr_line[0]:[get_obj()]})

        elif (curr_line.count('{') > 0 and curr_line[0] in final_obj_storage): # if name is already in dict, append to dict entry
            final_obj_storage[curr_line[0]].append(get_obj())

        elif (curr_line[0] in final_obj_storage): # No recurse, if already exists append to list
            final_obj_storage[curr_line[0]].append({curr_line[1]:curr_line[2]})

        else: # new standard key-val pair initiates into list
            final_obj_storage.update({curr_line[0]:[curr_line[1]]})

        if (line_ptr < len(config_file)):
            file_line = config_file[line_ptr]
            line_ptr+=1

            curr_line = parse_line(file_line)

    return final_obj_storage


out_dict = convert_file()
json_object = json.dumps(out_dict, indent = 4)  

with open('statsd.conf.json', 'w') as f:
    f.write(json_object)