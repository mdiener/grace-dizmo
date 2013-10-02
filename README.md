grace-dizmo
===========

Install
-------

Installing grace-dizmo can be done the same way as **Grace** (https://github.com/mdiener/grace). You do not need to install **Grace** first, as it will be automatically installed as a dependency. You can also grab an executable from http://www.webdiener.ch/grace for Windows, which includes both **Grace** and the dizmo plugin already.

General
-------

**Grace** can also be conveniently used to build and manage dizmos. It allows you to create dizmos, takes care of the plist file for you (you only have to worry about the keys you actually want to adjust, except the mandatory bundle). All commands except help and clean can be used with dizmo as a modifier.
Upon building a new dizmo, there will be a special config file placed in your project directory. It contains only _bundle_ as a key, which represents the bundle your dizmo belongs to. You can then add any other key dizmo supports in that file, and it will be placed into your Info.plist upon building of the dizmo.

**The config file provided needs to include the version of your project, otherwise the building of a dizmo will fail**.

Dizmo
-----

The first module provided is for dizmo development. You can use this by creating a new project with the _--type dizmo_ switch. Other than that, all the commands stay the same.

The dizmo plugin adds additional config options in the project.cfg file. The following is a list of adjustable options:
* development_region: The region you develop your dizmo.
* display_name: The name that is being displayed in your dizmo (title attribute)
* bundle_identifier: Identifier of your dizmo, used for storing and grouping dizmos together.
* width: The initial width of your dizmo.
* height: The initial height of your dizmo.

The following options should not be changed, unless you exactly know what you are doing.
* box_inset_x
* box_inset_y
* api_version
* main_html

JavaScript API wrapper class
----------------------------

The dizmo skeleton provides a JavaScript file called Dizmo.js. This will serve as a basic wrapper around the API provided by dizmos. You can, or should, enhance this class as you start writing more complicated dizmos. The provided wrapper contains the bare essentials and some starts for you to know how and what you can do. It is already included in your main file and can be accessed from there via: _self.getDizmo();_.
The class itself is well documented and you are encouraged to look into it when you have any questions about how it works. Otherwise the following functions should bring you to a point where your dizmo already starts looking good.

### Overview of Dizmo.js (The wrapper around dizmos API)

#### Methods

##### save

```javascript
PROJECTNAME.Dizmo.save(path, value);
```

Saves the provided value in the provided path. This will make it persistent: On a reload of the dizmo, the value will still be at the same place (at the saved path).

##### load

```javascript
PROJECTNAME.Dizmo.load(path);
```

Loads a path that was previously saved with the provided save function. The values loaded are JavaScript types. So if you have saved a number, you will get a number back; if you saved an object, you will get an object back.

##### showFront

```javascript
PROJECTNAME.Dizmo.showFront();
```

Shows the front of the dizmo. This also trigger the event _dizmo.turned_.

##### showBack

```javascript
PROJECTNAME.Dizmo.showBack();
```

Shows the back of the dizmo. This also trigger the event _dizmo.turned_.

### Events

The dizmo class provides a set of predefined events. You can register yourself on these by calling by using the following statement in your code:

```javascript
jQuery(events).on('dizmo.turned', function(e, side) {
    // Do something here
});
```

The _events_ object is provided and only used to attach events to it.

#### dizmo.turned

Triggered when the dizmo is turned to the front side. The events provides the side on which the dizmo has been turned to.

Example:
```javascript
jQuery(events).on('dizmo.turned', function(e, side) {
    if (side === 'front') {
        // do something when turned to front
    } else {
        // do something when turned to back
    }
});
```

#### dizmo.resized

Triggered when the dizmo has been resized (either width or height).

Example:
```javascript
jQuery(events).on('dizmo.resized', function(e, width, height) {
    jQuery(.mycontainer).width(width);
    jQuery(.mycontainer).height(height);
});
```

#### dizmo.onmodechanged

Triggered when the display mode of the viewer has been changed. Possible provided values are: 'presentation', 'edit', 'development'.

Example:
```javascript
jQuery(events).on('dizmo.onmodechanged', function(e, mode) {
    // do something when switched to a different mode
});
```

#### dizmo.docked

Triggered when the dizmo has been docked to another dizmo.

Example:
```javascript
jQuery(events).on('dizmo.docked', function(e) {
    // do something when the dizmo has been docked
});
```

#### dizmo.undocked

Triggered when the dizmo has been undocked.

Example:
```javascript
jQuery(events).on('dizmo.undocked', function(e) {
    // do something when the dizmo has been undocked
});
```

Dizmo Elements
--------------

There are several elements that can be used to style your dizmo in a "dizmo" fashion. The following is a list and usage example of the elements currently provided.
All of these elements can be added to the DOM in the html file. If any of these has their respective data-type, they will automatically be transformed to their widget counterpart. This only works once on the first time the dizmo is instantiated (or reloaded).

### Checkbox

Transforms your checkboxes into dizmo themed checkboxes. No additional events or anything is required to use this. It is solely a cosmetic change.

#### Data-Type
```html
<input type="checkbox" data-type="dizmo-checkbox" />
```

#### Constraints

Works only on checkbox elements.

#### Usage

```javascript
jQuery('.my-checkbox-element').dcheckbox();
```

### Slider

Creates a slider tha can be used as an element. This is only an extension to the jQuery slider plugin (http://jqueryui.com/slider/). Everything that applies to the plugin, usage, etc. does also apply to this widget.

#### Data-Type
```html
<div data-type="dizmo-slider"></div>
```

#### Constraints

All the constraints that apply to the jQuery UI slider apply here too. Please refer to the widget on the jQuery UI site: http://jqueryui.com/slider/.

#### Usage

```javascript
jQuery('.my-slider-div').dslider();
```

The next example shows how to attach an event handler to the slider.

```javascript
jQuery('.my-slider-div').sdlider({
    change: function(e, ui) {
        // Do something on slide change
    }
});

### Selectbox

The selectbox widget enhances a default html selectbox and styles it to fall in line with other dizmo elements.

#### Data-Type
```html
<select data-type="dizmo-selectbox">
    <option value="1">One</option>
    <option value="2">Two</option>
</select>
```

#### Constraints

Everything should work as it does on a default selectbox. The change event is being propagated, so you can just use the default jquery event to interact with the widget. It only works on select elements.
If the underlying element changes, a call to the update function is needed.

#### Usage

```javascript
jQuery('.my-select-element').dselectbox();
```

To update the element when the underlying select changes:
```javascript
jQuery('.my-select-element').dselectbox('update');
```

To set the value programmatically, use the provided value function. This is necessary, because the val() function on the select element from jQuery does not trigger the change event.
```javascript
jQuery('.my-select-element').dselectbox('value', 'b');
```

To get the value, one can either use
```javascript
jQuery('.my-select-element').val();
```
or
```javascript
jQuery('.my-select-element').dselectbox('value');
```

### Switch

A simple on/off switch made from a button. The widget provides some functionality to change the switch and get the current state, as well as set the height and width of the switch.

#### Data-Type
```html
<button data-type="dizmo-switch"></button>
```

#### Constraints

None.

#### Usage

To create the widget, a button element is necessary. It will not work with any other element.

```javascript
jQuery('.my-button-element').dswitch();
```

You can supply the initialisation with additional height, width and theme parameters. There are only two themes available right now: dark and light.

```javascript
jQuery('.my-button-element').dswitch({
    height: 50,
    width: 100,
    theme: 'light'
});
```

To change the state of the button programmatically, call 'state'. The same function is also used to get the current state.

```javascript
jQuery('.my-button-element').dswitch('state', 'off');
jQuery('.my-button-element').dswitch('state', 'on');

var state = jQuery('.my-button-element').dswitch('state');
```

Once initialized, the height and width of the button can be changed through the provided 'height' and 'width' function. The same functions can be used to get the height and width.

```javascript
jQuery('.my-button-element').dswitch('height', 200);
jQuery('.my-button-element').dswitch('width', 100);

var height = jQuery('.my-button-element').dswitch('height');
var width = jQuery('.my-button-element').dswitch('width');
```

### Button

A normal button, styled to match the dizmo theme. Uses either dark or light theme.

#### Data-Type
```html
<button data-type="dizmo-button"></button>
```

#### Constraints

None.

#### Usage

```javascript
jQuery('.my-button-element').dbutton();
jQuery('.my-button-element').dbutton({
    theme: 'light'
});
```
