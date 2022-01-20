# dtsx-sql-extractor
This utility extracts SQL statements from an SSIS package and creates a config file using a key-value format where the key is the name of the SSIS stage containing the SQL and the value is the SQL Query. 

## Usage
`SSISExtractor.py --filename 'test.dtsx' --source 'postgres'`

--filename : The DTSX file that needs to be parsed  
--source : If the value is set to "sqlserver", the utility will perform syntax conversion to PostgresSQL

## Author
Jerome Rajan (https://github.com/datasherlock)

Durga Prasad
