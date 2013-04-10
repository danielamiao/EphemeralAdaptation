// variables for the basic dropdown menu
var timeout = 300;
var closetimer = 0;
var menuitem = 0;
var curpos = -1;
var target = '-1';
var menu_opened = 0;

// variables of the timer
var myDate = new Date();
var starttime = myDate.getTime();
var endtime = myDate.getTime();

function addfadeinclass(array) {
	for (var i=0; i<array.length; i++) {
		var element = document.getElementById(array[i].toString());
		element.classList.add('fadein');
	}
}

function removefadeinclass(array) {
	for (var i=0; i<array.length; i++) {
		var element = document.getElementById(array[i].toString());
		element.classList.remove('fadein');
	}
}

function settarget(target_id) {
	// the target_id is usually passed in as a number only
	target = target_id.toString();
	
	// figure out the menu and item name of the target and display it on the page
        var item = document.getElementById(target);
        var itemname = item.innerHTML;
        var menuname = item.parentNode.parentNode.parentNode.firstChild.innerHTML;
        var heading = document.getElementById('targetbox');
        heading.innerHTML = menuname + ' > ' + itemname;

	// set the predictions to show up right away instead of fading in
	removefadeinclass(this.predictions[curpos]);
}

// open the selected menu
function openmenu(id) {
	// cancel the close timer
	cancelclosetimer();
	
	// close any opened menus 
	closemenu();

	// get the new menu layer and show it
	menuitem = document.getElementById(id);
	// menuitem.style.visibility = 'visible';
	menuitem.style.visibility = 'visible';
	var itemarray = menuitem.getElementsByTagName('a');
	for (var i=0; i < itemarray.length; i++) {
		itemarray[i].style.opacity = 1;
	}

	if (menu_opened == 0) {
		// update the start timer if this is the first time user opens a menu 
		myDate = new Date();
		starttime = myDate.getTime();
	}
}

// close opened menus
function closemenu() {
	if (menuitem) {
		menuitem.style.visibility = 'hidden';
		var itemarray = menuitem.getElementsByTagName('a');
		for (var i=0; i < itemarray.length; i++) {
			itemarray[i].style.opacity = 0;
		}
	}
}

// set close timer
function setclosetimer() {
	closetimer = window.setTimeout(closemenu, timeout);
}

// cancel close timer
function cancelclosetimer() {
	if(closetimer) {
		window.clearTimeout(closetimer);
		closetimer = null;
	}
}

// item selected, check for correctness and log
function selectitem(itemid) {
	// first close the menu for good aesthetics
	closemenu();
	myDate = new Date();
	endtime = myDate.getTime()
	var elapsed_time = endtime - starttime;

	if (target === itemid) {
		// record the time taken to select the item
		// if this is the correct selection, log the time 
		menu_opened = 0;
		var message = 'adaptive right ' + target + ' ' + itemid + ' ' + elapsed_time;
		console.log(message);

		$.ajax({
			type:"GET",
			url:"record",
			data: {
				'data': message,
			},      
		});
		
		// reinitialize the fadein class (default all fade so remove the previous predictions)	
		addfadeinclass(predictions[curpos]);	

		// if this is the last time, show the end for user to move on
		if (curpos === sequence.length-1) {
			showend();
		} 

		// otherwise, set the target to be the next in the task sequence
		else {
			settarget(sequence[++curpos]); 
		}
	}
	else { 
		// if this is not the correct selection, log the time and the error
		var message = 'adaptive wrong ' + target + ' ' + itemid + ' ' + elapsed_time;
		console.log(message);

		$.ajax({
			type:"GET",
			url:"record",
			data: {
				'data': message,
			},      
		});
	}
}

function showend() {
	document.getElementById('endbox').style.display = 'block';
}

// close the menus whenever the user clicks on the page
document.onclick = closemenu();

// show the first task selection item, this process starts as soon as the page is loaded
window.onload = function() { 
	curpos = 0;
	settarget(sequence[curpos]); 
}
