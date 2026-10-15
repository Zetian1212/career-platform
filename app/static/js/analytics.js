// Google Analytics behind a consent banner (Consent Mode v2, basic mode).
// Nothing is sent to Google and no cookie is set until the visitor clicks Accept.
(function () {
  var script = document.currentScript;
  var measurementId = script && script.dataset.gaId;
  var STORAGE_KEY = 'analytics-consent';
  if (!measurementId) return;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied'
  });

  function readChoice() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  function saveChoice(choice) {
    try { localStorage.setItem(STORAGE_KEY, choice); } catch (e) { /* choice lasts for this page only */ }
  }

  var loaded = false;
  function loadAnalytics() {
    if (loaded) return;
    loaded = true;
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('js', new Date());
    gtag('config', measurementId);
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    document.head.appendChild(tag);
  }

  function clearAnalyticsCookies() {
    var host = location.hostname;
    var domains = ['', host, '.' + host, '.' + host.split('.').slice(-2).join('.')];
    document.cookie.split(';').forEach(function (pair) {
      var name = pair.split('=')[0].trim();
      if (name !== '_ga' && name.indexOf('_ga_') !== 0) return;
      domains.forEach(function (domain) {
        document.cookie = name + '=; Max-Age=0; path=/' + (domain ? '; domain=' + domain : '');
      });
    });
  }

  function setUp() {
    var banner = document.getElementById('consent-banner');
    var settings = document.getElementById('consent-settings');
    if (!banner) return;

    function show() { banner.hidden = false; }
    function hide() { banner.hidden = true; }

    banner.querySelector('[data-consent="accept"]').addEventListener('click', function () {
      saveChoice('granted');
      hide();
      loadAnalytics();
    });
    banner.querySelector('[data-consent="decline"]').addEventListener('click', function () {
      saveChoice('denied');
      hide();
      gtag('consent', 'update', { analytics_storage: 'denied' });
      clearAnalyticsCookies();
    });
    if (settings) {
      settings.hidden = false;
      settings.addEventListener('click', show);
    }

    if (readChoice() === null) show();
  }

  if (readChoice() === 'granted') loadAnalytics();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setUp);
  } else {
    setUp();
  }
})();
