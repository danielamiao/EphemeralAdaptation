from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
import random, itertools, os, time

# Classes for the forms used in the views
class DemoForm(forms.Form):
    name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[("F", "Female"), ("M", "Male")], widget=forms.RadioSelect())
    choices = ["20-24", "25-39", "30-34", "35-39", "40 and up"]
    age = forms.ChoiceField(choices=[(x,x) for x in choices])
    choices = ["Windows", "Mac", "Linux", "Other"]
    usual_OS_used = forms.MultipleChoiceField(choices=[(x,x) for x in choices], widget=forms.CheckboxSelectMultiple)
    left_handed = forms.BooleanField(required=False)

class SurveyForm(forms.Form):
    difficulty = forms.ChoiceField(choices=[(0, "Not Difficult At All"), (1, ""), (2, ""), (3, ""), (4, "Very Difficult")], widget=forms.RadioSelect())
    satisfaction = forms.ChoiceField(choices=[(0, "Not Satisfied At All"), (1, ""), (2, ""), (3, ""), (4, "Very Satisfied")], widget=forms.RadioSelect())
    efficiency = forms.ChoiceField(choices=[(0, "Not Efficient At All"), (1, ""), (2, ""), (3, ""), (4, "Very Efficient")], widget=forms.RadioSelect())
    frustration = forms.ChoiceField(choices=[(0, "Not Frustrated At All"), (1, ""), (2, ""), (3, ""), (4, "Very Frustrated")], widget=forms.RadioSelect())

class FinalForm(forms.Form):
    difficulty = forms.ChoiceField(label="Which experiment was more difficult?", choices=[("control", "No FadeIn Menu Items"), ("adaptive", "FadeIn Menu Items")])
    satisfaction = forms.ChoiceField(label="Which experiment are you more satisfied with?", choices=[("control", "No FadeIn Menu Items"), ("adaptive", "FadeIn Menu Items")])
    efficiency = forms.ChoiceField(label="Which experiment were you more efficient in?", choices=[("control", "No FadeIn Menu Items"), ("adaptive", "FadeIn Menu Items")])
    frustration = forms.ChoiceField(label="Which experiment was more frustrating?", choices=[("control", "No FadeIn Menu Items"), ("adaptive", "FadeIn Menu Items")])

# Create your views here.

# Read in all the menu group items: 72 in total, at runtime, 12 will be randomly selected 
# and passed to the view for rendering
menu_groups_file = open('ea/static/menu_groups.csv', 'r')
menu_groups = []
for row in menu_groups_file:
    menu_groups.append(row.strip().split(','))
menu_groups_file.close()

# define constant variables for the experiment
INIT = ''
EXPERIMENT_SIZE = 12
EXPERIMENT_SEQ = []
for _ in itertools.repeat(None, EXPERIMENT_SIZE/2):
    EXPERIMENT_SEQ.append(0)
for _ in itertools.repeat(None, EXPERIMENT_SIZE/2):
    EXPERIMENT_SEQ.append(1)
random.shuffle(EXPERIMENT_SEQ)

# define global variables used in the experiment
control_sequence = []
frequent_items = [[], [], []] # 3 possible permutations of frequent items
exp_no = 0


def index(request):
    return render_to_response('index.html')

def record(request):
    message = request.GET['data']
    if message == "Experiment Begins":
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
    return HttpResponse("yay")

def demosurvey(request):
    if request.method == 'POST': # If the form has been submitted...
        form = DemoForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            print form.cleaned_data
            with open('ea/data/demosurvey.log', 'w+') as f:
                for key in form.cleaned_data:
                    entry = form.cleaned_data[key]
                    f.write(key + ': ' + str(entry) + '\n') 
            if EXPERIMENT_SEQ[exp_no] == 0:
                return HttpResponseRedirect('/ea/control/tut') # Redirect after POST
            else:
                return HttpResponseRedirect('/ea/adaptive/tut') # Redirect after POST
    else:
        form = DemoForm() # An unbound form

    return render(request, 'demosurvey.html', {
        'form': form,
    })
    
def survey(request, cond):
    if request.method == 'POST': # If the form has been submitted...
        form = SurveyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            print form.cleaned_data
            with open('ea/data/' + cond +'_survey.log', 'w+') as f:
                for key in form.cleaned_data:
                    entry = form.cleaned_data[key]
                    f.write(key + ': ' + str(entry) + '\n') 
            if cond == 'control':
                if EXPERIMENT_SEQ[exp_no] == 0:
                    return HttpResponseRedirect('/ea/adaptive/tut') # Redirect after POST
                else:
                    return HttpResponseRedirect('/ea/finalsurvey') # Redirect after POST
            else:
                if EXPERIMENT_SEQ[exp_no] == 0:
                    return HttpResponseRedirect('/ea/finalsurvey') # Redirect after POST
                else:
                    return HttpResponseRedirect('/ea/control/tut') # Redirect after POST
    else:
        form = SurveyForm() # An unbound form

    return render(request, 'survey.html', {
        'form': form,
    })

