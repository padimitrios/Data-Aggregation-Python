import json
import numpy as np

                                                        ### Tree structs and functions ###
class Node:

  # constructor arguments
  # msg -> json object  ex.{"TEMP": 25,"HUM": 50}
  def __init__(self, msg):
    self.msg = msg
    self.left = None
    self.right = None
    
# desc  -> insert new node to root
# root -> root of the current tree
# msg  -> json object  ex.{"TEMP": 25,"HUM": 50}
# void functions no return
def insert_left(root, msg):
  root.left = Node(msg)

def insert_right(root, msg):
  root.right = Node(msg)


# desc  -> insert a whole subtree to root
# root      -> pointer to root of the current tree
# subParent -> pointer to root of the sub tree to be appended to root
# reutrns   -> nothing
def insert_parent_right(root, subParent):
  root.right = subParent

def insert_parent_left(root, subParent):
  root.left = subParent

                                                         ### end tree ###

                                                    ### utility functions ###

# desc  -> calculate the lev distance of two strings
# token1   -> string of type TAG1-TAG2-...-TAGN
# token2   -> string of type TAG1-TAG2-...-TAGN
# returns  -> float (numeric value of difference between the 2 tokens)
def levenshtein_distance(token1, token2):
  distances = np.zeros((len(token1) + 1, len(token2) + 1))

  for t1 in range(len(token1) + 1):
    distances[t1][0] = t1

  for t2 in range(len(token2) + 1):
    distances[0][t2] = t2

  a = 0
  b = 0
  c = 0

  for t1 in range(1, len(token1) + 1):
    for t2 in range(1, len(token2) + 1):
      if (token1[t1 - 1] == token2[t2 - 1]):
        distances[t1][t2] = distances[t1 - 1][t2 - 1]
      else:
        a = distances[t1][t2 - 1]
        b = distances[t1 - 1][t2]
        c = distances[t1 - 1][t2 - 1]

        if (a <= b and a <= c):
          distances[t1][t2] = a + 1
        elif (b <= a and b <= c):
          distances[t1][t2] = b + 1
        else:
          distances[t1][t2] = c + 1

  return distances[len(token1)][len(token2)]

# desc  -> print the tree using lever order traversal
# root     -> pointer to root of the tree
# returns  -> nothing (display function)
def level_order_traversal(root):
  if not root:
    return

  queue = [root]

  while queue:
    level_size = len(queue)
    level_vals = []

    for i in range(level_size):
      node = queue.pop(0)
      level_vals.append(node.msg)
      if node.left:
        queue.append(node.left)
      if node.right:
        queue.append(node.right)

    print(" ".join(map(str, level_vals)))


# args for distance_matrix_calculation
# tag_arr     -> array of strings
# table_size  -> integer value of the size of the tag_arr
# returns     -> 2d array of distances
def distance_matrix_calculation(tag_arr, table_size):
  distances = [[0 for j in range(table_size)] for i in range(table_size)]

  #populate the upper triangular part of the matrix with the distances between the tags
  for i in range(table_size):
    for j in range(i + 1, table_size):
      distances[i][j] = levenshtein_distance(tag_arr[i], tag_arr[j])

  return distances

# desc  -> merges two json obects keeping the average of their values in case of two same instances
# obj1  -> json object  ex.{"TEMP": 25,"HUM": 50}
# obj2  -> json object  ex.{"TEMP": 25,"HUM": 50}
# returns     -> 2d array of distances
def message_merge(obj1, obj2):
  result = obj1.copy()

  for key, value in obj2.items():
      if key in result:
          result[key] = (result[key] + value) / 2
      else:
          result[key] = value

  return result

  
# desc  -> finds and returns and object in the array
# json_arr          -> array of json objects
# string_to_search  -> string of tags seperated by '-'
# returns           -> json object
def message_return(json_arr, string_to_search):

  for obj in json_arr:
    if set(obj.keys()) == set(string_to_search.split('-')):
      return obj


