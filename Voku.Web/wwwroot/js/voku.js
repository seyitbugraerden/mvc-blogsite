/*-----------------------------------------------------------------------------------*/
/* 	VOKU MAIN JS
/*-----------------------------------------------------------------------------------*/
(function($) {
"use strict";
/*-----------------------------------------------------------------------------------*/
/* 	SINGLE SLIDE
/*-----------------------------------------------------------------------------------*/
$(".single-slides").owlCarousel({ 
    items : 1,
	autoplay:false,
	autoplayHoverPause:true,
	singleItem	: true,
	navText: ["<i class='fa fa-angle-left'></i>","<i class='fa fa-angle-right'></i>"],
	lazyLoad:true,
	nav: true,
	loop: true,
	animateOut: 'fadeOut'	
});
/*-----------------------------------------------------------------------------------
    Animated progress bars
/*-----------------------------------------------------------------------------------*/
$('.progress-bars').waypoint(function() {
  $('.progress').each(function(){
    $(this).find('.progress-bar').animate({
      width:$(this).attr('data-percent')
     },200);
});},
	{ 
	offset: '100%',
    triggerOnce: true 
});
})(jQuery);








