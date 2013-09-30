jQuery(document).ready(function() {
    var elements = jQuery('input[data-type="dizmo-checkbox"]');
    elements.checkbox();
});

jQuery.widget('dizmo.checkbox', {
    _create: function() {
        if (this.element.attr('type') !== 'checkbox') {
            console.log('Checkbox only works on checkbox elements!');
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
