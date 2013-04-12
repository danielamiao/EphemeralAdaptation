from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import random, itertools, os, time

# Classes for the forms used in the views
class DemoForm(forms.Form):
    name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[("F", "Female"), ("M", "Male")], widget=forms.RadioSelect())
    choices = ["", "20-24", "25-39", "30-34", "35-39", "40 and up"]
    age = forms.ChoiceField(choices=[(x,x) for x in choices])
    choices = ["Windows", "Mac", "Linux", "Other"]
    usual_OS_used = forms.MultipleChoiceField(label="Which OS(es) do you normally use?", choices=[(x,x) for x in choices], widget=forms.CheckboxSelectMultiple)
    choices = ["External Mouse", "Touchpad", "Trackpoint", "Other"]
    usual_mouse_used = forms.MultipleChoiceField(label="Which type of mouse do you normally use?", choices=[(x,x) for x in choices], widget=forms.CheckboxSelectMultiple)
    left_handed = forms.BooleanField(label="Are you left-handed?", required=False)

class SurveyForm(forms.Form):
    label = "How difficult did you find this experiment? (0 being Not Difficult At All, 6 being Extremely Difficult)"
    difficulty = forms.ChoiceField(label=label, choices=[(x,x) for x in xrange(7)], widget=forms.RadioSelect())
    label = "How satisfied are you with this experiment? (0 being Not Satisfied At All, 6 being Extremely Satisfied)"
    satisfaction = forms.ChoiceField(label=label, choices=[(x,x) for x in xrange(7)], widget=forms.RadioSelect())
    label = "How efficient were you during this experiment? (0 being Not Efficient At All, 6 being Extremely Efficient)"
    efficiency = forms.ChoiceField(label=label, choices=[(x,x) for x in xrange(7)], widget=forms.RadioSelect())
    label = "How frustrated were you during this experiment? (0 being Not Frustrated At All, 6 being Extremely Frustrated)"
    frustration = forms.ChoiceField(label=label, choices=[(x,x) for x in xrange(7)], widget=forms.RadioSelect())

class FinalForm(forms.Form):
    choices=[("", ""), ("control", "Static Menu (No Predictions)"), ("adaptive", "Adaptive Menu (Has Predictions)")]
    difficulty = forms.ChoiceField(label="Which experiment was more difficult?", choices=choices)
    satisfaction = forms.ChoiceField(label="Which experiment are you more satisfied with?", choices=choices)
    efficiency = forms.ChoiceField(label="Which experiment were you more efficient in?", choices=choices)
    frustration = forms.ChoiceField(label="Which experiment was more frustrating?", choices=choices)

# Read in all the menu group items: 72 in total, at runtime, 12 will be randomly selected 
# and passed to the view for rendering
menu_groups_file = open('ea/static/menu_groups.csv', 'r')
menu_groups = []
for row in menu_groups_file:
    menu_groups.append(row.strip().split(','))
menu_groups_file.close()

#
# define constant variables for the entire RS assignment
#

#INIT variable keeps track of which experiment is first (control or adaptive)
INIT = '' 

#NUM_TRIALS specifies how many trials will be run in total
NUM_TRIALS = 12

#TRIAL_SEQ counterbalances the experimental trials
TRIAL_SEQ = []
for _ in itertools.repeat(None, NUM_TRIALS/2):
    TRIAL_SEQ.append(0)
for _ in itertools.repeat(None, NUM_TRIALS/2):
    TRIAL_SEQ.append(1)
random.shuffle(TRIAL_SEQ)

#DISTRIBUTION specifies the frequency of each menu item in the task sequence
#it is also used to determine how long the task sequence is (since the number
#means how many times a menu item is repeated)
DISTRIBUTION = [15, 8, 5, 4, 3, 3, 2, 2] #zipf distribution

#TUT_LENGTH specifies how many task items are in the tutorial
TUT_LENGTH = 8

#NUM_PRED defines how many predictions to make for the adaptive menu
NUM_PRED = 3

