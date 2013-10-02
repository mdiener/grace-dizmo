/**
 * Button widget
 *
 * Dizmo button styling. Uses theme light and dark.
 */
jQuery.widget('dizmo.dbutton', {
    options: {
        'theme': 'light'
    },

    _create: function() {
        if (!this.element.is('button')) {
            console.log('Only works on button elements!');
            return null;
        }

        if (this.options.theme === 'light') {
            this.element.addClass('dizmo-button-' + this.options.theme);
        } else if (this.options.theme === 'dark') {
            this.element.addClass('dizmo-button-' + this.options.theme);
        }

        this.element.addClass('dizmo-button');
        this._changeTheme(this.options.theme);
    },

    theme: function(theme) {
        if (jQuery.type(theme) === 'undefined') {
            return this.options.theme;
        }

        if (jQuery.type(theme) !== 'string') {
            return;
        }

        this._changeTheme(theme);
    },

    _changeTheme: function(theme) {
        this.element.removeClass('dizmo-button-' + theme);
        this.options.theme = theme;
        this.element.addClass('dizmo-button-' + theme);
    },
});

/**
 * Checkbox plugin.
 *
 * Can be used to create checkboxes styled to match other dizmos.
 *
 * Usage:
 * jQuery('#myInputElement').dcheckbox();
 */
jQuery.widget('dizmo.dcheckbox', {
    options: {
        theme: 'light'
    },

    _create: function() {
        if (this.element.attr('type') !== 'checkbox') {
            console.log('Only works on checkbox elements!');
            return null;
        }

        if (jQuery.type(Dizmo.Utils.randomString) !== 'function') {
            console.log('utils.js needs to be included before dizmo_checkbox.js!');
            return null;
        }

        if (jQuery.type(this.element.attr('id')) !== 'string') {
            this.attr('id', Dizmo.Utils.randomString(8));
        }

        this.element.addClass('dizmo-checkbox-input');
        this._wrapper = jQuery('<div />', {
            'class': 'dizmo-checkbox'
        }).insertBefore(this.element);
        this.element.appendTo(this._wrapper);

        var label = jQuery('label[for="' + this.element.attr('id') + '"]');
        if (label.length > 0) {
            label.insertAfter(this.element);
            label.addClass('dizmo-checkbox-label');
            var text = label.text();
            label.text('');
            jQuery('<span />', {
                'text': text,
                'class': 'dizmo-checkbox-label-text'
            }).appendTo(label);
        } else {
            label = jQuery('<label />', {
                'class': 'dizmo-checkbox-label',
                'for': this.element.attr('id')
            }).insertAfter(this.element);
        }

        jQuery('<span />', {
            'class': 'dizmo-checkbox-label-image'
        }).prependTo(label);

        this._changeTheme(this.options.theme);
    },

    theme: function(theme) {
        if (jQuery.type(theme) === 'undefined') {
            return this.options.theme;
        }

        if (jQuery.type(theme) !== 'string') {
            return;
        }

        this._changeTheme(theme);
    },

    _changeTheme: function(theme) {
        this._wrapper.removeClass('dizmo-checkbox-' + theme);
        this.options.theme = theme;
        this._wrapper.addClass('dizmo-checkbox-' + theme);
    },
});

/**
 * Dizmo selectbox plugin. Creates a dizmo-themed selectbox. The change event
 * is being propagated to the underlying select element, so there is no need
 * to attach another event handle to communicate with the widget.
 *
 * Usage:
 * jQuery('.my-select-element').dselectbox();
 *
 * If the underlying selectbox changes, a call to the update function of the
 * widget is required.
 * jQuery('.my-select-element').dselectbox('update');
 */
