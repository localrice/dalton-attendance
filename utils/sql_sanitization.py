sql_keywords = ['drop', 'delete', 'truncate', 'insert', 'update', 'alter', 'create',
                'select', 'union', 'join', 'or', 'and', 'exec', 'execute', 'xp_',
                'xp_cmdshell', 'sp_', 'sp_executesql', 'declare', 'cast', 'convert',
                'script', 'javascript', 'iframe', 'onload', 'alert', 'document',
                'cookie', 'eval', 'select', 'where', 'having', 'group by', 'order by',
                'from', 'count', '1=1', '--', '/*', '*/']


def check(input: str):
    '''
    takes an input and checks for any words that might be used in an sql injection
    returns True if any word associated with sql injection is found
    returns False if not
    '''
    user_input = input.lower()
    for k in sql_keywords:
        if k in user_input:
            return True
        else:
            pass
    return False
