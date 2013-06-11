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

All the functions, etc. are written as being called inside Main (from the file Main.js).

#### Methods

##### save

```javascript
self.getDizmo().save(path, value);

Saves the provided value in the provided path. This will make it persistent: On a reload of the dizmo, the value will still be at the same place (at the saved path).

##### load

```javascript
self.getDizmo().load(path);
```

Loads a path that was previously saved with the provided save function. The values loaded are JavaScript types. So if you have saved a number, you will get a number back; if you saved an object, you will get an object back.

##### showFront

```javascript
self.getDizmo().showFront();
```

Shows the front of the dizmo. This also trigger the event _dizmo.turned_.

##### showBack

```javascript
self.getDizmo().showBack();
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