# define global variables used in each experiment
control_sequence = []
frequent_items = [[], [], []] # 3 possible permutations of frequent items
exp_no = 0

# index renders the home page of the experiment
def index(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

# record is a function that writes the given message to a file, if there 
# are existing files when the first line (header) is written, move those to
# a newly created directory based on timestamp
def record(request):
    message = request.GET['data']
    if message == "condition correctness target selected time target_predicted selected_predicted":
        cur_dir = "ea/data"
        new_dir = time.strftime("results_%Y%m%d%H%M%S")
        for file in os.listdir(cur_dir):
            if "log" in file:
                try:
                    old = cur_dir + '/' + file
                    new = cur_dir + '/' + new_dir + '/'+ file
                    os.renames(old, new)
                except Error:
                    print Error
    with open('ea/data/output.log', 'a+') as f:
        f.write(message + '\n')
    return HttpResponse("message written to file")

# renders the Demographic Survey page
def demosurvey(request):
    if request.method == 'POST': # If the form has been submitted...
        form = DemoForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            with open('ea/data/demosurvey.log', 'w+') as f:
                for key in form.cleaned_data:
                    entry = form.cleaned_data[key]
                    f.write(key + ': ' + str(entry) + '\n') 
            if TRIAL_SEQ[exp_no] == 0: 
                return HttpResponseRedirect('control/tut') #half of the time the control condition is first
            else:
                return HttpResponseRedirect('adaptive/tut') #half of the time the adaptive condition is first
    else:
        form = DemoForm() # An unbound form

    return render(request, 'demosurvey.html', {'form': form})

# renders the Subjective Survey for each condition
def survey(request, cond):
    if request.method == 'POST': # If the form has been submitted...
        form = SurveyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            with open('ea/data/' + cond +'_survey.log', 'w+') as f:
                for key in form.cleaned_data:
                    entry = form.cleaned_data[key]
                    f.write(key + ': ' + str(entry) + '\n') 
            if cond == 'control':
                if TRIAL_SEQ[exp_no] == 0:
                    return HttpResponseRedirect('adaptive/tut') # Redirect after POST
                else:
                    return HttpResponseRedirect('finalsurvey') # Redirect after POST
            else:
                if TRIAL_SEQ[exp_no] == 0:
                    return HttpResponseRedirect('finalsurvey') # Redirect after POST
                else:
                    return HttpResponseRedirect('control/tut') # Redirect after POST
    else:
        form = SurveyForm() # An unbound form

    return render(request, 'survey.html', {'form': form})

# renders the Comparative Survey at the end of the experiment
def finalsurvey(request):
    if request.method == 'POST': # If the form has been submitted...
        form = FinalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            with open('ea/data/final_survey.log', 'w+') as f:
                for key in form.cleaned_data:
                    entry = form.cleaned_data[key]
                    f.write(key + ': ' + str(entry) + '\n') 
            return HttpResponseRedirect('done') # Redirect after POST
    else:
        form = FinalForm() # An unbound form

    return render(request, 'finalsurvey.html', {'form': form})

# render the Control Condition Experiment Page (could be tutorial or regular)
def control(request, tut):
    # if sequence not generated yet, generate a random task sequence, length SEQ_LENGTH
    # if it is generated, permute it so that sequence doesn't change, but menu item 
    # is simply switched to the same item of a different menu
    global control_sequence, INIT
    if not control_sequence: 
        control_sequence = gen_sequence()
        sequence = control_sequence
        INIT = 'control'
    else:
        if INIT == 'control':
            sequence = control_sequence;
        else:
            (sequence,permute_by) = permute_sequence(control_sequence)

    # if it's the tutorial page, truncate task sequence to TUT_LENGTH elements only
    if tut == 'tut':
        sequence = control_sequence[:TUT_LENGTH]
        tut = 1
    else: 
        tut = 0
    return render_to_response('control_menu.html', 
                              {'menu':random.sample(menu_groups, 12), 'sequence':sequence, 'tut':tut},
                              context_instance=RequestContext(request))

# render the Adaptive Condition Experiment Page (could be tutorial or regular)
def adaptive(request, tut):
    # if sequence not generated yet, generate a random task sequence, length SEQ_LENGTH
    # if it is generated, permute it so that sequence doesn't change, but menu item 
    # is simply switched to the same item of a different menu
    global control_sequence, INIT
    if not control_sequence: 
        control_sequence = gen_sequence()
        sequence = control_sequence
        predictions = get_predictions(sequence, permute_no=0)
        INIT = 'adaptive'
    else:
        if INIT == 'adaptive':
            sequence = control_sequence;
            predictions = get_predictions(sequence, permute_no=0)
        else:
            (sequence, permute_by) = permute_sequence(control_sequence)
            predictions = get_predictions(sequence, permute_no=permute_by)
    accuracy_count(sequence,predictions)
    # if it's the tutorial page, truncate task sequence to TUT_LENGTH elements only
    if tut == 'tut':
        sequence = sequence[:TUT_LENGTH]
        tut = 1
    else:
        tut = 0
    return render_to_response('adaptive_menu.html', 
                              {'menu':random.sample(menu_groups, 12), 'sequence':sequence, 'predictions':predictions, 'tut': tut},
                              context_instance=RequestContext(request))

# Renders the Experiment Completed page, reset the INIT and control_sequence for next experimenth
# increment experiment number for the next experiment
def done(request):
    global INIT, control_sequence, exp_no
    INIT = ''
    control_sequence = []
    exp_no = (exp_no+1) % 12
    return render_to_response('done.html', {}, context_instance=RequestContext(request))

# Generates the task sequence to be selected by the user
# For each of the 3 menus, 8 items are randomly selected (recall total number of items is 16)
# A zipf distribution is used over the 8 items such that frequency is: 15, 8, 5, 4, 3, 3, 2, 2
# Altogether, this makes a task sequence of length 126 
def gen_sequence():
    global frequent_items
    distribution = DISTRIBUTION #use the EXPERIMENT CONSTANT
    len_dist = len(DISTRIBUTION)
    sequence = []
    menu_index = 0
    # Menu 1
    menu1_list = range(0,16)
    sampled_menu1_list = random.sample(menu1_list, len_dist)
    for index, item in enumerate(sampled_menu1_list):
        for _ in itertools.repeat(None, distribution[index]):
            sequence.append(item)   
    
    # Menu 2
    menu2_list = range(16,32)
    sampled_menu2_list = random.sample(menu2_list, len_dist)
    for index, item in enumerate(sampled_menu2_list):
        for _ in itertools.repeat(None, distribution[index]):
            sequence.append(item)
    
    # Menu 3
    menu3_list = range(32,48)
    sampled_menu3_list = random.sample(menu3_list, len_dist)
    for index, item in enumerate(sampled_menu3_list):
        for _ in itertools.repeat(None, distribution[index]):
            sequence.append(item)
    
    # The 3 most frequently selected items are stored for prediction use later
    populate_freq_items(sampled_menu1_list[:NUM_PRED], sampled_menu2_list[:NUM_PRED], sampled_menu3_list[:NUM_PRED])
    random.shuffle(sequence)
    return sequence

# populate the frequent_items list so that we have all permutations of frequent items
# available to us, the input parameters are the default frequent items for control sequence
# frequent_items is populated as such: frequent_items = [[control_sequence],[permute_by_1],[permute_by_2]]
def populate_freq_items(menu1, menu2, menu3):
    global frequent_items
    control_seq_freq_items = [menu1[:], menu2[:], menu3[:]]
    
    menu1 = permute_by_one(menu1)
    menu2 = permute_by_one(menu2)
    menu3 = permute_by_one(menu3)
    
    permute_one_freq_items = [menu3[:], menu1[:], menu2[:]]
    menu1 = permute_by_one(menu1)
    menu2 = permute_by_one(menu2)
    menu3 = permute_by_one(menu3)
    
    permute_two_freq_items = [menu2[:], menu3[:], menu1[:]]
    frequent_items = [control_seq_freq_items, permute_one_freq_items, permute_two_freq_items]    
    
# permute all menu items by 1 menu, so that item 1 of menu 1 is now item 1 of menu 2 etc.
# the mod operator is used to make sure items of menu 3 wraps back around to be items of menu 1
def permute_by_one(menu): 
    new_menu = []
    for item in menu:
        new_menu.append((item + 16) % 48)
    return new_menu

# Permute the sequence for the second condition to prevent individuals from remembering 
# the sequence across conditions. For examples, if the first selection in the first 
# condition was Menu 1 > Item 3, then in the second condition the first selection would
# be either Menu 2 > Item 3 or Menu 3 > Item 3
def permute_sequence(sequence):
    permuted_sequence = []
    permute_by = random.randint(1,2) # random choose whether we want to permute by 1 or 2
    
    # the idea is to add either 16 or 32 to the sequence number randomly, then mod 48 to 
    # ensure it stays within the range [0,47] --> total of 48 menu items
    for elem in sequence:
        permuted_sequence.append((elem + 16 * permute_by) % 48) 
    return (permuted_sequence, permute_by)

# populate the predictions list so we have 3 predictions for each item in the task sequence
# the predictions are first chosen by filling it with the 3 most frequently selected items
# in that menu. Then, the most recently selected menu item in the task sequence replaces the 
# "least" frequent item out of the 3. Finally, the accuracy of the predictions is increased
# by manually correcting incorrect predictions
def get_predictions(sequence, permute_no):
    predictions = []
    recent_item = dict.fromkeys([0,1,2])
    
    for item in sequence:
        if item < 16:
            menu = 0
        elif item < 32:
            menu = 1
        elif item < 48:
            menu = 2
        else:
            predictions = []
            return predictions
        
        predicted_set = frequent_items[permute_no][menu][:]
        if recent_item[menu] is not None and recent_item[menu] not in predicted_set:
            predicted_set[NUM_PRED-1] = recent_item[menu] #replace the least frequent item with the most recently selected item
        recent_item[menu] = item
        predictions.append(predicted_set)
    
    # adjust accuracy of the predictions
    adjusted_predictions = adjust_predictions(sequence, predictions)
    return adjusted_predictions

# adjust predictions so that accuracy is 79%, as reported in the paper
# basically make a pass through the sequence to find all the incorrect
# predictions first, then randomly choose 18 to adjust
def adjust_predictions(sequence, predictions):
    target_accuracy = 0.79
    cur_accuracy = 0.645
    length = len(sequence)
    
    wrong_predictions = []    
    for index in xrange(length):
        if sequence[index] not in predictions[index]:
            wrong_predictions.append(index)

    num_adjust = int((target_accuracy - cur_accuracy) * len(sequence))
    items_adjust = random.sample(wrong_predictions,num_adjust)
    for item in items_adjust:
        if sequence[item] < 16:
            menu = 0
        elif sequence[item] < 32:
            menu = 1
        elif sequence[item] < 48:
            menu = 2
        
        if predictions[item][NUM_PRED-1] == get_recent_item(sequence, menu, item): # if the last prediction item is the most recently selected item
            predictions[item][NUM_PRED-2] = sequence[item] #replace the 2nd prediction item so the most recently selected item is kept
        else:
            predictions[item][NUM_PRED-1] = sequence[item]
            
    return predictions
    
def get_recent_item(sequence, menu, item_no):
    if menu == 0:
        item_range = range(0,16)
    elif menu == 1: 
        item_range = range(16,32)
    elif menu == 2:
        item_range = range(32,48)
    else:
        return -1
    while item_no > 0:
        item_no -= 1
        if sequence[item_no] in item_range:
            return sequence[item_no]
    return -1
        
# count the actual accuracy
def accuracy_count(sequence,predictions):
    count = 0
    for index,item in enumerate(sequence):
        if item in predictions[index]:
            count = count + 1
    print count/(len(sequence)+0.0)
    return count


    
    
