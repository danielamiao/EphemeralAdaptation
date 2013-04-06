from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import random
import itertools

# Create your views here.

# Read in all the menu group items: 72 in total, at runtime, 12 will be randomly selected 
# and passed to the view for rendering
menu_groups_file = open('ea/static/menu_groups.csv', 'r')
menu_groups = []
for row in menu_groups_file:
    menu_groups.append(row.strip().split(','))
menu_groups_file.close()

# define a global variable for task sequence
control_sequence = []

def index(request):
    return render_to_response('index.html')

def record(request):
    elapsed_time = request.GET['data']
    with open('ea/data/output.log', 'a+') as f:
        f.write(elapsed_time + '\n')
    return HttpResponse("yay")

def control(request, tut):
    # generate a random task sequence, 126 in length
    global control_sequence
    control_sequence = gen_sequence()
    
    # if it's the tutorial page, truncate task sequence to 8 elements only
    if tut == 'tut':
        del control_sequence[8:]
    return render_to_response('control_menu.html', 
                              {'menu':random.sample(menu_groups, 12), 'sequence':control_sequence},
                              context_instance=RequestContext(request))

def adaptive(request, tut):
    # need to permute the sequence such that sequence don't change, but menu item is simply
    # switched to the same item of a different menu (see function permute_sequence for details)
    global control_sequence
    sequence = permute_sequence(control_sequence)
    
    # get the predictions based on the sequence, and a given accuracy percentage
    predictions = get_predictions(sequence, accuracy=79)
    
    # if it's the tutorial page, truncate task sequence to 8 elements only
    if tut == 'tut':
        del sequence[8:]
    return render_to_response('adaptive_menu.html', 
                              {'menu':random.sample(menu_groups, 12), 'sequence':sequence, 'predictions':predictions},
                              context_instance=RequestContext(request))

def exit_survey(request):
    return render_to_response('exit_survey.html')

# Generates the task sequence to be selected by the user
# For each of the 3 menus, 8 items are randomly selected (recall total number of items is 16)
# A zipf distribution is used over the 8 items such that frequency is: 15, 8, 5, 4, 3, 3, 2, 2
# Altogether, this makes a task sequence of length 126 
def gen_sequence():
    distribution = [15, 8, 5, 4, 3, 3, 2, 2]
    sequence = []
    # Menu 1
    menu1_list = range(0,16)
    sampled_menu1_list = random.sample(menu1_list, 8)
    for index, item in enumerate(sampled_menu1_list):
        for _ in itertools.repeat(None, distribution[index]):
            sequence.append(item)
            
    # Menu 2
    menu2_list = range(16,32)
    sampled_menu2_list = random.sample(menu2_list, 8)
    for index, item in enumerate(sampled_menu2_list):
        for _ in itertools.repeat(None, distribution[index]):
            sequence.append(item)
            
    # Menu 3
    menu3_list = range(32,48)
    sampled_menu3_list = random.sample(menu3_list, 8)
    for index, item in enumerate(sampled_menu3_list):
        for _ in itertools.repeat(None, distribution[index]):
            sequence.append(item)
            
    random.shuffle(sequence)
    return sequence

# Permute the sequence for the adaptive condition to prevent individuals from remembering 
# the sequence across conditions. For examples, if the first selection in the control 
# condition was Menu 1 > Item 3, # then in the adaptive condition the first selection would
# be either Menu 2 > Item 3 or Menu 3 > Item 3
def permute_sequence(sequence):
    permuted_sequence = []
    for elem in sequence:
        # the idea is to add either 16 or 32 to the sequence number randomly, then mod 48 to 
        # ensure it stays within the range [0,47]
        permuted_sequence.append((elem + 16 * random.randint(1,2)) % 48) 
    return permuted_sequence

def get_predictions(sequence, accuracy):
    predictions = generate_predictions(sequence)
    adjusted_predictions = adjust_predictions(predictions, accuracy)
    return adjusted_predictions

def generate_predictions(sequence):
    predictions = []
    for item in sequence:
        if item < 16:
            predicted_set = random.sample(range(0,16), 3)
            if item not in predicted_set:
                predicted_set[0] = item
            predictions.append(predicted_set)
        elif item < 32:
            predicted_set = random.sample(range(16,32), 3)
            if item not in predicted_set:
                predicted_set[0] = item
            predictions.append(predicted_set)            
        elif item < 48:
            predicted_set = random.sample(range(32,48), 3)
            if item not in predicted_set:
                predicted_set[0] = item
            predictions.append(predicted_set)    
        else:
            predictions = []
            return predictions
    return predictions

def adjust_predictions(predictions, accuracy):
    length = len(predictions)
    num_adjust = int((1-float(accuracy)/100) * length)
    items_adjust = random.sample(range(0,length),num_adjust)
    for item in items_adjust:
        first_num = predictions[item][0]
        if first_num < 16:
            list_a = range(0,16)
            for elem in predictions[item]:
                list_a.remove(elem)
            predictions[item] = random.sample(list_a,3)
        elif first_num < 32:
            list_b = range(16,32)
            for elem in predictions[item]:
                list_b.remove(elem)
            predictions[item] = random.sample(list_b,3)
        elif first_num < 48:
            list_c = range(32,48)
            for elem in predictions[item]:
                list_c.remove(elem)
            predictions[item] = random.sample(list_c,3)
        else:
            return None
    return predictions
    
    
    
    
