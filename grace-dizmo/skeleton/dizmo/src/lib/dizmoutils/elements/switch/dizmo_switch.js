jQuery(document).ready(function() {
    var elements = jQuery('button[data-type="dizmo-switch"]');
    elements.dswitch();
});

jQuery.widget('dizmo.dswitch', {
    _create: function() {
        if (!this.element.is('button')) {
            console.log('Can only use dswitch on buttons!');
            return null;
        }

        this.element.addClass('dizmo-switch');
        jQuery('<span />', {
            'class': 'dizmo-switch-image dizmo-switch-on-image'
        }).appendTo(this.element);
        jQuery('<span />', {
            'class': 'dizmo-switch-image dizmo-switch-off-image'
        }).appendTo(this.element);
        this.state = 'off';
        this._initEvents();
    },

    _initEvents: function() {
        var self = this;

        self.element.on('click', function() {
            if (self.state === 'on') {
                self._switchOff();
            } else {
                self._switchOn();
            }
        });
    },

    _switchOn: function() {
        this.state = 'on';
        this.element.addClass('dizmo-switch-on');
        this.element.removeClass('dizmo-switch-off');
    },

    _switchOff: function() {
        this.state = 'off';
        this.element.addClass('dizmo-switch-off');
        this.element.removeClass('dizmo-switch-on');
    }
})
