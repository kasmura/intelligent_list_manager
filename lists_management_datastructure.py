all_lists = {'grocery_list': [], 'regular_daily_todos': []}

def make_empty_list(list_name):
    if list_name in all_lists:
        return "There is already a list with the list name '{list_name}'."
    else:
        all_lists[list_name] = []
        return f"A list with list name '{list_name}' was succesfully created."

def see_all_list_names():
    return 'All list of all lists by their list_name: ' + str(all_lists.keys())

def see_all_items_in_list(list_name):
    if list_name in all_lists:
        if not all_lists[list_name]:
            return f"The list '{list_name}' is empty."
        items_formatted = "\n".join([f"{i}. {item}" for i, item in enumerate(all_lists[list_name])])
        return f"Items in '{list_name}':\n{items_formatted}"
    else:
        return f"No list found with the name '{list_name}'."

def add_element(list_name, item_name):
    if list_name in all_lists:
        all_lists[list_name].append(item_name)
        return f"'{item_name}' added to '{list_name}'."
    else:
        return f"No list found with the name '{list_name}'."

def delete_element(list_name, item_index):
    if list_name in all_lists:
        try:
            removed_item = all_lists[list_name].pop(item_index)
            return f"'{removed_item}' removed from '{list_name}'."
        except IndexError:
            return f"Invalid index: {item_index}."
    else:
        return f"No list found with the name '{list_name}'."

def edit_element(list_name, item_index, new_name):
    if list_name in all_lists:
        try:
            all_lists[list_name][item_index] = new_name
            return f"Item at index {item_index} in '{list_name}' changed to '{new_name}'."
        except IndexError:
            return f"Invalid index: {item_index}."
    else:
        return f"No list found with the name '{list_name}'."

