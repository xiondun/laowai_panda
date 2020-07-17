$(document).ready(function () {
    // $('body').css({
    //     paddingTop: $('nav.navbar').outerHeight() 
    // })
    // Header scroll class

          // Start Scroll To Top  
  $(window).scroll(function() {

    var scrollToTop = $(".scroll-to-top");

    if ($(window).scrollTop() >= 300) {

      scrollToTop.fadeIn(500);
    
    } else {

      scrollToTop.fadeOut(500);

    }

  })
  // End Scroll To Top  

  $(".scroll-to-top").click(function (e) {

    e.preventDefault();

    $("html, body").animate({

      scrollTop: 0

    }, 1000);

  })

    // Navbar scrolling 
    $('nav.navbar .navbar-nav .nav-link').on('click', function (e) {
        var targetHref = $(this).attr('href');

        $('html, body').animate({
            scrollTop: $(targetHref).offset().top - 120
        }, 1000);


        e.preventDefault();
        
    })
    $(window).scroll(function () {
        if ($(this).scrollTop() > 75) {
            $('nav.navbar').addClass('header-scrolled');
            $('.navbar-brand img').css({
                width: 30
            })
        } else {
            $('nav.navbar').removeClass('header-scrolled');
            $('.navbar-brand img').css({
                width: 50
            })
        }
    });

    //  Tilt Js
    $('.single-feature').tilt({
        maxTilt: 9,
    });
    // INITIATE THE FOOTER
    siteFooter();
    // COULD BE SIMPLIFIED FOR THIS PEN BUT I WANT TO MAKE IT AS EASY TO PUT INTO YOUR SITE AS POSSIBLE
    $(window).resize(function () {
        siteFooter();
    });

    function siteFooter() {
        var siteContent = $('#site-wrapper');
        var siteFooter = $('#site-footer');
        var siteFooterHeight = siteFooter.height();
        siteContent.css({
            "margin-bottom": siteFooterHeight + 50
        });
    };

})