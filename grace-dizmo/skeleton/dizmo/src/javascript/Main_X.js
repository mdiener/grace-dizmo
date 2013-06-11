//= require Dizmo

Class("#PROJECTNAME.Main", {
    has: {
        // This will be your wrapper around the dizmo API. It is instantiated
        // before the the initialize function (defined below) is called and can
        // therefor already be used there.
        dizmo: {
            is: 'ro',
            init: function() {
                return new #PROJECTNAME.Dizmo();
            }
        }
    },

    after: {
        initialize: function() {
            var self = this;

            self.initEvents();
        }
    },

    methods: {
        initEvents: function() {
            var self = this;

            jQuery('.done-btn').on('click', function() {
                self.getDizmo().showFront();
            });
        }
    }
});