jQuery.widget('dizmo.dselectbox', {
    options: {
        theme: 'light'
    },

    _create: function() {
        var self = this;

        self.element.hide();
        self._value = this.element.children(':selected').val();
        self._open = false;

        self._buildElement();
        self._initEvents();

        self._changeTheme(this.options.theme);
    },

    _buildElement: function() {
        var self = this;

        var wrapper = jQuery('<div />', {
            'class': 'dizmo-selectbox'
        }).insertAfter(this.element);
        self._wrapper = wrapper;

        jQuery('<span />', {
            'class': 'dizmo-selectbox-image'
        }).appendTo(self._wrapper);
        jQuery('<span />', {
            'class': 'dizmo-selectbox-text',
            'text': self.element.children('option[value="' + self._value + '"]').text()
        }).appendTo(self._wrapper);

        var entries = self.element.children();
        var list = jQuery('<ul />', {
            'class': 'dizmo-selectbox-list'
        }).appendTo(self._wrapper);

        entries.each(function(index, el) {
            var el = jQuery(el);
            var li = jQuery('<li />', {
                'class': 'dizmo-selectbox-list-entry',
                'data-value': el.attr('value')
            }).appendTo(list);
            jQuery('<span />', {
                'text': el.text()
            }).appendTo(li);

            li.on('click', function(e) {
                var val = jQuery(this).attr('data-value');
                self._selectValue(val);
            });
        });
        list.hide();

        self._attachWrapperEvents();
    },

    _attachWrapperEvents: function() {
        var self = this;

        self._wrapper.on('click', function() {
            if (self._open) {
                self._closeSelectbox();
            } else {
                self._openSelectbox();
            }
        });
    },

    _initEvents: function() {
        var self = this;

        self.element.on('change', function() {
            var val = jQuery(this).val();
            self._setValue(val);
        });
    },

    _closeSelectbox: function() {
        var self = this;

        self._open = false;
        self._wrapper.children('.dizmo-selectbox-list').hide('slide', {
            direction: 'up',
            duration: 200,
            complete: function() {
                self._wrapper.removeClass('dizmo-selectbox-open');
            }
        });
    },

    _openSelectbox: function() {
        var self = this;

        var width = self._wrapper.width();

        self._open = true;
        var list = self._wrapper.children('.dizmo-selectbox-list');
        list.width(width);
        list.show('slide', {
            direction: 'up',
            duration: 200
        });
        self._wrapper.addClass('dizmo-selectbox-open');
    },

    _selectValue: function(val) {
        var self = this;

        self.element.val(val);

        var options = self.element.children('option');
        var noVal = true;
        options.each(function(i, el) {
            if (val === jQuery(el).attr('value')) {
                noVal = false;
            }
        });

        if (!noVal) {
            self.element.trigger('change');
        }
    },

    _setValue: function(val) {
        var self = this;

        var text = self.element.children('option[value="' + val + '"]').text();
        self._wrapper.children('.dizmo-selectbox-text').text(text);
    },

    value: function(val) {
        var self = this;

        if (jQuery.type(val) === 'undefined') {
            return self.element.val();
        }

        self._selectValue(val);
    },

    /**
     * Update the selectbox
     * @public
     */
    update: function() {
        var self = this;

        self._wrapper().remove();
        self._buildElement();
    },

    theme: function(theme) {
        if (jQuery.type(theme) === 'undefined') {
            return this.options.theme;
        }

        if (jQuery.type(theme) !== 'string') {
            return;
        }

        this._changeTheme(theme);
    },

    _changeTheme: function(theme) {
        this._wrapper.removeClass('dizmo-selectbox-' + theme);
        this.options.theme = theme;
        this._wrapper.addClass('dizmo-selectbox-' + theme);
    }
});

/**
 * Extending the current slider from jQuery UI and adding a wrapper around.
 *
 * Usage:
 * jQuery('.my-dizmo-slider').dslider();
 *
 * Use this slider only as a normal slider. To get a scrollbar, use the
 * dizmoscroll library.
 */
jQuery.widget('dizmo.dslider', jQuery.ui.slider, {
    options: {
        theme: 'light'
    },

    _create: function() {
        jQuery.ui.slider.prototype._create.call(this);

        this._wrapper = jQuery('<div />', {
            'class': 'dizmo-slider orientation-' + this.options.orientation
        }).insertBefore(this.element);
        this.element.appendTo(this._wrapper);
        this.element.addClass('dizmo-slider-inner');

        this._changeTheme(this.options.theme);
    },

    theme: function(theme) {
        if (jQuery.type(theme) === 'undefined') {
            return this.options.theme;
        }

        if (jQuery.type(theme) !== 'string') {
            return;
        }

        this._changeTheme(theme);
    },

    _changeTheme: function(theme) {
        this._wrapper.removeClass('dizmo-slider-' + theme);
        this.options.theme = theme;
        this._wrapper.addClass('dizmo-slider-' + theme);
    },
});

/**
 * Create a new switch element from a button.
 *
 * Usage:
 * jQuery('.my-button-element').dswitch();
 *
 * You can supply height, width and theme to the creation function of the button:
 * jQuery('.my-button-element').dswitch({
 *     width: 100,
 *     height: 50,
 *     theme: 'light'
 * });
 *
 * Themes available by default: "dark" and "light".
 *
 * To change the height and/or width of the element at a later time, use the provided
 * height and width functions.
 * jQuery('.my-button-element').dswitch('height', 100);
 * jQuery('.my-button-element').dswitch('width', 200);
 *
 * To get the height or width of the button, call these functions without any parameter.
 * var height = jQuery('.my-button-element').dswitch('height');
 * var width = jQuery('.my-button-element').dswitch('width');
 *
 * To get or set the state of the switch, call the state function.
 * var state = jQuery('.my-button-element').dswitch('state');
 *
 * jQuery('.my-button-element').dswitch('state', 'on');
 * jQuery('.my-button-element').dswitch('state', 'off');
 *
 * The only two states recognized are "on" and "off". Everything else will be ignored.
 */
