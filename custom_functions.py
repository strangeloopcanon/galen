# custom_functions.py
custom_functions = [
    {
        "type": "function",
        "function": {
            'name': 'extract_SQL',
            'description': 'Generate a SQLite-compatible SQL query to answer a given question from the attached SQLITE databases. Do not use unsupported functions like PERCENTILE_CONT. Instead, compute using SQLite-friendly methods or omit them if necessary.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The query that the user asked for to return information from attached SQLITE databases'
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            'name': 'visualise',
            'description': 'Perfect python code thats ready to run, of a visualisation of given data or a csv',
            'parameters': {
                'type': 'object',
                'properties': {
                    'vis_code': {
                        'type': 'string',
                        'description': 'A perfect python function to do analysis as asked, comprehensive with all relevant import functions, ready to be run.'
                    }
                }
            },
            "required": ["vis_code"]
        }
    },
    {
        "type": "function",
        "function": {
            'name': 'data_analysis',
            'description': 'Generate perfect, fully formed, comprehensive Python code to answer the user query based on some given input.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'string',
                        'description': 'A perfect python function to do analysis as asked, comprehensive with all relevant import functions, ready to be run.'
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            'name': 'write_report',
            'description': 'Generate perfect step-by-step instructions to create a report based on the original request.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'report_request': {
                        'type': 'string',
                        'description': 'Convert the query into perfect step-by-step instructions based on which a desired report will be written.'
                    }
                },
                "required": ["report_request"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            'name': 'qna',
            'description': 'Generate perfect, comprehensive answers to questions based on an embedded index.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'question': {
                        'type': 'string',
                        'description': 'A perfect, comprehensive question which will be asked so that it can be answered using the embedded index.'
                    }
                },
                "required": ["question"]
            }
        }
    }
]
