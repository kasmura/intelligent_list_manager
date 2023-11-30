The new OpenAI assistants API makes it easy to make simple applications that rely on the intelligence of models like GPT4. An assistant has a specific prompt that describes how it works, and we can give it access to tools that we program ourselves. Imagine an interactive bot where the user can say things like "I want to read Aristotle's Ethics and The Sisyphos Myth" for which it will create a reading list and reply "Both "Aristotle's Ethics" and "The Sisyphos Myth" have been added to your new reading list." You'd be able to say "actually, screw the Camus one" and it could say "The Sisyphos Myth" has been removed from your reading list." By using OpenAI Assistant API with the functionality of "function calls" this is not too hard.

# The Assistant - a bot with a specific prompt and specific tools
We can think of an assistant as a chatbot, it has the power of normal ChatGPT but we give it a different prompt so it behaves slightly differently. It also has tools available that it can use, a bit like (slash exactly like) how the paid ChatGPT can browse Bing. Our assistant has a name "List interactor" and instructions that describes how the assistant behaves when interacting with the user. To initialize an assistant object we can do the following:
```python
import openai
openai_client = OpenAI(api_key=OPENAI_API_KEY)
assistant = openai_client.beta.assistants.create(
    name="List interactor",
    instructions="You are a helpful assistant that helps the user make and edit lists. You have access to functional calls that allow you to make and see lists, add and delete and edit items. You have a tendency to make lists. If the user mentions something you always see whether there might be a relevant list to check, update or create, you don't even ask you just do it. Unless you know for sure which list name is approriate you always check which lists are already created. You usually dont show the snake case names of the lists to the user you usually present them in some more readable way.",
    tools=tools,
    model="gpt-4-1106-preview"
)
```
The parameter *tools* is a list that we will describe below. We select the model *gpt-4-1106-preview* which is a bit costly but is good at understanding context and using the tools. We want to use an intelligent model because we want the assistant to be intelligent enough to understand  what commands to perform even when not asked very explicitly. This makes the user interaction smoother.

# The Thread - a specific chat session
A *thread* can be thought of as a chat session. In some applications you might want to have a single thread per user, in other applications a new thread for each timer the user starts the application. 

When we have a thread we can then add the user's request to the thread and then ask the assistant to "act on the thread" which will make the assistant either reply with a text answer or more excitingly use some tools before it replies. When we ask the assistant the assistant to "act on the thread" we say that we "*run* the thread with a specific assistant". Let's create a new thread:
```python
assistant_thread = openai_client.beta.threads.create()
```
# Taking User Input - adding a message to a thread
For our use case we want an interactive bot that takes input and gives a response to the user after which the user can again give input. Code for this is easy to get from ChatGPT, for example you could use the prompt "give me template code for python terminal interaction taking user input and giving a response in a loop". It might give you functions *start_interaction()* and *process_input(user_input)*

In *process_input* we want to add the user's request to the thread and then we want to run the assistant on the thread in order to get things going and get a response from the bot. To add the user's message to the thread we use *openai_client.beta.threads.messages.create* with the 3 relevant arguments: The parameters are the id of the thread, the *role* which is "user" because it is the user's input (as opposed to *assistant*), and lastly the actual message string added to the chat session.
```python
def process_input(user_input):
    openai_client.beta.threads.messages.create(
        thread_id=assistant_thread.id,
        role="user",
        content=user_input
    )
    run_obj = openai_client.beta.threads.runs.create(
        thread_id=assistant_thread.id,
        assistant_id=assistant.id
    )
    respond_to_thread_action(run_obj)
```
After adding the user's request we let the assistant loose on the thread, by using *openai_client.beta.threads.runs.create*. We then delegate the responsibility of dealing with the result of running this thread to the function *respond_to_thread_action* that we will describe below.

