########################################################################################################################
#   Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                             #
#                                                                                                                      #
#   Licensed under the Apache License, Version 2.0 (the "License");                                                    #
#   you may not use this file except in compliance with the License.                                                   # 
#   You may obtain a copy of the License at                                                                            # 
#                                                                                                                      #
#       http://www.apache.org/licenses/LICENSE-2.0                                                                     # 
#                                                                                                                      #
#   Unless required by applicable law or agreed to in writing, software                                                #
#   distributed under the License is distributed on an "AS IS" BASIS,                                                  #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                           #
#   See the License for the specific language governing permissions and                                                #
#   limitations under the License.                                                                                     #
########################################################################################################################

from os import replace
from os.path import dirname, abspath
import sys
import os.path
import argparse
import re

namespaces = {'DTS': 'www.microsoft.com/SqlServer/Dts', "SQLTask": "www.microsoft.com/sqlserver/dts/tasks/sqltask"}


def init_argparse():
    """Parses the required arguments file name and source database type and returns a parser object"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s --filename 'test.dtsx' --source 'postgres'",
        description="Creates a configuration file in the output directory based on the SQLs in the dtsx file."
    )
    parser.add_argument(
        "-f", "--filename", action='store', help='Input DTSX file name', required=True
    )

    parser.add_argument(
        "-s", "--source", action="store", help='Type of the source database (sqlserver, postgres)', required=True
    )
    return parser


def validateArgs():
    """Validates arguments and returns file name if successful"""
    parser = init_argparse()
    args = parser.parse_args()

    if not os.path.isfile(args.filename):  # Check if file is present in the path
        print(args.filename)
        print("Unable to open file. Please check permissions, file name and the path")
        sys.exit(-1)

    if args.source.lower() != 'sqlserver' and args.source.lower() != 'postgres':  # Validate the value of the source argument
        print("The value of source must either be sqlserver or postgres")
        sys.exit(-1)
    else:
        pass
    return args.filename


def getNamespaces():
    """Returns the namespaces defined as a global variable in the utils.py"""
    return namespaces


def resolveNameSpace(namespace, elemProperty):
    """Resolves the namespace of the property"""
    return "{" + namespaces[namespace] + "}" + elemProperty


def writeToConfigFile(text, mode):
    """Writes the 'text' to the configuration file in the output directory using the 'mode' specified. Mode should be
    append or overwrite """
    config_file = dirname(dirname(abspath(__file__))) + "/output/config.properties"
    write_mode = 'w' if mode == 'overwrite' else 'a'
    try:
        with open(config_file, write_mode) as f:
            f.write(text + "\n")
    except:
        print("Error creating config file. Check if directory 'output' exists and try again.")
        sys.exit(-1)
    return config_file


def createConfigFile(sqlList, varList):
    """Writes the sqlList and varList to the configuration file and formats it as per requirement"""
    writeToConfigFile('[Connections]\n\n\n', 'overwrite')
    writeToConfigFile('\n\n\n[Variables]', 'append')
    for var in varList:
        config_file = writeToConfigFile(var, 'append')

    writeToConfigFile('\n\n\n[Query]', 'append')
    for sql in sqlList:
        config_file = writeToConfigFile(sql, 'append')
    print(config_file + " Configuration file created")
    return True


def getQuery(element, elementPath, valueType):
    """Gets the query from the elementPath"""
    if valueType.lower() == "attribute":
        query = element.get(elementPath)
        query = queryCleaner(query)
    elif valueType.lower() == "text":
        query = queryCleaner(element.text)
    return query


def getVariable(element, root):
    parser = init_argparse()
    args = parser.parse_args()
    
    parent_map = createParentChildMap(root)
    var_value = queryCleaner(element.text)
    var_name = parent_map[element].get(resolveNameSpace('DTS', 'ObjectName'))
    var_namespace = parent_map[element].get(resolveNameSpace('DTS', 'Namespace'))

    if args.source == 'sqlserver':
        var_value = sqlServerToPgConvertor(var_value)

    if var_namespace == 'User':
        return var_name, var_value
    else:
        return

def getQueryKey(element, elementPath, root):
    parent_map = createParentChildMap(root)
    query_key = "Query_" + parent_map[parent_map[element]].get(elementPath) \
        .replace("\\", "_") \
        .replace(" ", "_") \
        .replace("Package_Sequence_Container_", "") \
        .replace("Package_", "") \
        .replace("(", "") \
        .replace(")", "") \
        .replace("[", "") \
        .replace("]", "")

    return query_key


def createParentChildMap(root):
    parent_map = {child: parent for parent in root.iter() for child in parent}
    return parent_map


def createQueryConfiguration(sqlList, query, query_key):
    parser = init_argparse()
    args = parser.parse_args()
    if args.source == 'sqlserver':
        query = sqlServerToPgConvertor(query)
    sqlList.append(query_key + " = " + query)


def createVariableConfiguration(varsList, var_name, var_value):
    varsList.append(var_name + " = " + var_value)


def queryCleaner(query):
    if query.split('\n')[0].startswith('--'):
        return ' '.join(query.split('\n')[1:])
    else:
        return query.replace('\n', " ")


def sqlServerToPgConvertor(query):
    query = query \
        .replace("[dbo].", "") \
        .replace("]", "") \
        .replace("[", "") \
        .replace("GETDATE()", "current_date()") \
        .replace("WITH (NOLOCK)"," ") \
        .replace("WITH (nolock)"," ") \
        .replace("(nolock)"," ") \
        .replace("(NOLOCK)"," ")

    query = re.sub(r"\bEXEC\b","SELECT FROM ", query,flags=re.IGNORECASE)
    return query
