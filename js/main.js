/* ============================================================
   Logixinity — main.js
   Handles: sticky nav highlight, smooth scroll, subtle
   hero entrance animation.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ----------------------------------------------------------
     1. NAV — add scrolled class for tighter bg on scroll
  ---------------------------------------------------------- */
  const nav = document.querySelector('.nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }

  /* ----------------------------------------------------------
     2. ACTIVE NAV LINK — highlight section in viewport
  ---------------------------------------------------------- */
  const sections = document.querySelectorAll('section[id], div[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  const observerOptions = {
    root: null,
    rootMargin: '-30% 0px -60% 0px',
    threshold: 0,
  };

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        navLinks.forEach((link) => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${entry.target.id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach((section) => sectionObserver.observe(section));

  /* ----------------------------------------------------------
     3. ENTRANCE ANIMATIONS — fade-up on scroll into view
  ---------------------------------------------------------- */
  const animTargets = document.querySelectorAll(
    '.product-card, .price-card, .how-step, .stat-item, .cta-banner'
  );

  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        fadeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  animTargets.forEach((el) => {
    el.classList.add('fade-up');
    fadeObserver.observe(el);
  });

  /* ----------------------------------------------------------
     4. SMOOTH SCROLL for anchor links
  ---------------------------------------------------------- */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 72; // nav height
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ----------------------------------------------------------
     5. MOBILE NAV TOGGLE (hamburger, injected dynamically)
  ---------------------------------------------------------- */
  const navInner = document.querySelector('.nav-inner');
  if (navInner) {
    const hamburger = document.createElement('button');
    hamburger.className = 'nav-hamburger';
    hamburger.setAttribute('aria-label', 'Toggle navigation');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
    `;
    navInner.appendChild(hamburger);

    const mobileMenu = document.querySelector('.nav-links');
    hamburger.addEventListener('click', () => {
      const open = hamburger.getAttribute('aria-expanded') === 'true';
      hamburger.setAttribute('aria-expanded', String(!open));
      hamburger.classList.toggle('open', !open);
      if (mobileMenu) mobileMenu.classList.toggle('mobile-open', !open);
    });

    // Close menu on link click
    navLinks.forEach((link) => {
      link.addEventListener('click', () => {
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.classList.remove('open');
        if (mobileMenu) mobileMenu.classList.remove('mobile-open');
      });
    });
  }

});
