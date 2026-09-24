/**
 * AgriConnect Instant Dual-Language (English / Hindi) Localization Engine.
 * Enables 1-click seamless toggle between rural Hindi and urban English interfaces.
 */

(function () {
  const translations = {
    en: {
      navHome: "Home",
      navMarketplace: "Marketplace",
      navMandiRates: "Mandi Rates",
      navAnalytics: "Impact Analytics",
      navIVR: "IVR Demo",
      navGroupBuy: "Group Buying",
      navBasket: "Basket",
      heroHeadline: "Fresh Farm Harvest, Straight to Your Table. Zero Middlemen.",
      heroSub: "Connecting village farmers directly with urban households through assisted-digital facilitation. Farmers earn 75%+ realization; you save 25% on fresh harvest.",
      btnJoin: "Join Network",
      btnBrowseMarket: "Browse Farm Marketplace",
      objection1: "< 24h Farm-to-Fork",
      objection2: "75%+ Direct Farmer Payout",
      objection3: "100% Price Transparency",
      objection4: "Assisted VDF Access",
    },
    hi: {
      navHome: "होम (Home)",
      navMarketplace: "फसल बाजार (Market)",
      navMandiRates: "मंडी भाव (Mandi)",
      navAnalytics: "प्रभाव आंकड़े (Analytics)",
      navIVR: "आईवीआर फोन (IVR)",
      navGroupBuy: "सामूहिक खरीद (Group Buy)",
      navBasket: "टोकरी (Basket)",
      heroHeadline: "खेत से ताज़ा फसल, सीधे आपकी थाली तक। बिचौलियों का अंत।",
      heroSub: "ग्राम डिजिटल मित्रों के माध्यम से सीधे गांव के किसानों को शहरी परिवारों से जोड़ना। किसान को 75%+ वाजिब दाम, उपभोक्ता को 25% तक बचत।",
      btnJoin: "नेटवर्क से जुड़ें",
      btnBrowseMarket: "ताज़ा फसल बाजार देखें",
      objection1: "24 घंटे में खेत से थाली तक",
      objection2: "75%+ सीधा किसान भुगतान",
      objection3: "100% पारदर्शी दाम",
      objection4: "ग्राम मित्र द्वारा सहायता",
    }
  };

  let currentLang = localStorage.getItem('agriconnect_lang') || 'en';

  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('agriconnect_lang', lang);

    // Update toggle button text & flag
    const btn = document.getElementById('langToggleBtn');
    if (btn) {
      btn.innerHTML = lang === 'en' ? '🇮🇳 <strong>हिंदी</strong>' : '🇬🇧 <strong>English</strong>';
      btn.title = lang === 'en' ? 'हिंदी में बदलें (Switch to Hindi)' : 'Switch to English';
    }

    // Apply translations by data-i18n attributes or known IDs
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[lang] && translations[lang][key]) {
        el.innerText = translations[lang][key];
      }
    });

    // Optional toast
    console.log(`[AgriConnect] Language switched to: ${lang.toUpperCase()}`);
  }

  window.toggleAgriLanguage = function () {
    const nextLang = currentLang === 'en' ? 'hi' : 'en';
    applyLanguage(nextLang);
  };

  document.addEventListener('DOMContentLoaded', () => {
    applyLanguage(currentLang);
  });
})();
