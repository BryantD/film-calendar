/*
	Catalyst by Pixelarity
	pixelarity.com | hello@pixelarity.com
	License: pixelarity.com/license
*/

(function($) {

	var	$window = $(window),
		$body = $('body');

	// Breakpoints.
		breakpoints({
			wide:      [ '1281px',  '1680px' ],
			normal:    [ '981px',   '1280px' ],
			narrow:    [ '737px',   '980px'  ],
			mobile:    [ '481px',   '736px'  ],
			mobilep:   [ null,      '480px'  ]
		});

	// Play initial animations on page load.
		$window.on('load', function() {
			window.setTimeout(function() {
				$body.removeClass('is-preload');
			}, 100);
		});

	// Dropdowns.
		$('#nav > ul').dropotron({
			alignment: 'right'
		});

	// Nav Panel.

		// Title Bar.
			$(
				'<div id="navButton">' +
					'<a href="#navPanel" class="toggle"></a>' +
				'</div>'
			)
				.appendTo($body);

		// Panel.
			$(
				'<div id="navPanel">' +
					'<nav>' +
						$('#nav').navList() +
					'</nav>' +
				'</div>'
			)
				.appendTo($body)
				.panel({
					delay: 500,
					hideOnClick: true,
					hideOnSwipe: true,
					resetScroll: true,
					resetForms: true,
					side: 'left',
					target: $body,
					visibleClass: 'navPanel-visible'
				});

	// Banner.
		var $banner = $('#banner');

		if ($banner.length > 0) {

			// Parallax background.
				if (browser.name != 'ie'
				&&	browser.name != 'edge'
				&&	!browser.mobile) {

					var originalPosition = $banner.css('background-position');

					breakpoints.on('<=normal', function() {

						$window.off('scroll.px');
						$banner.css('background-position', originalPosition);

					});

					breakpoints.on('>normal', function() {

						$banner.css('background-position', 'center 0px');

						$window.on('scroll.px', function() {
							$banner.css('background-position', 'center ' + (parseInt($window.scrollTop()) * -0.5) + 'px');
						});

					});

				}

		}

})(jQuery);
