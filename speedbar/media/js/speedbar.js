/*global _speedbar_panel_url:false */
$(function() {
    var expanded = false;
    var have_contents = false;
    var $staff_diagnostics_panel = $('#staff-diagnostics-panel');
    var $body = $('.body', $staff_diagnostics_panel);
    var $tab = $('.tab', $staff_diagnostics_panel);
    $tab.click(function() {
        if(!have_contents) {
            $.get(_speedbar_panel_url, function(data) {
                $body.text(data);
                have_contents = true;
            });
        }

        $body.css('height', ($(window).height() * 0.9) + 'px');
        if(expanded) {
            $body.slideUp();
        } else {
            $body.slideDown();
        }
        expanded = ! expanded;
    });
    };
});
