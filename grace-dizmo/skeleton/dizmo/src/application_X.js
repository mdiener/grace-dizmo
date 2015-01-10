//= require Main

/*
Generally you do not need to edit this file. You can start writing
your code in the provided "Main" class.
*/

// Needed for the dizmo menu to work
function showBack() {
    dizmo.showBack();
}

// Needed for the dizmo menu to work
function showFront() {
    dizmo.showFront();
}

// Helper object to attach all the events to
var events = {};

// As soon as the dom is loaded, and the dizmo is ready, instantiate the main class
window.document.addEventListener('dizmoready', function() {
    new ##PROJECTNAME##.Main();
});
