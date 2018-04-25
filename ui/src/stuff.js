const disqus_config = function () {
    this.page.url = 'http://gd77.sp5drs.xyz';
    this.page.identifier = 'gd77';
};

(function(window, d) {
    window.dataLayer = window.dataLayer || [];
    const gtag = () => {
      dataLayer.push(arguments);
    }
    gtag('js', (new Date()).toString());
    gtag('config', 'UA-220058-16');

    const s = d.createElement('script');
    s.src = 'https://gd77.disqus.com/embed.js';
    s.setAttribute('data-timestamp', Date.now());
    (d.head || d.body).appendChild(s);
})(window, document);
