def _remove_duplicates(data):
    already_exist = set()
    data_without_duplicates = []

    for sublist in data:
        sublist_tuple = tuple(sublist)
        if sublist_tuple not in already_exist:
            data_without_duplicates.append(sublist)
            already_exist.add(sublist_tuple)
    
    return data_without_duplicates

def clean_data(data):

    data = _remove_duplicates(data)

    return data

if __name__ == '__main__':
     clean_data()