# desc  -> returns an array of string combination, of each objects keys
# json_arr          -> array of json objects
# returns           -> strings array
def extract_message_keys(json_arr):
  tag_arr = []
  for obj in json_arr:
    obj_keys = []
    for key in obj.keys():
      obj_keys.append(key)
    tag_arr.append('-'.join(sorted(obj_keys)))
  
  return tag_arr
                                                            ### utility functions end ###


                                                                ### tree generation ###
def tree_generation(json_arr):
  #intialize the tree
  tree_head = None
  
  # Initialize the array of tag strings and the dictionary of key-value pairs
  tag_arr = extract_message_keys(json_arr)
  
  messages_table = json_arr.copy()
  #calculate the distance table
  table_size = len(tag_arr)
  distances = distance_matrix_calculation(tag_arr, table_size)

  #tree construction loop when there is more than one tag
  while (table_size != 1):

    #find closest pair and coords of it in the table
    min_value = float('inf')
    min_row = 0
    min_col = 0
    for i in range(len(distances)):
      for j in range(i + 1, len(distances[i])):
        if distances[i][j] < min_value:
          min_value = distances[i][j]
          min_row = i
          min_col = j

    #get the closest messages from the messages array
    msg_1 = message_return(messages_table,tag_arr[min_col])
    msg_2 = message_return(messages_table,tag_arr[min_row])
    
    #combine the two msg
    aggregated_msgs = message_merge(msg_1,msg_2)
    
    #create the tree nodes that will be appended to the tree
    parent_of_childs = Node(aggregated_msgs)
    parent_of_childs.left = Node(msg_1)
    parent_of_childs.right = Node(msg_2)

    #check if one of the msg is the root of the tree
    first_tag_is_root = tree_head is not None and msg_1 == tree_head.msg
    second_tag_is_root = tree_head is not None and msg_2 == tree_head.msg

    if tree_head is None:
      #empty tree insert the parent as root
      tree_head = parent_of_childs

    elif first_tag_is_root and second_tag_is_root:
      #edge case
      pass

    elif first_tag_is_root:
      #if the tag_arr[min_col] is the current root.msg set futures root left child to tag_arr[min_row]
      #and set the future root child to the current root of the tree
      insert_left(parent_of_childs, msg_2)
      insert_parent_right(parent_of_childs, tree_head)
      tree_head = parent_of_childs

    elif second_tag_is_root:
      #if the tag_arr[min_row] is the current root.msg set futures root left child to tag_arr[min_col]
      #and set the future root child to the current root of the tree
      insert_left(parent_of_childs, msg_1)
      insert_parent_right(parent_of_childs, tree_head)
      tree_head = parent_of_childs

    else:
      #if none of the two msg are the root.msg then create a new sub tree with the closest pair
      insert_left(parent_of_childs, msg_1)
      insert_right(parent_of_childs, msg_2)

      #create a new super parent that will be the combination of the closest pair messages
      super_parent_of_childs = Node(message_merge(parent_of_childs.msg,tree_head.msg))
      #set the subtree root and the tree_head root as the children of the super parent root
      super_parent_of_childs.left = parent_of_childs
      super_parent_of_childs.right = tree_head
      #set the current tree root as the super parent root
      tree_head = super_parent_of_childs

    #pop the msg from the array and insert their combination
    messages_table.remove(msg_1)
    messages_table.remove(msg_2)
    messages_table.append(aggregated_msgs)

    #decrease the table_size cause of the msg combination
    table_size -= 1
    
    #update distances table with the distances of the new tag_arr
    tag_arr = extract_message_keys(messages_table)
    distances = distance_matrix_calculation(tag_arr, table_size)

  #print the levels of the tree
  level_order_traversal(tree_head)

#messages table
json_arr = [{
  "TEMP": 25,
  "HUM": 50
}, {
  "TEMP": 30,
  "CO2": 40,
  "HUM": 59
},{
  "H2O":54,
  "CO2": 40
}]

#tree generation function
tree_generation(json_arr)
