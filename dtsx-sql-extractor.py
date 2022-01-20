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

import xml.etree.ElementTree as ET
from lib import utils

if __name__ == "__main__":

    sqlList = []  # Initialize list to store all SQL statements
    varsList = []  # Initialize list to store all user variables

    fileName = utils.validateArgs()  # Validates the arguments and returns the file name if valid
    root = ET.parse(fileName).getroot()  # Get the root element of the DTSX package

    # Find all elements with the name VariableValue in the DTS namespace
    for element in root.findall(".//DTS:VariableValue", namespaces=utils.getNamespaces()):
        try:
            var_name, var_val = utils.getVariable(element, root)  # Get the name of the variable and the default value
            utils.createVariableConfiguration(varsList, var_name, var_val)  # Appends the name and value to the list
        except:
            continue

    # findall returns all the elements that match the name. Namespace is used to resolve the DTS class used in
    # the file
    for element in root.findall(".//SQLTask:SqlTaskData", namespaces=utils.getNamespaces()):
        try:
            # Gets the SQL query. The "attribute" argument indicates that the SQL statement is an attribute of the
            # element and not the text
            query = utils.getQuery(element, utils.resolveNameSpace('SQLTask', 'SqlStatementSource'), "attribute")
            # Gets the name of the executable containing the query from the parent element
            query_key = utils.getQueryKey(element, utils.resolveNameSpace('DTS', 'refId'), root)
            utils.createQueryConfiguration(sqlList, query, query_key)  # Appends the name and SQL to the list
        except:
            continue

    # The SQL text is contained as text within these properties rather than attribute values
    for element in root.findall('.//property[@name="SqlCommand"]'):
        try:
            # Gets the SQL query. The "attribute" argument indicates that the SQL statement is the text and not
            # the attribute
            query = utils.getQuery(element, "None", "text")
            # Gets the name of the executable containing the query from the parent element
            query_key = utils.getQueryKey(element, 'refId', root)
            utils.createQueryConfiguration(sqlList, query, query_key)  # Appends the name and SQL to the list
        except:
            continue

    utils.createConfigFile(sqlList, varsList)  # This function call creates the configuration file using the 2 lists