jQuery.widget('dizmo.dswitch', {
    options: {
        theme: 'light',
        width: 100,
        height: 50
    },

    _create: function() {
        if (!this.element.is('button')) {
            console.log('Can only use dswitch on buttons!');
            return null;
        }

        this.element.text('');
        this.element.addClass('dizmo-switch');
        this._changeTheme(this.options.theme);

        jQuery('<span />', {
            'class': 'dizmo-switch-box dizmo-switch-on-box',
            'text': 'ON'
        }).appendTo(this.element);
        jQuery('<span />', {
            'class': 'dizmo-switch-box dizmo-switch-off-box',
            'text': 'OFF'
        }).appendTo(this.element);

        this._setWidgetSize(this.options.width, this.options.height);

        this._currentState = 'off';
        this._initEvents();
    },

    _initEvents: function() {
        var self = this;

        self.element.on('click', function() {
            if (self._currentState === 'on') {
                self._switchOff();
            } else {
                self._switchOn();
            }
        });
    },

    height: function(height) {
        if (jQuery.type(height) === 'undefined') {
            return this.options.height;
        }

        var h = parseInt(height);
        if (isNaN(h)) {
            return;
        }

        w = this.element.width();
        this._setWidgetSize(w, h);
    },

    width: function(width) {
        if (jQuery.type(width) === 'undefined') {
            return this.options.width;
        }

        var w = parseInt(width);
        if (isNaN(w)) {
            return;
        }

        h = this.element.height();
        this._setWidgetSize(w, h);
    },

    _setWidgetSize: function(width, height) {
        this.options.width = width;
        this.options.height = height;
        this.element.height(height);
        this.element.width(width);
        this._setSpanLineHeight();
    },

    _setSpanLineHeight: function() {
        var height = this.element.children('span').height();
        this.element.children('span').css('line-height', height + 'px');
    },

    theme: function(theme) {
        if (jQuery.type(theme) === 'undefined') {
            return this.options.theme;
        }

        if (jQuery.type(theme) !== 'string') {
            return;
        }

        this._changeTheme(theme);
    },

    _changeTheme: function(theme) {
        this.element.removeClass('dizmo-switch-' + theme);
        this.options.theme = theme;
        this.element.addClass('dizmo-switch-' + theme);
    },

    _switchOn: function() {
        this._currentState = 'on';
        this.element.addClass('dizmo-switch-on');
        this.element.removeClass('dizmo-switch-off');
    },

    _switchOff: function() {
        this._currentState = 'off';
        this.element.addClass('dizmo-switch-off');
        this.element.removeClass('dizmo-switch-on');
    },

    state: function(state) {
        if (jQuery.type(state) !== 'string') {
            return this._currentState;
        }

        if (state === 'off') {
            if (this._currentState === 'on') {
                this._switchOff();
            }
            return;
        }

        if (state === 'on') {
            if (this._currentState === 'off') {
                this._switchOn();
            }
            return;
        }
    }
});

jQuery(document).ready(function() {
    var getTheme = function(el) {
        var theme = el.attr('data-theme');

        if (jQuery.type(theme) === 'undefined') {
            return null;
        } else {
            return theme;
        }
    }

    var elements = jQuery('input[data-type="dizmo-checkbox"]');
    elements.each(function(index, el) {
        var el = jQuery(el);
        var theme = getTheme(el);

        if (theme === 'dark' || theme === 'light') {
            el.dcheckbox({
                theme: theme
            });
        } else {
            el.dcheckbox();
        }

        el.removeAttr('data-type');
        el.removeAttr('data-theme');
    });

    elements = jQuery('select[data-type="dizmo-selectbox"]');
    elements.each(function(index, el) {
        var el = jQuery(el);
        var theme = getTheme(el);

        if (theme === 'dark' || theme === 'light') {
            el.dselectbox({
                theme: theme
            });
        } else {
            el.dselectbox();
        }

        el.removeAttr('data-type');
        el.removeAttr('data-theme');
    });

    elements = jQuery('div[data-type="dizmo-slider"]');
    elements.each(function(index, el) {
        var el = jQuery(el);
        var theme = getTheme(el);
        var or = el.attr('data-orientation');
        if (jQuery.type(or) === 'undefined') {
            or = 'horizontal';
        }

        if (theme === 'dark' || theme === 'light') {
            el.dslider({
                theme: theme,
                orientation: or
            });
        } else {
            el.dslider({
                orientation: or
            });
        }

        el.removeAttr('data-type');
        el.removeAttr('data-theme');
    });

    var elements = jQuery('button[data-type="dizmo-switch"]');
    elements.each(function(index, el) {
        var el = jQuery(el);
        var theme = getTheme(el);

        if (theme === 'dark' || theme === 'light') {
            el.dswitch({
                theme: theme
            });
        } else {
            el.dswitch();
        }

        el.removeAttr('data-type');
        el.removeAttr('data-theme');
    });

    var elements = jQuery('button[data-type="dizmo-button"]');
    elements.each(function(index, el) {
        var el = jQuery(el);
        var theme = getTheme(el);

        if (theme === 'dark' || theme === 'light') {
            el.dbutton({
                theme: theme
            });
        } else {
            el.dbutton();
        }

        el.removeAttr('data-type');
        el.removeAttr('data-theme');
    });
});
