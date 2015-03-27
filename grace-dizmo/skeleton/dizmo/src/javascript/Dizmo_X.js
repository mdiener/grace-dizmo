/**
 * @class The custom wrapper around the provided dizmo API
 *
 * @description
 * This class serves as a basis for a custom wrapper around the dizmo API. It should be extended by the developer and can be used as a reference as to how an interaction with the API could work out. Some basic events are already programmed and can be used.
 */
Class("##PROJECTNAME##.Dizmo", {
    my: {
        methods: {
            /**
             * Shows the back of the dizmo
             * @static
             */
            showBack: function() {
                dizmo.showBack();
            },

            /**
             * Shows the front of the dizmo
             * @static
             */
            showFront: function() {
                dizmo.showFront();
            },

            /**
             * Get the ID of the underlying dizmo
             * @return {String} ID of the dizmo
             */
            getId: function() {
                return dizmo.identifier;
            },

            /**
             * Load the value saved at the given path. If no value is saved
             * in this path, return null.
             * @param  {String} path The path to look for a value
             * @return {*}      Value that is saved in the given type
             * @static
             */
            load: function(path) {
                var self = this;

                return dizmo.privateStorage.getProperty(path);
            },

            /**
             * Saves a value in the given path.
             * @param {String} path  The path to save the value to
             * @param {*}  value The value to save
             * @static
             */
            save: function(path, value) {
                var self = this;

                dizmo.privateStorage.setProperty(path, value);
            },

            /**
             * Set the title of the dizmo
             * @param {String} value Title of the dizmo
             * @static
             */
            setTitle: function(value) {
                if (jQuery.type(value) === 'string') {
                    dizmo.setAttribute('settings/title', value);
                }
            },

            /**
             * Publish the path with the chosen value. If no path is specified, meaning if
             * the function is called with only value, it will use the standard publish path
             * 'stdout'.
             * @param  {String} path   The path to publish to
             * @param  {*}  value  The value to set the publish path to
             * @static
             */
            publish: function(path, value) {
                var self = this;

                if (jQuery.type(path) === 'undefined') {
                    return;
                }

                if (jQuery.type(value) === 'undefined') {
                    value = path;
                    path = 'stdout';
                }

                dizmo.publicStorage.setProperty(path, value);
            },

            /**
             * Delete the published path. If no path is specified, it will delete the standard
             * path 'stdout'.
             * @param  {String} path Path to remove from publishing
             * @static
             */
            unpublish: function(path) {
                if (jQuery.type(path) === 'undefined') {
                    path = 'stdout';
                }

                dizmo.publicStorage.deleteProperty(path);
            },

            /**
             * @return {Object} The size of the dizmo as width and height
             * @static
             */
            getSize: function() {
                return dizmo.getSize();
            },

            /**
             * Set the size of the dizmo
             * @param {Number} width  The width of the dizmo
             * @param {Number} height The height of the dizmo
             * @static
             */
            setSize: function(width, height) {
                if (jQuery.type(width) !== 'number') {
                    throw 'Please provide only numbers for width!'
                }
                if (jQuery.type(height) !== 'number') {
                    throw 'Please provide only numbers for height!'
                }

                dizmo.setSize(width, height);
            },

            subscribe: function(path, callback) {
                var self = this;

                if (jQuery.type(callback) !== 'function') {
                    console.log('Please only provide a function as the callback.');
                    return null;
                }
                if (jQuery.type(path) !== 'string') {
                    console.log('Please only provide a string as the path.');
                    return null;
                }

                var id = null;
                id = dizmo.privateStorage.subscribeTo(path, function(path, val, oldVal) {
                    callback.call(self, val, oldVal);
                });

                return id;
            },

            unsubscribe: function(id) {
                dizmo.privateStorage.unsubscribe(id);
            }
        }
    },

    after: {
        /**
         * Called after the internal initialize method
         * @private
         */
        initialize: function() {
            var self = this;

            self.setAttributes();
            self.initEvents();
        }
    },

    methods: {
        /**
         * Initiate all the events for dizmo related stuff
         * @private
         */
        initEvents: function() {
            var self = this;

            // Show back and front listeners
            dizmo.onShowBack(function() {
                jQuery("#front").hide();
                jQuery("#back").show();
                jQuery(events).trigger('dizmo.turned', ['back']);
            });

            dizmo.onShowFront(function() {
                jQuery("#back").hide();
                jQuery("#front").show();
                jQuery(events).trigger('dizmo.turned', ['front']);
            });

            // Subscribe to height changes of the dizmo
            dizmo.subscribeToAttribute('geometry/height', function(path, val, oldVal) {
                jQuery(events).trigger('dizmo.resized', [dizmo.getWidth(), dizmo.getHeight()]);
            });

            // Subscribe to width changes of the dizmo
            dizmo.subscribeToAttribute('geometry/width', function(path, val, oldVal) {
                jQuery(events).trigger('dizmo.resized', [dizmo.getWidth(), dizmo.getHeight()]);
            });

            // Subscribe to displayMode changes
            viewer.subscribeToAttribute('settings/displaymode', function(path, val, oldVal) {
                if (val === 'presentation') {
                    dizmo.setAttribute('state/framehidden', true);
                } else {
                    dizmo.setAttribute('state/framehidden', false);
                }

                jQuery(events).trigger('dizmo.onmodechanged', [val]);
            });

            //Tell the dizmo space that this dizmo can be docked to other dizmos. You can also supply a function
            //which gets the to be docked dizmo and has to return false or true if the dizmo can dock.
            dizmo.canDock(false);

            //If a dizmo is docked to this dizmo, the function provided to the onDock function is being called and receives
            //the instance of the docked dizmo as a parameter.
            dizmo.onDock(function(dockedDizmo) {
                // Write code here that should happen when a dizmo has been docked.
                // The line below is a small example on how to relay the event to other
                // classes.
                jQuery(events).trigger('dizmo.docked');
            });

            // onUndock is called when a dizmo has been undocked from this dizmo. The provided function receives the undocked
            // dizmo as a parameter.
            dizmo.onUndock(function(undockedDizmo) {
                // Write code here that should happen when a dizmo has been un-docked.
                // The line below is a small example on how to relay the event to other
                // classes.
                jQuery(events).trigger('dizmo.undocked');
            });
        },

        /**
         * Set the dizmo default attributes like resize and docking
         * @private
         */
        setAttributes: function() {
            var self = this;

            // Allow the resizing of the dizmo
            dizmo.setAttribute('settings/usercontrols/allowresize', true);
        }
    }
});
