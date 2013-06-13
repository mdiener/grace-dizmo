Class("#PROJECTNAME.Dizmo", {
    after: {
        /**
         * Called after the internal initialize method
         * @private
         */
        initialize: function() {
            var self = this;

            // Show front and hide back on first load
            jQuery("#back").hide();
            jQuery("#front").show();

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
                if (val < 200) {
                    dizmo.setAttribute('geometry/height', 200);
                }

                self.save('height', val);
                jQuery(events).trigger('dizmo.resized', [dizmo.getWidth(), dizmo.getHeight()]);
            });

            // Subscribe to width changes of the dizmo
            dizmo.subscribeToAttribute('geometry/width', function(path, val, oldVal) {
                if (val < 200) {
                    dizmo.setAttribute('geometry/width', 200);
                }

                self.save('width', val);
                jQuery(events).trigger('dizmo.resized', [dizmo.getWidth(), dizmo.getHeight()]);
            });

            // Subscribe to displayMode changes
            viewer.subscribeToAttribute('displayMode', function(path, val, oldVal) {
                if (val === 'presentation') {
                    dizmo.setAttribute('hideframe', true);
                } else {
                    dizmo.setAttribute('hideframe', false);
                }

                jQuery(events).trigger('dizmo.onmodechanged', [val]);
            });

            // Register on the canDock event and return a default of false.
            // False => No docking will occur
            // True => Docking might occur (if the other dizmo allows it)
            dizmo.canDock(function(dockingDizmo) {
                return false;
            });

            // onDock and onUndock will not do anything as of now, since the canDock returns false,
            // meaning the dizmo can never be docked.
            dizmo.onDock(function(dockedDizmo) {
                // Write code here that should happen when a dizmo has been docked.
                // The line below is a small example on how to relay the event to other
                // classes.
                jQuery(events).trigger('dizmo.docked');
            });
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
            dizmo.setAttribute('allowResize', true);

            // Set the size and width of the dizmo to the values it had before reloading (or closing
            // of dizmos)
            var width = self.load('width');
            var height = self.load('height');
            if (jQuery.type(width) === 'number') {
                dizmo.setAttribute('geometry/width', width);
            }
            if (jQuery.type(height) === 'number') {
                dizmo.setAttribute('geometry/height', height);
            }
        },

        /**
         * Shows the back of the dizmo
         * @public
         */
        showBack: function() {
            dizmo.showBack();
        },

        /**
         * Shows the front of the dizmo
         * @public
         */
        showFront: function() {
            dizmo.showFront();
        },

        /**
         * Load the value saved at the given path. If no value is saved
         * in this path, return null. The value will be parsed through JSON as
         * this functions assumes it's saved in JSON format (see load)
         * @param  {String} path The path to look for a value
         * @return {mixed}       Either the value as a JavaScript type or null
         * @public
         */
        load: function(path) {
            var val = dizmo.privateStorage().getProperty(path);
            var json;

            if (jQuery.type(val) === 'string') {
                try {
                    json = jQuery.parseJSON(val);
                } catch(e) {
                    json = null;
                }
            } else {
                json = null;
            }

            return json;
        },

        /**
         * Saves a value in the given path. The value is, regardless of its type,
         * first converted into a JSON string and then saved at the given
         * path.
         * @param {String} path  The path to save the value to
         * @param {Mixed}  value The value to save (can be any JavaScript type)
         * @public
         */
        save: function(path, value) {
            var jsonString = JSON.stringify(value);

            dizmo.privateStorage().setProperty(path, jsonString);
        },

        /**
         * Publish the path with the chosen value. If no path is specified, meaning if
         * the function is called with only val, it will use the standard publish path
         * 'stdout'.
         * @param  {String} path The path to publish to
         * @param  {Mixed}  val  The value to set the publish path to
         * @public
         */
        publish: function(path, val) {
            if (jQuery.type(path) === 'undefined') {
                return;
            }

            if (jQuery.type(val) === 'undefined') {
                val = path;
                path = 'stdout';
            }

            var jsonString = JSON.stringify(val);
            dizmo.publicStorage().setProperty(path, jsonString);
        },

        /**
         * Delete the published path. If no path is specified, it will delete the standard
         * path 'stdout'.
         * @param  {String} path Path to remove from publishing
         * @public
         */
        unpublish: function(path) {
            if (jQuery.type(path) === 'undefined') {
                path = 'stdout';
            }

            dizmo.publicStorage().deleteProperty(path);
        }
    }
});
