# Logixinity Marketing Website — High-Level Solution Design Document

**Version:** 1.0  
**Date:** May 2026  
**Author:** Engineering Team  
**Status:** Live / Production  
**URL:** https://www.logixinity.com

---

## 1. Overview

The Logixinity website is the public-facing marketing and content platform for Logixinity — an Australian company building AI-driven financial products. The site introduces the company's product suite, drives user acquisition, hosts the company blog, and links visitors directly into the product apps.

The website is a **static multi-page site** — no backend server, no database, no build pipeline. All pages are plain HTML, CSS, and vanilla JavaScript, deployed as static files.

---

## 2. Goals & Objectives

- Introduce Logixinity and its product suite to prospective users
- Drive sign-ups to Propiq (and Gen LXI when launched)
- Host the company blog for SEO and thought leadership
- Provide a dedicated product landing page for Propiq
- Allow the internal team to manage blog content via a lightweight admin panel
- Be fast, SEO-friendly, and mobile-responsive with zero dependencies

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌────────────────────────────────────────────────┐
│          Visitor (Browser / Mobile)             │
└───────────────────┬────────────────────────────┘
                    │ HTTPS
┌───────────────────▼────────────────────────────┐
│         Static File Hosting (GitHub Pages       │
│         or Vercel / Netlify equivalent)         │
│                                                 │
│   index.html      — Home / landing page         │
│   propiq.html     — Propiq product page         │
│   blog.html       — Blog list + article view    │
│   gen-lxi.html    — Gen LXI product page        │
│   admin.html      — Internal blog admin panel   │
│   blog-admin.html — Blog post editor            │
│   css/styles.css  — Global styles               │
│   css/propiq.css  — Propiq page styles          │
│   css/admin.css   — Admin panel styles          │
│   assets/         — Images, logos               │
└────────────────────────────────────────────────┘
```

### 3.2 Deployment

| Layer | Technology |
|---|---|
| Hosting | GitHub Pages (static) |
| Domain | www.logixinity.com |
| CI/CD | Git push to `main` → auto-deploy |
| Repository | GitHub (RamananRaj/logixinity) |
| HTTPS | Enforced via GitHub Pages / CDN |

There is **no server-side code**, no API, and no database. All dynamic behaviour (blog loading, admin editing) is handled entirely in the browser via vanilla JavaScript.

---

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Markup | Plain HTML5 |
| Styling | Plain CSS3 (no framework) |
| Scripting | Vanilla JavaScript (ES6+) |
| Fonts | Google Fonts — Inter |
| Icons | Inline SVG |
| Content storage | Supabase (blog posts, via JS client in browser) |
| Payments/Auth | None (links out to propiq.logixinity.com) |

---

## 5. Site Structure

### 5.1 Pages

| Page | File | Purpose |
|---|---|---|
| **Home** | `index.html` | Company landing page — hero, product cards, how it works, about |
| **Propiq** | `propiq.html` | Dedicated product page for Propiq with features, tools, pricing, and CTAs |
| **Gen LXI** | `gen-lxi.html` | Future product page for Gen LXI (AI for accountants — currently hidden in nav) |
| **Blog** | `blog.html` | Blog article list + individual article view (SPA-style, single file) |
| **Admin** | `admin.html` | Internal admin panel — manage blog posts, view stats, edit content |
| **Blog Admin** | `blog-admin.html` | Blog post editor (create/edit posts) |
| **Propiq Mockup** | `propiq_image_macbook.html` | Standalone HTML mockup used for generating marketing images |
| **Accountant AI Admin** | `accountant-ai-admin.html` | Admin section for Gen LXI content (future) |

### 5.2 Stylesheets

| File | Scope |
|---|---|
| `css/styles.css` | Global site styles — nav, hero, sections, footer, utilities |
| `css/propiq.css` | Propiq product page specific styles |
| `css/admin.css` | Admin panel dark-theme styles |
| `css/accountant-ai.css` | Gen LXI page styles |

---

## 6. Page Descriptions

### 6.1 Home (`index.html`)

The primary marketing landing page. Sections:

- **Navigation** — Logo + nav links (Propiq, How it works, About, Blog) + Login dropdown + CTA button
- **Hero** — Headline, product description cards, dual CTA buttons, feature pills
- **Stats bar** — AI-powered / AUS-built trust signals
- **Products** — Product cards for Propiq (and Gen LXI, currently hidden)
- **How it works** — 3-step walkthrough (Create account → Connect data → AI insights)
- **About** — Company mission, Melbourne origin, team philosophy
- **Footer** — Links, legal, social

The **Login dropdown** is a custom-built accessible dropdown (ARIA `haspopup`) listing available apps. Currently shows Propiq only; Gen LXI shown as "Coming soon".

### 6.2 Propiq Product Page (`propiq.html`)

Dedicated landing page for Propiq with:
- Feature highlights (income tracking, dashboard, calculators, advisor chat)
- Embedded or linked free calculators section (`#tools`)
- Subscription plan comparison
- Direct CTAs to sign up at `propiq.logixinity.com`

