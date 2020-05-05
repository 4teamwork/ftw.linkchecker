$(function() {
  $('.linkchecker-toggle').click(function() {
    $(this).next('.hide-show').toggle();
    $('.hide-show').not($(this).next('.hide-show')).hide();

    $('span', this).toggleClass('icon-arrow-up icon-arrow-down');

    classes = $(this).attr('class')
    createCookie('active-link', classes, 1)
  });

  openActiveLink();
});

function openActiveLink() {
  var activeCookie = readCookie('active-link');
  var activeLinkClasses = '.'.concat(activeCookie.split(' ').join('.'));

  var activeElement = $(activeLinkClasses);
  if ( activeElement.length ) {
    activeElement.next('.hide-show').toggle()

    // Source: https://stackoverflow.com/a/6677069/10750109
    $([document.documentElement, document.body]).animate({
      scrollTop: activeElement.offset().top
    }, 0);
  }
}

// Source https://stackoverflow.com/a/1599291/10750109
function createCookie(name, value, days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    var expires = "; expires=" + date.toGMTString();
  }
  else var expires = "";

  document.cookie = name + "=" + value + expires + "; path=/";
}

function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}
