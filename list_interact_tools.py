tools = [
        {
            "type": "function",
            "function": {
                "name": "make_empty_list",
                "description": "Make a new empty list with a given name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "list_name": {
                            "type": "string",
                            "description": "The name of the new list. Should be snake case, for example 'morning_routine'",
                        },
                    },
                    "required": ["list_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "see_all_list_names",
                "description": "See a list of all the list names",
                "parameters": {
                    "type": 'object',
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "see_all_items_in_list",
                "description": "Specify a list_name to get all the items in that list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "list_name": {
                            "type": "string",
                            "description": "The name of the list for which you want to see all the items",
                        },
                    },
                    "required": ["list_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_element",
                "description": "Add a string item a list with a certain list_name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "list_name": {
                            "type": "string",
                            "description": "The name of the list for which you want to add an item",
                        },
                        "item_name": {
                            "type": "string",
                            "description": "The string you want to add to the list",
                        },
                    },
                    "required": ["list_name", "item_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "edit_element",
                "description": "Edit an item with a certain index from a specific list with name list_name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "list_name": {
                            "type": "string",
                            "description": "The name of the list for which you want to edit an item",
                        },
                        "item_index": {
                            "type": "integer",
                            "description": "The index of the item you want to edit from the list",
                        },
                        "new_name": {
                            "type": "integer",
                            "description": "The new string at the given index of the list",
                        },
                    },
                    "required": ["list_name", "item_index", "new_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_element",
                "description": "Delete an item with a certain index from a specific list with name list_name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "list_name": {
                            "type": "string",
                            "description": "The name of the list for which you want to delete an item",
                        },
                        "item_index": {
                            "type": "integer",
                            "description": "The index of the item you want to delete from the list",
                        },
                    },
                    "required": ["list_name", "item_index"],
                },
            },
        },
]