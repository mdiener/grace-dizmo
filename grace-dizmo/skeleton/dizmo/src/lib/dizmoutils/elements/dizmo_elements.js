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
        if (this.element.attr('type') !== 'button') {
            console.log('Only works on button elements!');
            return null;
        }

        if (this.options.theme === 'light') {
            this.element.addClass('dizmo-button-' + this.options.theme);
        } else if (this.options.theme === 'dark') {
            this.element.addClass('dizmo-button-' + this.options.theme);
        }

        this.element.addClass('dizmo-button');
    }
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

        this.element.removeAttr('data-type');
    }
});

jQuery.widget('dizmo.dselectbox', {
    _create: function() {
        var self = this;

        self.element.hide();
        self._value = this.element.children(':selected').val();
        self._open = false;

        self._buildElement();
        self._initEvents();
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
        self.element.trigger('change');
    },

    _setValue: function(val) {
        var self = this;

        var text = self.element.children('option[value="' + val + '"]').text();
        self._wrapper.children('.dizmo-selectbox-text').text(text);
    },

    update: function() {
        var self = this;

        self._wrapper().remove();
        self._buildElement();
    }
});

/**
 * Extending the current slider from jQuery UI and adding a wrapper around.
 */
jQuery.widget('dizmo.dslider', jQuery.ui.slider, {
    _create: function() {
        jQuery.ui.slider.prototype._create.call(this);

        this.element.wrap('<div class="dizmo-slider-parent orientation-' + this.options.orientation + '"></div>');
        this.element.addClass('dizmo-slider');
    }
});

/**
 * Create a new switch element from a button.
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
        if (theme === 'light') {
            this.options.theme = 'light'
            this.element.addClass('dizmo-switch-light');
            this.element.removeClass('dizmo-switch-dark');
            return;
        }

        if (theme === 'dark') {
            this.options.theme = 'dark'
            this.element.addClass('dizmo-switch-dark');
            this.element.removeClass('dizmo-switch-light');
            return;
        }
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
    var elements = jQuery('input[data-type="dizmo-checkbox"]');
    elements.dcheckbox();

    elements = jQuery('select[data-type="dizmo-selectbox"]');
    elements.dselectbox();

    elements = jQuery('div[data-type="dizmo-slider"]');
    elements.each(function(index, el) {
        var or = jQuery(el).attr('data-orientation');
        jQuery(el).dslider({
            orientation: or
        });
    });

    var elements = jQuery('button[data-type="dizmo-switch"]');
    elements.dswitch();

    var elements = jQuery('button[data-type="dizmo-button"]');
    elements.dbutton();
});
