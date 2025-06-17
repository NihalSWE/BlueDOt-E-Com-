/***************************************************
==================== JS INDEX ======================
****************************************************

01. PreLoader Js
02. Common Js
03. Menu Controls JS
04. Offcanvas Js
05. Search Js
06. One Page Scroll Js
07. Body overlay Js
08. cartmini-open-btn
09. Smooth Scroll Js
10. BeforeAfter Js
11. Sticky Header Js
12. Header Height Js
13. Sidebar Js
14. backtotop Js
15. Nice Select Js
16. magnificPopup img view 
17. magnificPopup video view
18. Ecommerce Cart Js
19. Show Login Toggle Js
20. Show Coupon Toggle Js
21. Create An Account Toggle Js
22. Shipping Box Toggle Js
23. Wow Js
24. Counter Js
25. Jquery proggess ber
26. parallax
27. circle percent 
28. header language
29. cursor style
30. tp-btn-trigger
31. gsap-costom-hover
32. Password Toggle Js



****************************************************/


(function ($) {
	"use strict";

	var windowOn = $(window);
	
	////////////////////////////////////////////////////
	// 01. PreLoader Js
	windowOn.on('load', function () {
		$(".loader-wrapper").fadeOut(500);
	});


	////////////////////////////////////////////////////
	// 02. Common Js

	$("[data-background").each(function () {
		$(this).css("background-image", "url( " + $(this).attr("data-background") + "  )");
	});

	$("[data-width]").each(function () {
		$(this).css("width", $(this).attr("data-width"));
	});

	$("[data-bg-color]").each(function () {
		$(this).css("background-color", $(this).attr("data-bg-color"));
	});

	$("[data-text-color]").each(function () {
		$(this).css("color", $(this).attr("data-text-color"));
	});



	////////////////////////////////////////////////////
	// 03. Menu Controls JS
	$('.tp-hamburger-toggle').on('click', function(){
		$('.tp-header-side-menu').slideToggle('tp-header-side-menu');
	});

	if($('.tp-main-menu-content').length && $('.tp-main-menu-mobile').length){
		let navContent = document.querySelector(".tp-main-menu-content").outerHTML;
		let mobileNavContainer = document.querySelector(".tp-main-menu-mobile");
		mobileNavContainer.innerHTML = navContent;
		let arrow = $(".tp-main-menu-mobile .has-dropdown > a");
		arrow.each(function () {
			let self = $(this);
			let arrowBtn = document.createElement("BUTTON");
			arrowBtn.classList.add("dropdown-toggle-btn");
			arrowBtn.innerHTML = "<i class='fa-regular fa-angle-right'></i>";
	
			self.append(function () {
			  return arrowBtn;
			});
	
			self.find("button").on("click", function (e) {
			  e.preventDefault();
			  let self = $(this);
			  self.toggleClass("dropdown-opened");
			  self.parent().toggleClass("expanded");
			  self.parent().parent().addClass("dropdown-opened").siblings().removeClass("dropdown-opened");
			  self.parent().parent().children(".tp-submenu").slideToggle();
			});
	
		  });
	}


	
	
	////////////////////////////////////////////////////
	// 04. Offcanvas Js
	$(".tp-offcanvas-open-btn").on("click", function () {
		$(".offcanvas__area").addClass("offcanvas-opened");
		$(".body-overlay").addClass("opened");
	});
	$(".offcanvas-close-btn").on("click", function () {
		$(".offcanvas__area").removeClass("offcanvas-opened");
		$(".body-overlay").removeClass("opened");
	});



	// ////////////////////////////////////////////////////
	// // 05. Search Js
	 if($('.search-box-outer').length) {
		$('.search-box-outer').on('click', function() {
			$('body').addClass('search-active');
		});
		$('.close-search').on('click', function() {
			$('body').removeClass('search-active');
		});
	}

	
    ////////////////////////////////////////////////////
	// 06. One Page Scroll Js
	function scrollNav() {
		$('.tp-onepage-menu li a').click(function () {
			$(".tp-onepage-menu li a.active").removeClass("active");
			$(this).addClass("active");

			$('html, body').stop().animate({
				scrollTop: $($(this).attr('href')).offset().top - 80
			}, 300);
			return false;
		});
	}
	scrollNav();



	////////////////////////////////////////////////////
	// 07. Body overlay Js
	$(".body-overlay").on("click", function () {
		$(".offcanvas__area").removeClass("offcanvas-opened");
		$(".tp-search-area").removeClass("opened");
		$(".cartmini__area").removeClass("cartmini-opened");
		$(".body-overlay").removeClass("opened");
	});



	////////////////////////////////////////////////////
	// 08. cartmini-open-btn
	$(".cartmini-open-btn").on("click", function () {
		$(".cartmini__area").addClass("cartmini-opened");
		$(".cartmini-overlay").addClass("openeds");
	});
	$(".cartmini-close-btn").on("click", function () {
		$(".cartmini__area").removeClass("cartmini-opened");
		$(".cartmini-overlay").removeClass("openeds");
	});
	$(".cartmini-overlay").on("click", function () {
		$(".cartmini__area").removeClass("cartmini-opened");
		$(".cartmini-overlay").removeClass("openeds");
	});



	////////////////////////////////////////////////////
	// 09. Smooth Scroll Js
	function smoothSctoll() {
		$('.smooth a').on('click', function (event) {
			var target = $(this.getAttribute('href'));
			if (target.length) {
				event.preventDefault();
				$('html, body').stop().animate({
					scrollTop: target.offset().top - 120
				}, 1500);
			}
		});
	}
	smoothSctoll();
	if($('#smooth-wrapper').length && $('#smooth-content').length){
		gsap.registerPlugin(ScrollTrigger, ScrollSmoother, TweenMax, ScrollToPlugin);
	
		gsap.config({
			nullTargetWarn: false,
		});
	
		let smoother = ScrollSmoother.create({
			smooth: 2,
			effects: true,
			smoothTouch: 0.1,
			normalizeScroll: false,
			ignoreMobileResize: true,
		});

	}


	// split text animation
	var st = $(".tp-split-text");
	if(st.length == 0) return;
	gsap.registerPlugin(SplitText);
	st.each(function(index, el) {
		el.split = new SplitText(el, {
			type: "lines,words,chars",
			linesClass: "tp-split-line"
		});
		gsap.set(el, { perspective: 400 });
		if( $(el).hasClass('right') ){
			gsap.set(el.split.chars, {
				opacity: 0,
				x: "50",
				ease: "Back.easeOut",
			});
		}
		if( $(el).hasClass('left') ){
			gsap.set(el.split.chars, {
				opacity: 0,
				x: "-50",
				ease: "circ.out",
			});
		}
		if( $(el).hasClass('up') ){
			gsap.set(el.split.chars, {
				opacity: 0,
				y: "80",
				ease: "circ.out",
			});
		}
		if( $(el).hasClass('down') ){
			gsap.set(el.split.chars, {
				opacity: 0,
				y: "-80",
				ease: "circ.out",
			});
		}
		el.anim = gsap.to(el.split.chars, {
			scrollTrigger: {
				trigger: el,
				start: "top 90%",
			},
			x: "0",
			y: "0",
			rotateX: "0",
			scale: 1,
			opacity: 1,
			duration: 0.4,
			stagger: 0.02,
		});
	});


	
	////////////////////////////////////////////////////
	// 10. BeforeAfter Js
	if ($(".beforeAfter").length > 0) {
		$('.beforeAfter').beforeAfter({
			movable: true,
			clickMove: true,
			position: 50,
			separatorColor: '#fafafa',
			bulletColor: '#fafafa',
			onMoveStart: function (e) {
				console.log(event.target);
			},
			onMoving: function () {
				console.log(event.target);
			},
			onMoveEnd: function () {
				console.log(event.target);
			},
		});
	}


	///////////////////////////////////////////////////
	// 11. Sticky Header Js
	windowOn.on('scroll', function () {
		var scroll = windowOn.scrollTop();
		if (scroll < 200) {
			$("#header-sticky").removeClass("header-sticky");
		} else {
			$("#header-sticky").addClass("header-sticky");
		}
	});


	///////////////////////////////////////////////////
	// 12. Header Height Js
	if ($('.tp-header-height').length > 0) {
		var headerHeight = document.querySelector(".tp-header-height");
		var setHeaderHeight = headerHeight.offsetHeight;
		$(".tp-header-height").each(function () {
			$(this).css({
				'height': setHeaderHeight + 'px'
			});
		});

		$(".tp-header-height.header-sticky").each(function () {
			$(this).css({
				'height': inherit,
			});
		});
	}


	////////////////////////////////////////////////////
	// 13. Sidebar Js
	$(".tp-menu-bar").on("click", function () {
		$(".tpoffcanvas").addClass("opened");
		$(".body-overlay").addClass("apply");
	});
	$(".close-btn").on("click", function () {
		$(".tpoffcanvas").removeClass("opened");
		$(".body-overlay").removeClass("apply");
	});
	$(".body-overlay").on("click", function () {
		$(".tpoffcanvas").removeClass("opened");
		$(".body-overlay").removeClass("apply");
	});



	////////////////////////////////////////////////////
  	// 14. backtotop Js
	  function back_to_top() {
		var btn = $('#back_to_top');
		var btn_wrapper = $('.back-to-top-wrapper');

		windowOn.scroll(function () {
			if (windowOn.scrollTop() > 300) {
				btn_wrapper.addClass('back-to-top-btn-show');
			} else {
				btn_wrapper.removeClass('back-to-top-btn-show');
			}
		});

		btn.on('click', function (e) {
			e.preventDefault();
			$('html, body').animate({ scrollTop: 0 }, '300');
		});
	}
	back_to_top();


	////////////////////////////////////////////////////
	// 15. Nice Select Js
	$('.tp-header-search-category select').niceSelect();


	////////////////////////////////////////////////////
	// 16. magnificPopup img view 
	$('.popup-image').magnificPopup({
		// delegate: 'a',
		type: 'image',
		gallery: {
			enabled: true
		}
	});


	////////////////////////////////////////////////////
	// 17. magnificPopup video view
	$(".popup-video").magnificPopup({
		type: "iframe",
	});


	////////////////////////////////////////////////////
	// 18. Ecommerce Cart Js
	function tp_ecommerce() {
		$('.tp-cart-minus').on('click', function () {
			var $input = $(this).parent().find('input');
			var count = Number($input.val()) - 1;
			count = count < 1 ? 1 : count;
			$input.val(count);
			$input.change();
			return false;
		});
	
		$('.tp-cart-plus').on('click', function () {
			var $input = $(this).parent().find('input');
			$input.val(Number($input.val()) + 1);
			$input.change();
			return false;
		});

		$("#slider-range").slider({
			range: true,
			min: 0,
			max: 500,
			values: [75, 300],
			slide: function (event, ui) {
				$("#amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
			}
		});
		$("#amount").val("$" + $("#slider-range").slider("values", 0) +
			" - $" + $("#slider-range").slider("values", 1));
	
		

		$('.tp-checkout-payment-item label').on('click', function () {
			$(this).siblings('.tp-checkout-payment-desc').slideToggle(400);
			
		});
		

		$('.tp-color-variation-btn').on('click', function () {
			$(this).addClass('active').siblings().removeClass('active');
		});
		

		$('.tp-size-variation-btn').on('click', function () {
			$(this).addClass('active').siblings().removeClass('active');
		});


	
		////////////////////////////////////////////////////
		// 19. Show Login Toggle Js
		$('.tp-checkout-login-form-reveal-btn').on('click', function () {
			$('#tpReturnCustomerLoginForm').slideToggle(400);
		});



	
		////////////////////////////////////////////////////
		// 20. Show Coupon Toggle Js
		$('.tp-checkout-coupon-form-reveal-btn').on('click', function () {
			$('#tpCheckoutCouponForm').slideToggle(400);
		});


	
		////////////////////////////////////////////////////
		// 21. Create An Account Toggle Js
		$('#cbox').on('click', function () {
			$('#cbox_info').slideToggle(900);
		});


	
		////////////////////////////////////////////////////
		// 22. Shipping Box Toggle Js
		$('#ship-box').on('click', function () {
			$('#ship-box-info').slideToggle(1000);
		});
	}
	tp_ecommerce();


	////////////////////////////////////////////////////
	// 23. Wow Js
	new WOW().init();


	////////////////////////////////////////////////////
	// 24. Counter Js
	new PureCounter();
	new PureCounter({
		filesizing: true,
		selector: ".filesizecount",
		pulse: 2,
	});




	////////////////////////////////////////////////////
	// 25. Jquery proggess ber
	if (typeof ($.fn.knob) != 'undefined') {
		$('.knob').each(function () {
		var $this = $(this),
		knobVal = $this.attr('data-rel');

		$this.knob({
		'draw': function () {
			$(this.i).val(this.cv + '%')
		}
		});

		$this.appear(function () {
		$({
			value: 0
		}).animate({
			value: knobVal
		}, {
			duration: 2000,
			easing: 'swing',
			step: function () {
			$this.val(Math.ceil(this.value)).trigger('change');
			}
		});
		}, {
		accX: 0,
		accY: -150,
		});
	});
	}


	////////////////////////////////////////////////////
	// 26. parallax 
	if ($('.scene').length > 0) {
		$('.scene').parallax({
			scalarX: 2,
			scalarY: 2,
		});
	};
	if ($('.scene-2').length > 0) {
		$('.scene-2').parallax({
			scalarX: 1,
			scalarY: 1,
		});
	};




	////////////////////////////////////////////////////
	// 27. circle percent 
	$(".circle_percent").each(function () {
        var $this = $(this),
            $dataV = $this.data("percent"),
            $dataDeg = $dataV * 3.6,
            $round = $this.find(".round_per");
        $round.css("transform", "rotate(" + parseInt($dataDeg + 180) + "deg)");
        $this.append('<div class="circle_inbox"><span class="percent_text"></span></div>');
        $this.prop('Counter', 0).animate({
            Counter: $dataV
        }, {
            duration: 3000,
            easing: 'swing',
            step: function (now) {
                $this.find(".percent_text").text(Math.ceil(now) + "%");
            }
        });
        if ($dataV >= 51) {
            $round.css("transform", "rotate(" + 360 + "deg)");
            setTimeout(function () {
                $this.addClass("percent_more");
            }, 1000);
            setTimeout(function () {
                $round.css("transform", "rotate(" + parseInt($dataDeg + 180) + "deg)");
            }, 1000);
        }
    });



	////////////////////////////////////////////////////
	// 28. header language
	if ($("#tp-header-lang-toggle").length > 0) {
		window.addEventListener('click', function(e){
	
			if (document.getElementById('tp-header-lang-toggle').contains(e.target)){
				$(".tp-lang-list").toggleClass("tp-lang-list-open");
			}
			else{
				$(".tp-lang-list").removeClass("tp-lang-list-open");
			}
		});
	}


	
	////////////////////////////////////////////////////
	// 29. cursor style
	document.addEventListener("DOMContentLoaded", function() {
		var cursor = document.querySelector(".cursor");
		var cursor2 = document.querySelector(".cursor2");
		document.addEventListener("mousemove", function(e) {
			cursor.style.cssText = cursor2.style.cssText = "left: " + e.clientX + "px; top: " + e.clientY + "px;";
		});
		var cursorScale = document.querySelectorAll('a, button, .brand-item,.swiper-button-prev,.swiper-button-next, .icons');
		cursorScale.forEach(link => {
			link.addEventListener('mousemove', () => {
				cursor.classList.add('grow');
				if (link.classList.contains('small')) {
					cursor.classList.remove('grow');
					cursor.classList.add('grow-small');
				}
			});
			link.addEventListener('mouseleave', () => {
				cursor.classList.remove('grow');
				cursor.classList.remove('grow-small');
			});
		});
	});
	

	///////////////////////////////////////////////////
	// 30. tp-btn-trigger
	if ($('.tp-btn-trigger').length > 0) {

		gsap.set(".tp-btn-bounce", { y: -100, opacity: 0 });
		var mybtn = gsap.utils.toArray(".tp-btn-bounce");
		mybtn.forEach((btn) => {
			var $this = $(btn);
			gsap.to(btn, {
				scrollTrigger: {
					trigger: $this.closest('.tp-btn-trigger'),
					start: "top center",
					markers: false
				},
				duration: 1,
				ease: "bounce.out",
				y: 0,
				opacity: 1,
			})
		});
	}



	///////////////////////////////////////////////////
	// 31. gsap-costom-hover
	var hoverBtns = gsap.utils.toArray(".tp-costom-wrapper-hover");
	const hoverBtnItem = gsap.utils.toArray(".tp-costom-inner-hover");
	hoverBtns.forEach((btn, i) => {
		$(btn).mousemove(function (e) {
			callParallax(e);
		});
		function callParallax(e) {
			parallaxIt(e, hoverBtnItem[i], 60);
		}

		function parallaxIt(e, target, movement) {
			var $this = $(btn);
			var relX = e.pageX - $this.offset().left;
			var relY = e.pageY - $this.offset().top;

			gsap.to(target, 1, {
				x: ((relX - $this.width() / 2) / $this.width()) * movement,
				y: ((relY - $this.height() / 2) / $this.height()) * movement,
				ease: Power2.easeOut,
			});
		}
		$(btn).mouseleave(function (e) {
			gsap.to(hoverBtnItem[i], 1, {
				x: 0,
				y: 0,
				ease: Power2.easeOut,
			});
		});
	});



	////////////////////////////////////////////////////
	// 32. Password Toggle Js
	if($('.password-show-toggle').length > 0){
		var showBtn = $('.password-show-toggle');
		showBtn.each(function (e) {
			$(this).on('click', function(x){
				let inputField = $(this).parent().find('input');
				if(inputField.attr('type') === "password"){
					inputField.attr('type', 'text')
					$(this).children('.open-eye-icon').css({
						'display' : 'block'
					})
					$(this).children('.close-eye-icon').css({
						'display' : 'none'
					})
				}else{
					inputField.attr('type', 'password')
					$(this).children('.open-eye-icon').css({
						'display' : 'none'
					})
					$(this).children('.close-eye-icon').css({
						'display' : 'block'
					})
				}
			})
		})
	}



})(jQuery);