def get_initials(string):
    """
    This function takes a string as a paramter and returns the initials of every word in capitalized form.
    
    Example:
        ```
        >>>get_initials("hello world")
        'HW'

        ```
    """
    words = string.split()
    initials = [word[0].upper() for word in words]
    return ''.join(initials)