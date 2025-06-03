
(function ($) {
	"use strict";




	// Home 1 project  slider
	var slider = new Swiper('.tp-project-active', {
		slidesPerView: 4,
		spaceBetween: 30,
		loop: true,
		speed:1500,
		autoplay: {
			delay: 4000,
		},
		breakpoints: {
			'1400': {
				slidesPerView: 4,
			},
			'1200': {
				slidesPerView: 3,
			},
			'992': {
				slidesPerView: 3,
			},
			'768': {
				slidesPerView: 1,
			},
			'576': {
				slidesPerView: 1,
			},
			'0': {
				slidesPerView: 1,
			},
		},
		pagination: {
			el: ".tp-project-dot",
			clickable: true,
			renderBullet: function (index, className) {
			  return '<span class="' + className + '">' + '<button>'+(index + 1)+'</button>' + "</span>";
			},
		},
	});


	// Home 1 Shop
	var slider = new Swiper('.tp-product-active', {
		slidesPerView: 4,
		spaceBetween: 30,
		loop: true,
		breakpoints: {
			'1200': {
				slidesPerView: 4,
			},
			'992': {
				slidesPerView: 3,
			},
			'768': {
				slidesPerView: 2,
			},
			'576': {
				slidesPerView: 2,
			},
			'0': {
				slidesPerView: 1,
			},
		},
		// Navigation arrows
		navigation: {
			nextEl: '.slider-next',
			prevEl: '.slider-prev',
		},
	});



	// Home 2 slider slide
	// All Hero slider
	const sliderswiper = new Swiper('.tp-slider-2-active', {
		// Optional parameters
		speed:1500,
		loop: true,
		slidesPerView: 1,
		autoplay: true,
		effect:'fade',
		breakpoints: {
			'1600': {
				slidesPerView:1,
			},
			'1400': {
				slidesPerView:1,
			},
			'1200': {
				slidesPerView:1,
			},
			'992': {
				slidesPerView: 1,
			},
			'768': {
				slidesPerView: 1,
			},
			'576': {
				slidesPerView: 1,
			},
			'0': {
				slidesPerView: 1,
			},

			a11y: false,
		},
		pagination: {
			el: ".tp-slider-2-dots",
			clickable:true,
		},

	});



	// Home 2 Project
	var slider = new Swiper('.tp-product-2-active', {
		slidesPerView: 4,
		spaceBetween: 30,
		loop: true,
		breakpoints: {
			'1200': {
				slidesPerView: 4,
			},
			'992': {
				slidesPerView: 3,
			},
			'768': {
				slidesPerView: 2,
			},
			'576': {
				slidesPerView: 2,
			},
			'0': {
				slidesPerView: 1,
			},
		},
		// Navigation arrows
		navigation: {
			nextEl: '.slider-next',
			prevEl: '.slider-prev',
		},
	})



	// Home 2 Testimonial
	var slider = new Swiper('.tp-testimonial-2-active', {
		slidesPerView: 3,
		spaceBetween: 30,
		loop: true,
		breakpoints: {
			'1200': {
				slidesPerView: 3,
			},
			'992': {
				slidesPerView: 2,
			},
			'768': {
				slidesPerView: 1,
			},
			'576': {
				slidesPerView: 1,
			},
			'0': {
				slidesPerView: 1,
			},
		},
		// Navigation arrows
		navigation: {
			nextEl: '.slider-next',
			prevEl: '.slider-prev',
		},
	})





	// Home 3 Testimonial

		$('.tp-testimonial-3-active').slick({
			slidesToShow: 1,
			slidesToScroll: 1,
			arrows: false,
			fade: false,
			asNavFor: '.tp-testimonial-3-img-active'
		});
	
		$('.tp-testimonial-3-img-active').slick({	
			slidesToShow: 3,
			slidesToScroll: 1,
			asNavFor: '.tp-testimonial-3-active',
			dots: false,
			arrows: false,
			focusOnSelect: true,
			centerPadding: '0',
			centerMode: true,
			responsive: [
			{
				breakpoint: 1200,
				settings: {
					slidesToShow: 3,
				}
			},
			{
				breakpoint: 992,
				settings: {
					slidesToShow: 3,
				}
			},
			{
				breakpoint: 768,
				settings: {
					slidesToShow: 1,
				}
			},
			{
				breakpoint: 480,
				settings: {
					arrows: false,
					slidesToShow: 1,
				}
			}
			
		]
	});



	// Home 3 Brand 
	var slider = new Swiper('.tp-brand-3-active', {
		slidesPerView: 4,
		spaceBetween: 30,
		speed:500,
		loop: true,
		autoplay:true,
		centeredSlides: true,
		breakpoints: {
			'1200': {
				slidesPerView: 5,
			},
			'992': {
				slidesPerView: 4,
			},
			'768': {
				slidesPerView: 3,
			},
			'576': {
				slidesPerView: 2,
			},
			'0': {
				slidesPerView: 2,
			},
		},
	});



	// Home 4 Project
	var slider = new Swiper('.tp-project-4-active', {
		slidesPerView: 5,
		spaceBetween: 30,
		loop: true,
		autoplay: {
			delay: 3000,
		},
		centeredSlides: true,
		speed:1000,
		breakpoints: {
			'1800': {
				slidesPerView: 5,
			},
			'1700': {
				slidesPerView: 4,
			},
			'1600': {
				slidesPerView: 4,
			},
			'1400': {
				slidesPerView: 4,
			},
			'1200': {
				slidesPerView: 3,
			},
			'992': {
				slidesPerView: 3,
			},
			'768': {
				slidesPerView: 2,
			},
			'576': {
				slidesPerView: 1,
			},
			'0': {
				slidesPerView: 1,
			},
		},
	});


	// Home 4 text-slider
	var textSlide = new Swiper(".tp-text-slider-active", {
		loop: true,
		freemode: true,
		slidesPerView: 'auto',
		spaceBetween: 30,
		centeredSlides: true,
		allowTouchMove: false,
		speed: 35000,
		autoplay: {
			delay: 1,
			disableOnInteraction: true,
		},
	});


	// Home 4 testimonial
	var slider = new Swiper('.tp-testimonial-4-active', {
		slidesPerView: 1,
		spaceBetween: 30,
		speed: 1500,
		autoplay:true,
		loop: true,
		pagination: {
			el: ".tp-testimonial-4-dot",
			clickable: true,
			renderBullet: function (index, className) {
			  return '<span class="' + className + '">' + '<button>'+(index + 1)+'</button>' + "</span>";
			},
		},
		breakpoints: {
			'1200': {
				slidesPerView: 1,
			},
			'992': {
				slidesPerView: 1,
			},
			'768': {
				slidesPerView: 1,
			},
			'576': {
				slidesPerView: 1,
			},
			'0': {
				slidesPerView: 1,
			},
		},
	});



	// Home 4 Brand 
	var slider = new Swiper('.tp-brand-2-active', {
		slidesPerView: 4,
		spaceBetween: 30,
		loop: true,
		autoplay:true,
		centeredSlides: true,
		breakpoints: {
			'1200': {
				slidesPerView: 5,
			},
			'992': {
				slidesPerView: 4,
			},
			'768': {
				slidesPerView: 3,
			},
			'576': {
				slidesPerView: 2,
			},
			'0': {
				slidesPerView: 2,
			},
		},
	});



	// Home 5 testimonial 
	var slider = new Swiper('.tp-testimonial-5-active', {
		spaceBetween: 30,
		loop: true,
		speed: 1500,
		breakpoints: {
			'1200': {
				slidesPerView: 1,
			},
			'992': {
				slidesPerView: 1,
			},
			'768': {
				slidesPerView: 1,
			},
			'576': {
				slidesPerView: 1,
			},
			'0': {
				slidesPerView: 1,
			},
		},
		// Navigation arrows
		navigation: {
			nextEl: '.slider-next',
			prevEl: '.slider-prev',
		},
	});










})(jQuery);