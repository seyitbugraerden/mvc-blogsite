document.addEventListener('submit', function (event) {
    event.preventDefault(); event.stopImmediatePropagation();
    let notice = event.target.querySelector('.form-notice');
    if (!notice) { notice = document.createElement('p'); notice.className = 'form-notice'; notice.setAttribute('role', 'status'); event.target.appendChild(notice); }
    notice.textContent = 'Form gönderimi henüz aktif değil. Bilgileriniz gönderilmedi ve kaydedilmedi.';
}, true);
(function ($) {
    if ($.fn.owlCarousel) $('.single-slides').owlCarousel({items:1,nav:true,loop:true,autoplay:false,navText:['<i class="fa fa-angle-left"></i>','<i class="fa fa-angle-right"></i>']});
    $('.progress').each(function () { $(this).find('.progress-bar').css('width', $(this).attr('data-percent')); });
    if ($.fn.prettyPhoto) $('a[data-rel="prettyPhoto"]').prettyPhoto({social_tools:false});
})(jQuery);
