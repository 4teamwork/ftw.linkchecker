$(function() {
    $('.linkchecker-toggle').click(function() {
        $(this).next('.hide-show').toggle();
        $('.hide-show').not($(this).next('.hide-show')).hide();
    });
});
