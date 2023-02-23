import json
import numpy as np
# import levenshtein

### Tree structs and functions ###
class Node:
  def __init__(self, tags):
      #tags is a string value of type TAG1-TAG2-...-TAGN
      self.tags = tags
      self.left = None
      self.right = None

# args for tree insertion functions
# root -> root of the current tree
# tags -> string of type TAG1-TAG2-...-TAGN
# void functions no return
def insert_left(root, tags):
    root.left = Node(tags)

def insert_right(root, tags):
    root.right = Node(tags)

# args for tree insertion functions
# root      -> pointer to root of the current tree
# subParent -> pointer to root of the sub tree to be appended to root
# reutrns   -> nothing
def insert_parent_right(root, subParent):
    root.right = subParent

def insert_parent_left(root, subParent):
    root.left = subParent
  
### end tree ###

### utility functions ###
  
# args for combination
# str_1    -> string of type TAG1-TAG2-...-TAGN
# str_2    -> string of type TAG1-TAG2-...-TAGN
# returns  -> final string combination of str_1 and str_2
def combination(str_1, str_2):
    #intial string with - to await for the next values to be appended
    final_str = str_1 + "-"

    #parse the tokens and append the new tag with a "-" on the end to await for new tag
    for token in str_2.split("-"):
        if token not in final_str:
            final_str += token + "-"
          
    #remove the last "-" for the final string because no more tags will be appended
    final_str = final_str[:-1]
  
    return final_str

# args for levenshtein_distance
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
            if (token1[t1-1] == token2[t2-1]):
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

# args for levenshtein_distance
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
            level_vals.append(node.tags)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        print(" ".join(map(str, level_vals)))

# args for distance_matrix_calculation
# tag_arr     -> array of strings
# table_size  -> integer value of the size of the tag_arr
# returns     -> 2d array of distances
def distance_matrix_calculation(tag_arr,table_size):
  distances = [[0 for j in range(table_size )] for i in range(table_size )]

  #populate the upper triangular part of the matrix with the distances between the tags
  for i in range(table_size):
    for j in range(i + 1, table_size ):
        distances[i][j] = levenshtein_distance(tag_arr[i], tag_arr[j])
  
  return distances

### utility functions end ###


### tree generation function ###
def tree_generation():
  #intialize the tree
  tree_head = None

  # Define the array of JSON objects (messeges)
  json_arr = [
      {"TEMP": 25, "HUM": 50},
      {"TEMP": 30, "CO2": 40, "HUM": 59},
      {"RAIN": 30, "WEATHER": 40, "SUN":40},
      {"YES":30},
      {"YES":20}
  ]
  
  # Initialize the array of tag strings and the dictionary of key-value pairs
  tag_arr = []
  value_dict = {}
  
  for json_obj in json_arr:
      # Extract the keys of the object and create a string with the keys separated by '-'
      keys = list(json_obj.keys())
      tag_str = '-'.join(keys)
  
      tag_arr.append(tag_str)
  
      # Iterate over each key in the object
      for key in keys:
          # Add the key to the dictionary if it doesn't exist
          if key not in value_dict:
              value_dict[key] = 0
          # Add the value to the key in the dictionary
          value_dict[key] += json_obj[key]

  #calculate the distance table
  table_size =  len(tag_arr)
  distances = distance_matrix_calculation(tag_arr,table_size)
  #print(distances)

  #tree construction loop when there is more than one tag
  while(table_size != 1):

    #find closest pair and coords of it in the table
    min_value = float('inf')
    min_row = 0
    min_col = 0
    for i in range(len(distances)):
      for j in range(i+1,len(distances[i])):
          if distances[i][j] < min_value:
              min_value = distances[i][j]
              min_row = i
              min_col = j

    #combine the two tags
    aggregated_tags = combination(tag_arr[min_col],tag_arr[min_row])
    #create the tree nodes that will be appended to the tree
    parent_of_childs = Node(aggregated_tags)
    parent_of_childs.left = Node(tag_arr[min_col])
    parent_of_childs.right = Node(tag_arr[min_row])

    #check if one of the string is the root of the tree
    first_tag_is_root = tree_head is not None and tag_arr[min_col] == tree_head.tags
    second_tag_is_root = tree_head is not None and tag_arr[min_row] == tree_head.tags
  
    if tree_head is None:
      #empty tree insert the first tags and set the root as their parent
      insert_right(parent_of_childs, tag_arr[min_col])
      insert_left(parent_of_childs, tag_arr[min_row])
      tree_head = parent_of_childs
  
    elif first_tag_is_root and second_tag_is_root:
      #edge case
      pass
      
    elif first_tag_is_root:
      #if the tag_arr[min_col] is the current root.tags set futures root left child to tag_arr[min_row]
      #and set the future root child to the current root of the tree
      insert_left(parent_of_childs, tag_arr[min_row])
      insert_parent_right(parent_of_childs, tree_head)
      tree_head = parent_of_childs
  
    elif second_tag_is_root:
      #if the tag_arr[min_row] is the current root.tags set futures root left child to tag_arr[min_col]
      #and set the future root child to the current root of the tree
      insert_left(parent_of_childs, tag_arr[min_col])
      insert_parent_right(parent_of_childs, tree_head)
      tree_head = parent_of_childs
  
    else:
      #if none of the two tags are the root.tags then create a new sub tree with the closest pair
      insert_left(parent_of_childs, tag_arr[min_row])
      insert_right(parent_of_childs, tag_arr[min_col])

      #create a new super parent that will be the combination of the closest pair tags and the current root.tags
      super_parent_of_childs = Node(combination(parent_of_childs.tags,tree_head.tags))
      #set the subtree root and the tree_head root as the children of the super parent root
      super_parent_of_childs.left = parent_of_childs
      super_parent_of_childs.right = tree_head
      #set the current tree root as the super parent root
      tree_head = super_parent_of_childs

    #pop the tags from the array and insert their combination
    tag_arr.pop(min_col)
    tag_arr.pop(min_row)
    tag_arr.append(aggregated_tags)

    #decrease the table_size cause of the tags combination
    table_size -= 1
    #update distances table with the distances of the new tag_arr
    distances = distance_matrix_calculation(tag_arr,table_size)

  #print the levels of the tree
  level_order_traversal(tree_head)
  
tree_generation()
