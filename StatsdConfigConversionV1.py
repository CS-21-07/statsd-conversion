import json
import re
import string
STATSD_LOC = "./Config/statsd.conf"
#NOTE TO FUTURE USERS:
#This script is specifically used to create the graph.json file found within the graphing solution provided by SU
#team SU21-07. This graph.json holds the specs of all predefined graphs ingested by the utility. 
#This script is just meant to automatically do EXACTLY what has been done (but does fix a few small typos), 
#and this code operates a finnicky way to accomodate the format yielded by the hand-made graph.json. Going forward
#Code within the graphing utility should probably be adapted to use the second version of this script, which 
#converts the whole configuration file, and not just pieces of it in a consistent and more reliable way. 

def parse_line(line):
    ret = [i for i in re.split(r' +(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line) if i != '']
    return ret

def write_graph_conf():
    #VERY SENSITIVE TO CONFIG FORMAT
    #If you are to use this function, statsd.conf must adhere to a few rules in order to not produce broken json.
    #1. If a graph has a LINES field, it must be the last field (it acts as a delimiter).
    #2. When creating object fields that are lists or objects of objects, no empty lines should be present inside a {}
    #3. Any closing } should take up their own lines.
    #4. The whole of the graph{} section should be followed by the 'group' section, as it is used as a hackish delimiter to mark the end of the graphing section. yikes.

    statsd = open(STATSD_LOC, "r+") #read thru line by line
    graph_conf= open("graph.json","w+")
    json_output = '{"graph":{'


    file_line = statsd.readline()
    while (file_line): #iterates through the whole config file, checking for Graph
        parsed_line = parse_line(file_line)
        indentation_level = 0

        if (parsed_line and parsed_line[0] == "graph" or parsed_line[0] == "detailgraph"): #find a graph
            indentation_level+=1
            json_output+=(parsed_line[1]+ ': {')
            while (indentation_level > 0 and file_line):  #iterates through lines within a graph entry
                file_line = statsd.readline()
                parsed_line = parse_line(file_line)
                
                if (len(parsed_line)==0): #for empty lines
                    pass

                elif (parsed_line[0]=="graph" or parsed_line[0]=="detailgraph"): 
                    json_output+="},"
                    indentation_level-=1

                elif (parsed_line[0] == "ARGS"):
                    json_output+='"ARGS": ['
                    json_output+= (parsed_line[1])
                    file_line = statsd.readline()
                    while(parsed_line[0]=="ARGS"):
                        json_output+= (","+parsed_line[1])
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                    json_output += '],'

                elif (parsed_line[0] == "RRDFILE"):
                    indentation_level+=1
                    json_output+='"RRDFILE": { "path": ' + parsed_line[1]+','
                    data_source_list = []
                    while(indentation_level==2): #While inside RRDFILE indentation level
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        
                        if (parsed_line[0]=="DATASOURCE"): #first ds label
                            json_output+='"DATASOURCE": {'
                            while (parsed_line[0] == "DATASOURCE"): #covers over all included datasources and adds them to object
                                ds_string = (parsed_line[1] + ": {")
                                
                                file_line = statsd.readline()
                                parsed_line = parse_line(file_line)
                                ds_string+= ('"'+parsed_line[0] + '": ' + parsed_line[1]+',')

                                file_line = statsd.readline()
                                parsed_line = parse_line(file_line)
                                ds_string+= ('"'+parsed_line[0] + '": "' + parsed_line[1].strip('\n') + '"},')

                                json_output+=ds_string
                                file_line = statsd.readline() #move over '}'

                                file_line = statsd.readline()
                                parsed_line = parse_line(file_line)
                                
                            indentation_level-=1;
                            json_output = json_output[:-1]+'}'
                    json_output+='},'

                elif (parsed_line[0]== "LINE"):
                    indentation_level+=1
                    json_output+='"LINE": ['
                    lines = []

                    while (parsed_line[0] == "LINE"): #covers over all included datasources and adds them to object
                        if (len(lines) > 0):
                            lines.append(",")

                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string = ('{"' + parsed_line[0] +'": '+ parsed_line[1].strip("\n") + ",")
                       
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string += ('"'+parsed_line[0] +'": '+ parsed_line[1].strip("\n") + ",")
                               
                        if (parsed_line[1].strip("\n") == '"gtmaaaarequests"'):
                            print("entered")

                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string += ('"'+parsed_line[0] +'": '+ parsed_line[1].strip("\n") + ",")
                             
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string += ('"'+parsed_line[0] +'": "'+ parsed_line[1].strip("\n") + '"}')
                        
                        lines.append(line_string)

                        file_line = statsd.readline() # }
                        file_line = statsd.readline() # next line
                        parsed_line = parse_line(file_line)
                            
                    for elem in lines:
                        json_output+=(elem)

                    json_output=json_output[:-1]+'}]'
                    indentation_level-=1;

                elif (parsed_line[0]=="DETAILGRAPH"):
                    json_output+= ('"DETAILGRAPH": ["')
                    without_quotes = parsed_line[1].strip('"')
                    without_quotes = parsed_line[1].strip('"\n')
                    details = without_quotes.split(",")
                    json_output += details[0]
                    for detail in details:
                        json_output+=('","' + detail)
                    json_output+="\"],\n"

                elif (parsed_line[0]=="AREA"):
                    ds_string = ('"'+parsed_line[0] +'"'+ ": {")
                                
                    file_line = statsd.readline()
                    parsed_line = parse_line(file_line)
                    ds_string+= ('"'+parsed_line[0] + '": ' + parsed_line[1].strip('\n')+',')

                    file_line = statsd.readline()
                    parsed_line = parse_line(file_line)
                    ds_string+= ('"'+parsed_line[0] + '": ' + parsed_line[1].strip('\n') + ',')

                    file_line = statsd.readline()
                    parsed_line = parse_line(file_line)
                    ds_string+= ('"'+parsed_line[0] + '": "' + parsed_line[1].strip('\n') + '"},')

                    json_output+=ds_string
                    file_line = statsd.readline() #move onto '}'
                    parsed_line = parse_line(file_line)
            
                elif (parsed_line[0]=="STACK"):
                    indentation_level+=1
                    json_output+='"STACK": ['
                    stacks = []

                    while (parsed_line[0] == "STACK"): #covers over all included datasources and adds them to object
                        if (len(stacks) > 0):
                            stacks.append(",")

                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string = ('{"' + parsed_line[0] +'": '+ parsed_line[1].strip("\n") + ",")
                       
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string += ('"'+parsed_line[0] +'": '+ parsed_line[1].strip("\n") + ",")
                             
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                        line_string += ('"'+parsed_line[0] +'": "'+ parsed_line[1].strip("\n") + '"}')
                        
                        stacks.append(line_string)

                        file_line = statsd.readline()
                        file_line = statsd.readline()
                        parsed_line = parse_line(file_line)
                            
                    for elem in stacks:
                        json_output+=(elem)

                    json_output=json_output[:-1]+'}]'

                    indentation_level-=1;

                elif (len(parsed_line) >= 2): #generic case
                    if (parsed_line[0] == "group"): #hackish escape clause
                        indentation_level-=1
                        break

                    if (parsed_line[1].strip("\n")=='UNKNOWN'):
                        json_output += ('"'+parsed_line[0]+'": "' + parsed_line[1].strip("\n")+'",' )
                    else:
                        json_output += ('"'+parsed_line[0]+'": ' + parsed_line[1]+',' )

                elif (parsed_line[0].strip('\n') == '}'):
                    indentation_level-=1
                
                else: #new line character, }
                    pass 
        else:
            file_line = statsd.readline()

    json_output +="}}}"
    return json_output

graphs= open("graph.json","w+")

graphs_json = write_graph_conf()
graphs.write(graphs_json)

graphs.close()



    