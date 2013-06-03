//= require Dizmo

Class("#PROJECTNAME.Main", {
    has: {
        dizmo: {
            is: 'r',
            init: function() {
                return new #PROJECTNAME.Dizmo();
            }
        }
    }

    after: {
        initialize: function(dizmo) {
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
