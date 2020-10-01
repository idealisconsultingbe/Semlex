odoo.define('web_chatter_position', function (require) {
    "use strict";

    var config = require('web.config');
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');

    FormController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_chatter_position', this._onChatterPosition.bind(this));
            }
        },
        _onChatterPosition: function () {
            if (this.renderer.chatterPosition == 'bottom') {
                this.renderer.chatterPosition = 'right';
            }
            else {
                this.renderer.chatterPosition = 'bottom';
            }
            this.renderer.applyChatterPosition();
        },
        // update: function () {
        //     var def = this._super.apply(this, arguments);
        //     var self = this;
        //     return this.dp.add(def).then(function () {
        //         self.renderer.applyChatterPosition();
        //     });
        // }
    });

    FormRenderer.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.chatterPosition = 'bottom';
        },
        applyChatterPosition: function () {
            var $form = $('.o_form_view');
            if (config.device.isMobile) {
                return;
            }
            if ($form.length == 1) {
                var $sheet = $form.find('div.o_form_sheet_bg');
                var $chatter = $form.find('aside.o_chatter');
                if ($sheet.length == 1 && $chatter.length == 1) {
                    if (this.chatterPosition == 'right') {
                        $form.css('display', 'flex');
                        $sheet.css('width', '');
                        $sheet.find('.o_form_sheet').css('max-width', '');
                        $chatter.css('width', '');
                    }
                    else {
                        $form.css('display', 'block');
                        $sheet.css('width', '100%');
                        $sheet.find('.o_form_sheet').css('max-width', '100%');
                        $chatter.css('width', '100%');
                    }
                }
            }
        },
        // _renderView: function () {
        //     console.log('_renderView', this.chatterPosition);
        //     var self = this;
        //     var def = this._super.apply(this, arguments);
        //     def.then(function() {
        //         self.applyChatterPosition();
        //     });
        //     return def;
        // },
        _updateView: function ($newContent) {
            this._super.apply(this, arguments);
            this.applyChatterPosition();
            var self = this;
            setTimeout(function () {
                self.applyChatterPosition();
            }, 200);
            setTimeout(function () {
                self.applyChatterPosition();
            }, 600);
            setTimeout(function () {
                self.applyChatterPosition();
            }, 2000);
        },
    });
});