### 6.3 Blog (`blog.html`)

A single-page application rendered in one HTML file:
- **List view** — Cards for all published posts, filterable by tag
- **Article view** — Full post rendered dynamically when a card is clicked (no page reload)
- Posts are fetched from **Supabase** via the JS client embedded in the page
- Tag filter bar with category chips (Property, Investment, Tax, AI, etc.)
- Featured post highlighted at top

### 6.4 Admin Panel (`admin.html`)

Password-protected internal tool (client-side protection only — `noindex, nofollow` set):
- Sidebar navigation with sections for Blog, Gen LXI content, and site settings
- Blog post list — view, publish/unpublish, feature, delete
- Stats overview
- Dark-themed UI consistent with a developer-facing internal tool

### 6.5 Blog Admin / Editor (`blog-admin.html`)

Rich editor for creating and editing blog posts:
- Fields: Title, excerpt, author, category, tags, date, featured toggle, published toggle
- Full HTML content area (raw HTML editing, monospace font)
- Saves to Supabase on submit
- Responsive editor grid (2-col on desktop, 1-col on mobile)

---

## 7. Content Management

Blog content is managed via the internal admin panel rather than a CMS. The flow is:

```
Author writes post in blog-admin.html editor
  → Saves to Supabase (blog_posts table)
    → blog.html fetches and renders posts on page load
```

No build step is required. Published posts appear on the live site immediately.

### Blog Post Schema (Supabase)

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| title | string | Post title |
| content | text | Full HTML content |
| excerpt | string | Short summary for list view |
| author | string | Author name |
| category | string | Primary category |
| tags | string[] | Filter tags |
| date | date | Publication date |
| featured | boolean | Pin to top of list |
| published | boolean | Visible on site |
| created_at | timestamp | — |

---

## 8. Navigation & Routing

The site uses **anchor-based navigation** within pages (e.g. `#products`, `#how`, `#about`) and standard HTML links between pages. There is no client-side router.

The blog implements a lightweight **SPA pattern** within a single HTML file — clicking a post card hides the list view and shows the article view by toggling CSS classes and injecting content via JavaScript.

---

## 9. SEO & Meta

- Each page has unique `<title>`, `<meta name="description">`, and Open Graph tags
- `robots` meta is set to `index, follow` on public pages and `noindex, nofollow` on admin pages
- Semantic HTML with `<header>`, `<nav>`, `<section>`, `<article>`, `<footer>` elements
- ARIA labels on interactive navigation elements

---

## 10. Product Suite (Current & Roadmap)

| Product | Status | Target Audience | URL |
|---|---|---|---|
| **Propiq** | Live | Australian property investors | propiq.logixinity.com |
| **Gen LXI** | Coming Soon | Accountants & businesses (Xero integration) | TBD |

Gen LXI features (planned): Xero integration, AI-driven business insights, automated reports, anomaly detection, multi-client management.

---

## 11. External Links & Integrations

| Destination | Purpose |
|---|---|
| `propiq.logixinity.com` | CTA for Propiq sign-up and login |
| Google Fonts (Inter) | Typography |
| Supabase JS client | Blog post read/write from browser |

No analytics, tracking pixels, or ad scripts are present. The site is ad-free.

---

## 12. Non-Functional Requirements

| Requirement | Approach |
|---|---|
| **Performance** | Static HTML — no JS framework overhead; fonts preconnected |
| **Mobile responsiveness** | CSS media queries throughout; mobile hamburger nav |
| **SEO** | Semantic HTML, complete meta tags, clean URL structure |
| **Accessibility** | ARIA attributes on nav, `alt` text on images, semantic landmarks |
| **Security** | Static site — minimal attack surface; admin is client-side only |
| **Maintainability** | Plain HTML/CSS/JS — no build tools, no npm, zero dependencies |

---

## 13. Known Limitations & Future Considerations

- **Admin authentication** is client-side only — not suitable for sensitive data; a server-side auth layer should be added if content sensitivity increases
- **Blog editor** uses raw HTML input — a rich text editor (e.g. Tiptap or Quill) would improve the authoring experience
- **No analytics** currently — Google Analytics or Plausible should be considered for traffic insights
- **Gen LXI content** is hidden in the navigation pending product launch — content and routing are prepared but not yet public
- **Contact / enquiry form** is not yet present — a Formspree or similar no-backend form solution would be easy to add
- As the product suite grows, migrating to a proper static site generator (Astro, Next.js) would simplify multi-page management and enable MDX-based blog authoring
