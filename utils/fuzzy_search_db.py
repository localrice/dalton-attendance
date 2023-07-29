from fuzzysearch import find_near_matches
from utils.sql_sanitization import check
def fuzzy_search_names(searched_name:str,db,table_name):
    '''
    searches the table for the closest student name with the searched_name
    returns a list 
    '''
    cursor = db.cursor()
    sql_injection_present = check(searched_name)
    if sql_injection_present:
        return {'error':'unsafe searched_name'}
    else:
        cursor.execute(f'SELECT student_name FROM {table_name}')
        result = cursor.fetchall()
        list_of_names = [i[0] for i in result]
        name_id_dict = {}
        for name in list_of_names:
            cursor.execute(f'SELECT student_id FROM {table_name} WHERE student_name = ?',(name,))
            result=cursor.fetchall()
            name_id_dict[name] = result[0][0]
        matched_ids = {}
        for key, values in name_id_dict.items():
            fuzz = find_near_matches(searched_name,key,max_l_dist=1)
            if not fuzz:
                pass
            else:
                matched_ids[key] = values
                        
        if not matched_ids:
            return {'error':'null'}
        else: 
            return matched_ids