# Function Calls - the assistant want us to run specific functions on our side
Let's make a small detour to talk about function calls before returning to the *respond_to_thread_action* in the next section. Let's assume we have a dict with lists as follows
```python
all_lists = {'grocery_list': [], 'regular_daily_todos': []}
```
We an imagine an [abstract data type] (ADT) (https://en.wikipedia.org/wiki/Abstract_data_type) with the following operations:
- *make_empty_list(list_name)*
- *see_all_list_names()*
- *see_all_items_in_list(list_name)*
- *add_element(list_name, item_name)* 
- *delete_element(list_name, item_index)* 
- *edit_element(list_name, item_index, new_name)*

An ADT is separate from its implementation. You can easily ask ChatGPT to produce code for implementing these operations in Python, so we will not cover it here. Besides, our assistant will not know anything about the implementation it will interact with the ADT.

An assistant can use tools, in our case these tools will be the operations of the ADT. We give the assistant the information about which operations it can perform through the *tools* parameter we saw above. The argument is a list of dicts like this:
```python
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
...
```
Each item in the list is a dict where we specify the *signature* of a function: The name of the function and its description along with each parameter and the parameter type. Remember to be smart about the way you add descriptions about the functions and the arguments, to make the assistant behave as robustly as you can.

In the case of a function taking no arguments, we can write 
```
"parameters": {"type": 'object',"properties": {}}
```

# The Status of a Run
Let's now return to the function *respond_to_thread_action(run)* which we called after submitting the user's request. Inside this function we will now continually ask OpenAI's servers about the *status* of the thread. For our case the status can either be "completed" or "requires_action". If it is completed, there is a text reply that we can present to the end-user. If the status is "requires_action" there will be an associated list of function calls the assistant wants to perform in sequence. One such function call could be add_element("grocery_list", "3 apples"). The assistant will provide both the name of the function and the arguments to the relevant parameters. We will first poll until the thread is ready for us:
```python
def respond_to_thread_action(run):
    while run.status != "completed" and run.status != "requires_action":
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=assistant_thread.id,
            run_id=run.id
        )
        time.sleep(0.1)
    ...
```
By using *retrieve* with the thread id and the run id we can get the information about the status of the run.

## Status "complete" - The assistant's reply to the end-user
Assume we now exit the while loop after the status changes.

In the case where the status is complete, we can get the list of "thread messages" using *messages.list* and specifying the thread id. We can then iterate over the thread messages. However, some of these thread messages we might have already seen, so for simplicity we keep a global list of *all_thread_msg_ids* that we have seen so far. In this way we can skip the ones we have seen. A more elegant solution could be used but this works fine for this quick prototype.
```python
...
if run.status == 'completed':
  new_messages = openai_client.beta.threads.messages.list(
    thread_id=assistant_thread.id
  )
  new_std_outs = []
  for thread_message in new_messages.data:
    if thread_message.id in all_thread_msg_ids: continue
    all_thread_msg_ids.append(thread_message.id)
    for context_text in thread_message.content:
      new_std_outs.append((thread_message.role, context_text.text.value))
    new_std_outs.reverse()
    for role, value in new_std_outs:
      print(role, '>', value)
...
```
The thread messages are ordered with most recent messages first which is probably not how we want to present it to the user. We print both the messages of the user and the assistant - maybe you would want to build a web interface where you want to display both.

Notice that we have an outer loop over both thread messages but inside a thread message it is in principle be many context texts.

# Status "requires_action" - the assistant wants us to perform function calls on our side and tell it the results
In the case where the status of the run is *requires_action*, we will be able to get a list of specific function calls to be performed in sequence. We will perform these function calls at our end, get the the function outputs and submit the outputs back to the thread. Once this is done, the assistant can use the function outputs to produce a text reply leading to status "completed" and we proceed as above. However, something else could also happen! It might also be that the assistant will use the submitted function call outputs to decide it wants to pursue other function calls. For example, it might want us to run "see_all_list_names()" and then once we have submitted the resulting list of all the list names it will decide to add an item to a specific list.

In the below code we loop over the *tool calls* the assistant wants to perform. We look at the function name of each call *tool_call.function.name* and call the relevant function using the specified arguments. In this prototype we will not do error checking, but we would want to do things like checking whether the right arguments are provided and of the right format etc.
```python
...
elif run.status == 'requires_action':
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    function_call_outputs = []
    for tool_call in tool_calls:
    tool_call_arguments = json.loads(tool_call.function.arguments)
    if tool_call.function.name == 'make_empty_list':
        function_call_output = make_empty_list(tool_call_arguments['list_name'])
    elif tool_call.function.name == 'see_all_list_names':
        function_call_output = see_all_list_names()
    elif tool_call.function.name == 'see_all_items_in_list':
        function_call_output = see_all_items_in_list(tool_call_arguments['list_name'])
    elif tool_call.function.name == 'add_element':
        function_call_output = add_element(tool_call_arguments['list_name'], tool_call_arguments['item_name'])
    elif tool_call.function.name == 'edit_element':
        function_call_output = edit_element(tool_call_arguments['list_name'], tool_call_arguments['item_index'], tool_call_arguments['new_name'])
    elif tool_call.function.name == 'delete_element':
        function_call_output = delete_element(tool_call_arguments['list_name'], tool_call_arguments['item_index'])
    else:
        raise Exception('Unknown function name', tool_call)
    ...
```
Still inside the loop over tool calls, once we have the resulting output by running the given function on our side we will want to construct a dict with the fields *output* and the id *tool_call_id* of the tool call we are currently processing in the loop. We add this dict to a list of all the function call outputs and use *submit_tool_outputs* to submit this list of tool outputs to the thread and the run we are using.
```python
...
print('tool use > ', tool_call.function.name)
print('\t Input: ', tool_call_arguments)
print('\t Output: ', function_call_output)
function_call_outputs.append({
    'output': function_call_output,
    'tool_call_id': tool_call.id
})
submit_obj = openai_client.beta.threads.runs.submit_tool_outputs(
    run_id = run.id,
    thread_id = assistant_thread.id,
    tool_outputs = function_call_outputs)
respond_to_thread_action(submit_obj)
```
When we have done so we call the *respond_to_thread_action* function recursively: As described above we are then waiting for further function calls or a text response with status "completed".

# Trying it out
Let's try out the system
```
user > heyo
assistant > Hello! How can I assist you today? Is there a list you need help with, or do you have something else in mind?
user > my favorite colors are green, purple, and orange
tool use >  see_all_list_names
	 Input:  {}
	 Output:  All list of all lists by their list_name: dict_keys(['grocery_list', 'regular_daily_todos'])
tool use >  make_empty_list
	 Input:  {'list_name': 'favorite_colors'}
	 Output:  A list with list name 'favorite_colors' was succesfully created.
tool use >  add_element
	 Input:  {'list_name': 'favorite_colors', 'item_name': 'Green'}
	 Output:  'Green' added to 'favorite_colors'.
tool use >  add_element
	 Input:  {'list_name': 'favorite_colors', 'item_name': 'Purple'}
	 Output:  'Purple' added to 'favorite_colors'.
tool use >  add_element
	 Input:  {'list_name': 'favorite_colors', 'item_name': 'Orange'}
	 Output:  'Orange' added to 'favorite_colors'.
assistant > I've noted your favorite colors as Green, Purple, and Orange in a list. If there's anything else you'd like to do, just let me know!
user > actually remove the one that is most similar to yellow
tool use >  delete_element
	 Input:  {'list_name': 'favorite_colors', 'item_index': 2}
	 Output:  'Orange' removed from 'favorite_colors'.
assistant > Orange, being the color most similar to yellow, has been removed from your list of favorite colors. You now have Green and Purple on your list. If you need anything else adjusted or if there is anything else I can do for you, just tell me!
user > I need to buy vitamin B at some point
tool use >  see_all_items_in_list
	 Input:  {'list_name': 'grocery_list'}
	 Output:  The list 'grocery_list' is empty.
tool use >  add_element
	 Input:  {'list_name': 'grocery_list', 'item_name': 'Vitamin B'}
	 Output:  'Vitamin B' added to 'grocery_list'.
assistant > I've added Vitamin B to your grocery list. Whenever you're ready to shop, you'll have that reminder in place. Is there anything else you're considering to add to your lists?
user > what lists do I have?
tool use >  see_all_list_names
	 Input:  {}
	 Output:  All list of all lists by their list_name: dict_keys(['grocery_list', 'regular_daily_todos', 'favorite_colors'])
assistant > You currently have three lists:

1. Grocery List
2. Regular Daily Todos
3. Favorite Colors

Would you like to see the items in any of these lists, or perhaps update them?
```

# The bigger picture
Giving LLMs access to basic data structures should be a useful step towards more complex applications and the lists abstract data type is an easy and intuitive data structure for an LLM to handle.

It also does not need to be only end-users that talk to such assistants. One can imagine ecosystems and platforms of assistants that interact with each other using natural language each taking responsibility for separate things using their available functionality and other assistants whose main responsibility is to interact in natural language with such lower-level assistants. Different assistants may have different access rights in the system, allowing for a system or platform where new assistants can easily be accessed while maintaining the user's privacy. Such a view parallels the idea of LLMs as forming the kernel of a new high-level operating system, see Andrej Kaparthy's twitter post. https://twitter.com/karpathy/status/1707437820045062561

If you have any questions or comments or just want to talk about the many possibilities opened up by these technologies, please feel free to reach out. You can find me on https://kmrasmussen.com

The code for the prototype is available at https://github.com/kasmura/intelligent_list_manager