def finalsurvey(request):
    if request.method == 'POST': # If the form has been submitted...
        form = FinalForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            print form.cleaned_data
            with open('ea/data/final_survey.log', 'w+') as f:
                for key in form.cleaned_data:
                    entry = form.cleaned_data[key]
                    f.write(key + ': ' + str(entry) + '\n') 
            return HttpResponseRedirect('/ea/done') # Redirect after POST
    else:
        form = FinalForm() # An unbound form

    return render(request, 'finalsurvey.html', {
        'form': form,
    })

def control(request, tut):
    # if sequence not generated, generate a random task sequence, 126 in length
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

    # if it's the tutorial page, truncate task sequence to 8 elements only
    if tut == 'tut':
        sequence = control_sequence[:8]
    return render_to_response('control_menu.html', 
                              {'menu':random.sample(menu_groups, 12), 'sequence':sequence, 'tut':tut},
                              context_instance=RequestContext(request))

def adaptive(request, tut):
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

    # if it's the tutorial page, truncate task sequence to 8 elements only
    if tut == 'tut':
        sequence = sequence[:8]
    return render_to_response('adaptive_menu.html', 
                              {'menu':random.sample(menu_groups, 12), 'sequence':sequence, 'predictions':predictions, 'tut': tut},
                              context_instance=RequestContext(request))

def done(request):
    global INIT, exp_no
    INIT = ''
    exp_no = (exp_no+1) % 12
    print EXPERIMENT_SEQ
    print exp_no
    return render_to_response('done.html')

# Generates the task sequence to be selected by the user
# For each of the 3 menus, 8 items are randomly selected (recall total number of items is 16)
# A zipf distribution is used over the 8 items such that frequency is: 15, 8, 5, 4, 3, 3, 2, 2
# Altogether, this makes a task sequence of length 126 
def gen_sequence():
    global frequent_items
    distribution = [15, 8, 5, 4, 3, 3, 2, 2]
    sequence = []
    menu_index = 0
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
    
    populate_freq_items(sampled_menu1_list[:3], sampled_menu2_list[:3], sampled_menu3_list[:3])
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
    #print frequent_items
    
def permute_by_one(menu): 
    new_menu = []
    for item in menu:
        new_menu.append((item + 16) % 48)
    return new_menu

# Permute the sequence for the adaptive condition to prevent individuals from remembering 
# the sequence across conditions. For examples, if the first selection in the control 
# condition was Menu 1 > Item 3, # then in the adaptive condition the first selection would
# be either Menu 2 > Item 3 or Menu 3 > Item 3
def permute_sequence(sequence):
    permuted_sequence = []
    permute_by = random.randint(1,2)
    
    # the idea is to add either 16 or 32 to the sequence number randomly, then mod 48 to 
    # ensure it stays within the range [0,47]
    for elem in sequence:
        permuted_sequence.append((elem + 16 * permute_by) % 48) 
    return (permuted_sequence, permute_by)

def get_predictions(sequence, permute_no):
    predictions = []
    recent_item = dict.fromkeys([0,1,2])
    #import pdb; pdb.set_trace()
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
            predicted_set[2] = recent_item[menu]
        recent_item[menu] = item
        predictions.append(predicted_set)
    
    adjusted_predictions = adjust_predictions(sequence, predictions, recent_item)
    return adjusted_predictions

# adjust predictions so that accuracy is 79%, as reported in the paper
def adjust_predictions(sequence, predictions, recent_item):
    target_accuracy = 0.79
    cur_accuracy = 0.645
    length = len(sequence)
    
    wrong_predictions = []    
    for index in xrange(length):
        if sequence[index] not in predictions[index]:
            wrong_predictions.append(index)
    print len(wrong_predictions)
    num_adjust = int((target_accuracy - cur_accuracy) * len(sequence))
    items_adjust = random.sample(wrong_predictions,num_adjust)
    for item in items_adjust:
        if sequence[item] < 16:
            menu = 0
        elif sequence[item] < 32:
            menu = 1
        elif sequence[item] < 48:
            menu = 2
        
        if predictions[item][2] == recent_item[menu]:
            predictions[item][2] = sequence[item]
        else:
            predictions[item][1] = sequence[item]
            
    return predictions
    
# count the actual accuracy
def accuracy_count(sequence,predictions):
    count = 0
    for index,item in enumerate(sequence):
        if item in predictions[index]:
            count = count + 1
    return count


    
    
