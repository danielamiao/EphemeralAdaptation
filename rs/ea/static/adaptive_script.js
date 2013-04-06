// variables for the basic dropdown menu
var timeout = 300;
var closetimer = 0;
var menuitem = 0;

// variables for the menu item selection
// var sequence = [0, 4, 5, 16, 9, 13, 15, 0, 17, 4];
// var predictions = [[0, 5, 2],
//     		[4, 1, 3],
// 		[5, 2, 3],
// 		[17, 12, 13],
// 		[7, 8, 11],
// 		[12, 14, 17],
// 		[15, 16, 17],
// 		[1, 5, 4],
// 		[13, 14, 15],
// 		[0, 4, 5]
// 		]
var curpos = -1;
var target = '-1';

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

	// update the start timer in case the user clicks on something here
	myDate = new Date();
	starttime = myDate.getTime();
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
		var message = 'right ' + target + ' ' + itemid + ' ' + elapsed_time;
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
		var message = 'wrong ' + target + ' ' + itemid + ' ' + elapsed_time;
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
	document.getElementById('endbox').innerHTML = "Congratulations! You are done this section, click on continue to continue onto the next section!";
}

// close the menus whenever the user clicks on the page
document.onclick = closemenu();

// show the first task selection item, this process starts as soon as the page is loaded
window.onload = function() { 
	curpos = 0;
	settarget(sequence[curpos]); 
}
