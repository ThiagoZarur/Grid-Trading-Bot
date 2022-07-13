#Función recursiva que se encarga de transformar diccionarios que contengan floats como strings 
def fix_floats(data):
    if isinstance(data,list):
        iterator = enumerate(data)
    elif isinstance(data,dict):
        iterator = data.items()
    else:
        raise TypeError('Can only traverse list or dict')
    
    for i,value in iterator:
        if isinstance(value,(list,dict)):
            fix_floats(value)
        elif isinstance(value,str):
            try:
                data[i] = float(value)
            except ValueError:
                pass
    return data