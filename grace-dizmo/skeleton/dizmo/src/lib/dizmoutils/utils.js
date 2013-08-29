/**
 * @class Utils class for some simple tasks
 *
 * @description
 * This class is already instantiated and can be access through the global object "utils". It offer a few simple functions like randomized strings and the position of a dizmo to another dizmo. There might be more added to this class as the development continues.
 */
Class("Dizmo.Utils", {
    methods: {
        /**
         * Get the side on which the docked dizmo has docked.
         * @param  {Object} otherDizmo A complete dizmo object (as provided by onDock, onUndock, canDock)
         * @return {String}            A string with either 'left', 'right', 'top', 'bottom'
         */
        getDizmoPosition: function(mydizmo, otherDizmo) {
            if (typeof otherDizmo !== 'object') {
                throw {
                    name: 'mustBeADizmoObject',
                    message: 'You need to provide a dizmo object, as provided by onDock, onUndock or canDock.'
                };
            }

            try {
                var myRight = mydizmo.getAttribute('geometry/x');
                var myLeft = myRight - mydizmo.getAttribute('geometry/width');
                var myTop = mydizmo.getAttribute('geometry/y');
                var myBottom = myTop + mydizmo.getAttribute('geometry/height') + 40;
            } catch (e) {
                throw {
                    name: 'mustBeADizmoObject',
                    message: 'You need to provide a dizmo object, as provided by onDock, onUndock or canDock.'
                };
            }

            try {
                var otherRight = otherDizmo.getAttribute('geometry/x');
                var otherLeft = otherRight - otherDizmo.getAttribute('geometry/width');
                var otherTop = otherDizmo.getAttribute('geometry/y');
                var otherBottom = otherTop + otherDizmo.getAttribute('geometry/height') + 40;
            } catch (e) {
                throw {
                    name: 'mustBeADizmoObject',
                    message: 'You need to provide a dizmo object, as provided by onDock, onUndock or canDock.'
                };
            }

            if (otherRight <= myLeft) {
                return 'left';
            }

            if (otherLeft >= myRight) {
                return 'right';
            }

            if (otherBottom <= myTop) {
                return 'top';
            }

            if (otherTop >= myBottom) {
                return 'bottom';
            }
        },

        /**
         * Returns a random alphanumeric string with the requested length. Contains dupes unless
         * the nodupes flag is set to false.
         * @param  {Number}  length  The length of the random string
         * @param  {Boolean} nodupes True if no dupes should be produced
         * @return {String}          A random alphanumeric string
         */
        randomString: function(length, nodupes) {
            if (jQuery.type(length) !== 'number') {
                throw 'Length is not a number';
            }
            if (length < 1) {
                throw 'Length must be greater or equal to 1';
            }
            if (jQuery.type(nodupes) !== 'boolean') {
                if (jQuery.type(nodupes) === 'undefined') {
                    nodupes = false;
                } else {
                    throw 'Nodupes must be either a boolean or undefined';
                }
            }

            var chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            var output = '';
            var used = '';

            if (nodupes && length > chars.length) {
                throw 'Length must be smaller than ' + chars.length + ' if used with nodupes.'
            }

            do {
                var randnum = Math.floor(Math.random() * chars.length);
                var chr = chars.charAt(randnum);

                if (nodupes === true) {
                    var added = (used.indexOf(chr) !== -1);

                    if (added === true) {
                        continue;
                    }

                    used += chr;
                }

                output += chr;
            } while (output.length < length);

            return output;
        }
    }
});

utils = new Dizmo.Utils();
