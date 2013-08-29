/**
 * @class Controller used by dizmos that want to be controlled
 *
 * @description
 * This class provides a simple interface for any dizmo that has scenes and thus can be controlled by another dizmo, like the Navigator. It does not need to be instantiated and provides, through static functions and events, a common interface that can be used to listen to changes from the outside to step through scenes.
 * Although it does not need to be instantiated, it needs to be initialized (only once). By calling Dizmo.Presentation.Listener.initialize(eventObj), you will pass the event object you want all the events being attached to, to the class. Further usage does not need any other initialization and the class can be used by calling the functions in the same way as the initialize function has been called.
 *
 * <h3Events</h3>
 *
 * All the step events receive the current step and the step before as arguments
 * "presentation.step.first"    Called when the first step is set
 * "presentation.step.previous" Called when the previous step is set
 * "presentation.step.next"     Called when the next step is set
 * "presentation.step.last"     Called when the last step is set
 *
 * "presentation.animationfinished" Called when an animation has finished
 * "presentation.animationstarted"  Called when an animation has started
 */
Class("Dizmo.Presentation.Controller", {
    my: {
        has: {
            events: {
                is: 'rw',
                init: null
            }
        },

        methods: {
            /**
             * Initialize the class and pass the event object to it
             * @param  {Object} eventObj The object to attach all the events to
             * @public
             */
            init: function(eventObj) {
                var self = this;

                if (jQuery.type(eventObj) !== 'object') {
                    throw new {
                        name: 'NotAnObjectError',
                        message: 'Please provide a valid event object.'
                    };
                }

                dizmo.publicStorage().setProperty('presentation/totalSteps', '0');
                dizmo.publicStorage().setProperty('presentation/step', '0');
                dizmo.publicStorage().setProperty('presentation/animationRunning', 'false');

                self.setEvents(eventObj);
                self.initEvents();
            },

            /**
             * Initialize the events
             * @private
             */
            initEvents: function() {
                var self = this;

                var pubStore = dizmo.publicStorage();

                pubStore.subscribeTo('presentation/step', function(path, val, oldVal) {
                    step = parseInt(val);
                    oldStep = parseInt(oldVal);
                    var maxSteps = dizmo.publicStorage().getProperty('presentation/totalSteps');
                    maxSteps = parseInt(maxSteps);

                    if (isNaN(step) || isNaN(maxSteps)) {
                        return;
                    }
                    if (step > maxSteps || step < 1) {
                        return;
                    }

                    if (isNaN(oldStep)) {
                        oldStep = 1;
                    }

                    if (step === 1) {
                        jQuery(self.getEvents()).trigger('presentation.step.first', [step, oldStep]);
                        return;
                    }
                    if (step >= maxSteps) {
                        jQuery(self.getEvents()).trigger('presentation.step.last', [step, oldStep]);
                        return;
                    }
                    if (step < oldStep) {
                        jQuery(self.getEvents()).trigger('presentation.step.previous', [step, oldStep]);
                        return;
                    }
                    if (step > oldStep) {
                        jQuery(self.getEvents()).trigger('presentation.step.next', [step, oldStep]);
                        return;
                    }
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
                        return;
                    }
                });
            },

            /**
             * Set the total steps available for this dizmo
             * @param {Number} steps The total number of steps available
             * @public
             */
            setTotalSteps: function(steps) {
                steps = parseInt(steps);

                if (isNaN(steps)) {
                    throw new {
                        'name': 'NotANumberError',
                        'message': 'Please provide a number as the total steps!'
                    }
                }

                dizmo.publicStorage().setProperty('presentation/totalSteps', steps.toString());
            },

            /**
             * @return {Number} The total number of steps available to this dizmo
             * @public
             */
            getTotalSteps: function() {
                var totalSteps = dizmo.publicStorage().getProperty('presentation/totalSteps');
                totalSteps = parseInt(totalSteps);

                if (isNaN(totalSteps)) {
                    return 0;
                }

                return totalSteps;
            },

            /**
             * Set the current step of the dizmo
             * @param {Number} step The current step
             * @public
             */
            setStep: function(step) {
                step = parseInt(step);

                if (isNaN(step)) {
                    throw new {
                        'name': 'NotANumberError',
                        'message': 'Please provide a number as a step!'
                    }
                }

                dizmo.publicStorage().setProperty('presentation/step', step.toString());
            },

            /**
             * Get the current step
             * @return {Number} The current step
             * @public
             */
            getStep: function() {
                var step = dizmo.publicStorage().getProperty('presentation/step');
                step = parseInt(step);

                if (isNaN(step)) {
                    return 0;
                }

                return step;
            },

            /**
             * Go to the first step
             * @public
             */
            firstStep: function() {
                var self = this;

                self.setStep(1);
            },

            /**
             * Go to the previous step
             * @public
             */
            previousStep: function() {
                var self = this;

                var step = dizmo.publicStorage().getProperty('presentation/step');
                step = parseInt(step);

                if (isNaN(step)) {
                    throw new {
                        'name': 'NotANumberError',
                        'message': 'The step property does not seem to be a number!'
                    }
                }

                if (step - 1 <= 1) {
                    self.firstStep();
                    return;
                }

                self.setStep(--step);
            },

            /**
             * Go to the next step
             * @public
             */
            nextStep: function() {
                var self = this;

                var step = dizmo.publicStorage().getProperty('presentation/step');
                var totalSteps = dizmo.publicStorage().getProperty('presentation/totalSteps');
                step = parseInt(step);
                totalSteps = parseInt(totalSteps);

                if (isNaN(step) || isNaN(totalSteps)) {
                    throw new {
                        'name': 'NotANumberError',
                        'message': 'The step property does not seem to be a number!'
                    }
                }

                if (step + 1 >= totalSteps) {
                    self.lastStep();
                    return;
                }

                self.setStep(++step);
            },

            /**
             * Go to the last step
             * @public
             */
            lastStep: function() {
                var self = this;

                var totalSteps = dizmo.publicStorage().getProperty('presentation/totalSteps');
                totalSteps = parseInt(totalSteps);

                if (isNaN(totalSteps)) {
                    throw new {
                        'name': 'NotANumberError',
                        'message': 'The total steps property does not seem to be a number!'
                    }
                }

                self.setStep(totalSteps);
            },

            /**
             * Start the animation
             * @public
             */
            startAnimation: function() {
                dizmo.publicStorage().setProperty('presentation/animationRunning', 'true');
            },

            /**
             * End the animation
             * @public
             */
            stopAnimation: function() {
                dizmo.publicStorage().setProperty('presentation/animationRunning', 'false');
            }
        }
    }
});
