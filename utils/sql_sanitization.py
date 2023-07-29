import re

sql_keywords = ['drop', 'delete', 'truncate', 'insert', 'update', 'alter', 'create',
                'select', 'union', 'join', 'or', 'and', 'exec', 'execute', 'xp_',
                'xp_cmdshell', 'sp_', 'sp_executesql', 'declare', 'cast', 'convert',
                'script', 'javascript', 'iframe', 'onload', 'alert', 'document',
                'cookie', 'eval', 'select', 'where', 'having', 'group by', 'order by',
                'from', 'count', '--', '/*', '*/']


def check(name: str):
    '''
    takes an input and checks for any words that might be used in an sql injection
    returns True if any word found in sql_keywords is found
    returns False if not
    '''
    name_tokens = re.findall(r'\b\w+=\w+\b|\b\w+\b', name.lower())
    print(name_tokens)
    for token in name_tokens:
        if token in sql_keywords:
            return True
    return False
