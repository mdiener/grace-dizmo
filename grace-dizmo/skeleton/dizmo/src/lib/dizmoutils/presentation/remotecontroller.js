/**
 * @class Controller class for remote dizmos
 *
 * @description
 * Every dizmo that wants to control another dizmo through the presentation properties can use this class. It is designed to allow easy access to stepping through scenes of another dizmo and provide a common interface for things like animation running flags and total steps inside another dizmo. The Navigator for example makes heavy use of this class. It needs to be instantiated with the dizmo that should be controlled and a global event object, where events are going to be attached to.
 *
 * <h3>Events</h3>
 *
 * "presentation.animationfinished" Called when an animation has finished
 * "presentation.animationstarted"  Called when an animation has started
 */
Class("Dizmo.Presentation.RemoteController", {
    has: {
        dizmo: {
            is: 'rw',
            init: null
        },

        totalSteps: {
            is: 'rw',
            init: 0
        },

        step: {
            is: 'rw',
            init: 0,

            getterName: 'getStep',
            setterName: 'setStep'
        },

        events: {
            is: 'rw',
            init: null
        }
    },

    after: {
        /**
         * Control another dizmo with this class. The dizmo is provided through the
         * config object.
         * @param  {Object} config The configuration for the controller
         *                         {
         *                             dizmo:    {Object} The dizmo which needs to be controlled
         *                             eventObj: {Object} The event object to attache the events to
         *                         }
         * @constructs
         */
        initialize: function(config) {
            var self = this;

            if (jQuery.type(config.dizmo) !== 'object') {
                throw {
                    name: 'NotAnObjectError',
                    message: 'Please provide a valid dizmo object.'
                };
            }

            if (jQuery.type(config.eventObj) !== 'object') {
                throw {
                    name: 'NotAnObjectError',
                    message: 'Please provide a valid event object.'
                };
            }

            self.setDizmo(config.dizmo);
            self.setEvents(config.eventObj);

            totalSteps = self.getDizmo().publicStorage().getProperty('presentation/totalSteps');
            if (jQuery.type(totalSteps) !== 'undefined') {
                totalSteps = parseInt(totalSteps);
                if (!isNaN(totalSteps)) {
                    self.setTotalSteps(totalSteps);
                }
            }

            step = self.getDizmo().publicStorage().getProperty('presentation/step');
            if (jQuery.type(step) !== 'undefined') {
                step = parseInt(step);
                if (!isNaN(step)) {
                    self.setStep(step);
                }
            }

            self.initEvents();
        }
    },

    methods: {
        /**
         * Initialize all the events
         * @private
         */
        initEvents: function() {
            var self = this;

            var dizmo = self.getDizmo();
            var pubStore = dizmo.publicStorage();

            pubStore.subscribeTo('presentation/totalSteps', function(path, val, oldVal) {
                steps = parseInt(val);

                if (isNaN(steps)) {
                    self.setTotalSteps(0);
                }

                self.setTotalSteps(steps);
            });

            pubStore.subscribeTo('presentation/step', function(path, val, oldVal) {
                step = parseInt(val);

                if (isNaN(step)) {
                    self.step = 0;
                }

                self.step = step;
            });

            pubStore.subscribeTo('presentation/animationRunning', function(path, val, oldVal) {
                var oldState;
                var currentState;

                if (jQuery.type(oldVal) === 'undefined') {
                    oldVal = 'false';
                }

                try {
                    currentState = jQuery.parseJSON(val);
                } catch (err) {
                    throw new {
                        'name': 'WrongFormatError',
                        'message': 'The provided animation value has a wrong format.'
                    }
                }

                if (jQuery.type(currentState) !== 'boolean') {
                    throw new {
                        'name': 'NotABooleanError',
                        'message': 'The provided animation stop value is not a boolean.'
                    }
                }

                try {
                    oldState = jQuery.parseJSON(oldVal);
                } catch (err) {
                    throw new {
                        'name': 'WrongFormatError',
                        'message': 'The provided animation value has a wrong format.'
                    }
                }

                if (jQuery.type(oldState) !== 'boolean') {
                    throw new {
                        'name': 'NotABooleanError',
                        'message': 'The provided animation stop value is not a boolean.'
                    }
                }

                if (oldState && !currentState) {
                    jQuery(self.getEvents()).trigger('presentation.animationfinished');
                    return;
                }

                if (!oldState && currentState) {
                    jQuery(self.getEvents()).trigger('presentation.animationstarted');
                }
            });
        },

        /**
         * Set the step to this value
         * @param {Number/String} step The step to set the controlled dizmo to. Can either be
         *                             a number or a number as a string.
         * @public
         */
        setStep: function(step) {
            var self = this;

            step = parseInt(step);

            if (isNaN(step)) {
                throw 'The provided step parameter is neither a number nor a valid string.';
            }
            if (step > self.getTotalSteps()) {
                throw 'The provided step is bigger than the total steps accepter by this dizmo';
            }

            self.getDizmo().publicStorage().setProperty('presentation/step', step.toString());
            self.step = step;
        },

        /**
         * @return {Number} The current step
         * @public
         */
        getStep: function() {
            var self = this;

            return self.step;
        },

        /**
         * Go to the first step of the dizmo
         * @public
         */
        firstStep: function() {
            var self = this;

            var dizmo = self.getDizmo();
            var step = self.getStep();

            if (step === 0) {
                return;
            }

            self.setStep(1);
        },

        /**
         * Go the the previous step of the dizmo
         * @public
         */
        previousStep: function() {
            var self = this;

            var dizmo = self.getDizmo();
            var step = self.getStep();

            if (step - 1 === 0) {
                self.firstStep();
                return;
            }

            self.setStep(--step);
        },

        /**
         * Go to the next step of the dizmo
         * @public
         */
        nextStep: function() {
            var self = this;

            var dizmo = self.getDizmo();
            var step = self.getStep();
            var totalSteps = self.getTotalSteps();

            if (step + 1 === totalSteps) {
                self.lastStep();
                return;
            }

            self.setStep(++step);
        },

        /**
         * Go the the last step of the dizmo
         * @public
         */
        lastStep: function() {
            var self = this;

            var dizmo = self.getDizmo();
            var step = self.getStep();
            var totalSteps = self.getTotalSteps();

            if (step === totalSteps) {
                return;
            }

            self.setStep(totalSteps);
        }
    }
});
