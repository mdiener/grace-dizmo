jQuery(document).ready(function() {
    var replaceElemenets = function() {
        var elements = jQuery('div[data-type="dizmo-slider"]');

        elements.each(function(index, el) {
            var or = jQuery(el).attr('data-orientation');
            jQuery(el).slider({
                orientation: or
            });

            jQuery(el).wrap('<div class="dizmo-slider-parent orientation-' + or + '"></div>');
        });

        elements.removeAttr('data-type');
        elements.addClass('dizmo-slider');
    }

    if (jQuery.type(jQuery.ui) === 'object') {
        if (jQuery.type(jQuery.ui.version) === 'string') {
            replaceElemenets();
            return;
        }
    }

    console.log('JQuery.UI needs to be loaded!');
})
