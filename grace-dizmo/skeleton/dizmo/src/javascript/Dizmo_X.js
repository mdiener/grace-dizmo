Class("#PROJECTNAME.Dizmo", {
    after: {
        initialize: function() {
            var self = this;

            // Show front and hide back on first load
            jQuery("#back").hide();
            jQuery("#front").show();

            self.setAttributes();
            self.initEvents();

            self.restore();
        }
    },

    methods: {
        /**
         * Initiate all the events for dizmo related stuff
         */
        initEvents: function() {
            // Show back and front listeners
            dizmo.onShowBack(function() {
                jQuery("#front").hide();
                jQuery("#back").show();
            });

            dizmo.onShowFront(function() {
                jQuery("#back").hide();
                jQuery("#front").show();
            });

            // Subscribe to height changes of the dizmo
            dizmo.subscribeToAttribute('geometry/height', function(path, val, oldVal) {
                if (val < 200) {
                    dizmo.setAttribute('geometry/height', 200);
                }

                dizmo.privateStorage().setProperty('height', val);
                jQuery(events).trigger('dizmo.resize', [dizmo.getWidth(), dizmo.getHeight()]);
            });

            // Subscribe to width changes of the dizmo
            dizmo.subscribeToAttribute('geometry/width', function(path, val, oldVal) {
                if (val < 200) {
                    dizmo.setAttribute('geometry/width', 200);
                }

                dizmo.privateStorage().setProperty('width', val);
                jQuery(events).trigger('dizmo.resize', [dizmo.getHeigh(), dizmo.getWidth()]);
            });

            // Subscribe to displayMode changes
            viewer.subscribeToAttribute('displayMode', function(path, val, oldVal) {
                if (val === 'presentation') {
                    dizmo.setAttribute('hideframe', true);
                    jQuery(events).trigger('dizmo.displaymode', [true]);
                } else {
                    dizmo.setAttribute('hideframe', false);
                    jQuery(events).trigger('dizmo.displaymode', [false]);
                }
            });
        },

        /**
         * Restore the saved dizmo state (width, height)
         * @private
         */
        restore: function() {
            if (dizmo.privateStorage().getProperty('width')) {
                dizmo.setAttribute('geometry/width', parseInt(dizmo.privateStorage().getProperty('width')));
            }

            if (dizmo.privateStorage().getProperty('height')) {
                dizmo.setAttribute('geometry/height', parseInt(dizmo.privateStorage().getProperty('height')));
            }
        },

        /**
         * Set the dizmo default attributes like resize and docking
         * @private
         */
        setAttributes: function() {
            dizmo.setAttribute('allowResize', true);
            dizmo.canDock(function() {
                return false;
            });
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

        save: function(path, val) {
            var json = JSON.stringify(val);

            dizmo.privateStorage().setProperty(path, val);
        }
    }
});
