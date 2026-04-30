import {
  ArrowRight,
  Award,
  BadgeDollarSign,
  Banknote,
  BriefcaseBusiness,
  Building2,
  Car,
  CheckCircle2,
  ChevronRight,
  CreditCard,
  Globe,
  Landmark,
  LineChart,
  LockKeyhole,
  Mail,
  MapPin,
  Menu,
  Phone,
  PiggyBank,
  Shield,
  ShieldCheck,
  Smartphone,
  Star,
  TrendingUp,
  Users,
  WalletCards,
  Zap,
} from "lucide-react"
import { ContactForm } from "./ContactForm"
import { HomeSignInPanel } from "./HomeSignInPanel"

const productNav = [
  ["Checking", "/checking"],
  ["Savings & CDs", "/savings"],
  ["Credit Cards", "/credit-cards"],
  ["Home Loans", "/home-loans"],
  ["Auto", "/auto"],
  ["Business", "/business"],
  ["Investing", "/investing"],
]

const homeProducts = [
  {
    icon: WalletCards,
    title: "Checking Accounts",
    text: "Choose everyday banking with online bill pay, debit card access, mobile deposits, and clear balance visibility.",
    href: "/checking",
    cta: "Explore checking",
  },
  {
    icon: PiggyBank,
    title: "Savings Accounts & CDs",
    text: "Build savings goals, track progress, and keep reserve funds separate from operating cash.",
    href: "/savings",
    cta: "Start saving",
  },
  {
    icon: CreditCard,
    title: "Credit Cards",
    text: "Issue cards, manage spend limits, and monitor activity with controls that fit daily life and business operations.",
    href: "/credit-cards",
    cta: "Compare cards",
  },
  {
    icon: Building2,
    title: "Home Loans",
    text: "Plan mortgage payments, organize documents, and keep housing costs visible inside the same financial workspace.",
    href: "/home-loans",
    cta: "View loans",
  },
  {
    icon: Car,
    title: "Auto",
    text: "Track auto financing, estimate payment impact, and keep loan obligations aligned with your budget.",
    href: "/auto",
    cta: "Explore auto",
  },
  {
    icon: BriefcaseBusiness,
    title: "Business Banking",
    text: "Manage business accounts, card programs, approvals, reports, and roles from a single operating layer.",
    href: "/business",
    cta: "See business tools",
  },
  {
    icon: LineChart,
    title: "Investing",
    text: "Connect long-term goals, investment accounts, and portfolio movement with everyday cash decisions.",
    href: "/investing",
    cta: "Explore investing",
  },
  {
    icon: ShieldCheck,
    title: "Security Center",
    text: "Protect accounts with MFA, step-up checks, trusted devices, audit records, and role-aware access controls.",
    href: "/security",
    cta: "Review security",
  },
]

const categoryPages = {
  checking: {
    icon: WalletCards,
    eyebrow: "Checking",
    title: "Bank from anywhere with accounts built for daily movement.",
    text: "VaultWise checking gives customers a clean place to manage cash, debit activity, transfers, statements, and account health.",
    primary: "Open checking",
    highlights: ["Online and mobile banking", "Debit card controls", "Bill pay and transfers", "Statements and transaction history"],
  },
  savings: {
    icon: PiggyBank,
    eyebrow: "Savings & CDs",
    title: "Set money aside with goals, reserves, and progress you can actually see.",
    text: "Keep emergency funds, business reserves, and planned savings organized beside the accounts that fund them.",
    primary: "Start saving",
    highlights: ["Goal tracking", "Reserve accounts", "Automated transfers", "Monthly savings reports"],
  },
  "credit-cards": {
    icon: CreditCard,
    eyebrow: "Credit cards",
    title: "Cards with practical controls for households and teams.",
    text: "Issue physical or virtual cards, monitor spend, set limits, and turn controls on before activity becomes a problem.",
    primary: "Compare cards",
    highlights: ["Virtual and physical cards", "Spend limits", "Merchant category blocks", "Instant card lock"],
  },
  "home-loans": {
    icon: Building2,
    eyebrow: "Home loans",
    title: "Plan housing costs with the rest of your financial life in view.",
    text: "Model payments, track loan balances, and keep mortgage obligations connected to cash flow and budget planning.",
    primary: "Explore home loans",
    highlights: ["Payment planning", "Loan balance tracking", "Document checklist", "Budget impact view"],
  },
  auto: {
    icon: Car,
    eyebrow: "Auto",
    title: "Understand vehicle financing before and after you buy.",
    text: "Estimate payments, track auto loan movement, and keep transportation costs visible in monthly plans.",
    primary: "Explore auto financing",
    highlights: ["Payment estimates", "Loan tracking", "Insurance reminders", "Budget category reporting"],
  },
  business: {
    icon: BriefcaseBusiness,
    eyebrow: "Business banking",
    title: "Run business banking with approvals, cards, and reports in one place.",
    text: "VaultWise business tools help teams manage operating accounts, permissions, vendor cards, transfers, and monthly finance reviews.",
    primary: "Open business account",
    highlights: ["Team roles", "Dual-control approvals", "Business card controls", "Operating reports"],
  },
  investing: {
    icon: LineChart,
    eyebrow: "Investing",
    title: "Keep investments connected to the goals they serve.",
    text: "See portfolio movement beside savings, debt, cash reserves, and long-term plans so decisions stay grounded.",
    primary: "Explore investing",
    highlights: ["Portfolio tracking", "Goal planning", "Retirement views", "Education planning"],
    disclosure: "Investment products are not FDIC insured, are not bank deposits, and may lose value.",
  },
}

const pricingPlans = [
  ["Everyday", "$0", "Core banking visibility for individuals.", ["Checking dashboard", "Savings goals", "Card activity", "Email support"]],
  ["Business", "$29", "More controls for teams and operators.", ["Unlimited accounts", "Team roles", "Card controls", "CSV exports"]],
  ["Enterprise", "Custom", "Advanced governance and implementation.", ["Approval workflows", "Dedicated support", "Custom integrations", "Audit-ready reporting"]],
]

const securityControls = [
  "Multi-factor authentication",
  "Trusted device tracking",
  "Step-up checks for sensitive actions",
  "Role-based access controls",
  "Card lock and channel controls",
  "Audit logs for account activity",
  "Encrypted sensitive fields",
  "Idempotency for financial operations",
]

function PublicShell({ children }) {
  return (
    <div className="shell public-shell chase-shell">
      <UtilityBar />
      <header className="chase-header">
        <div className="chase-nav">
          <a href="/" className="chase-brand" aria-label="VaultWise home">
            <span className="chase-mark"><Landmark size={19} /></span>
            <span>VaultWise</span>
          </a>
          <nav className="chase-menu" aria-label="Primary navigation">
            {productNav.map(([label, href]) => <a key={href} href={href}>{label}</a>)}
          </nav>
          <div className="chase-actions">
            <a href="/contact" className="chase-link-button">Schedule a meeting</a>
            <a href="/login" className="chase-signin">Sign in</a>
            <button className="chase-menu-button" type="button" aria-label="Open menu"><Menu size={20} /></button>
          </div>
        </div>
      </header>
      {children}
      <PublicFooter />
    </div>
  )
}

function UtilityBar() {
  return (
    <div className="chase-utility">
      <div className="chase-utility-inner">
        <div className="chase-utility-tabs">
          <a href="/" className="active">Personal</a>
          <a href="/business">Business</a>
          <a href="/product">Commercial</a>
        </div>
        <div className="chase-utility-links">
          <a href="/contact">Customer service</a>
          <a href="/contact">Find ATM or branch</a>
          <a href="/security">Security</a>
        </div>
      </div>
    </div>
  )
}

export function PublicHome() {
  return (
    <PublicShell>
      <main className="chase-main">

        {/* ── Hero ── */}
        <section className="chase-hero">
          <div className="chase-hero-copy">
            <p className="chase-eyebrow">Banking made clear</p>
            <h1>Bank, save, borrow, and invest with confidence.</h1>
            <p>
              Manage everyday money, cards, loans, business accounts, and long-term goals from one secure VaultWise workspace.
            </p>
            <div className="chase-hero-actions">
              <a href="/register" className="chase-primary">Open an account</a>
              <a href="/product" className="chase-secondary">Explore products</a>
            </div>
          </div>
          <HomeSignInPanel />
        </section>

        {/* ── Trust strip ── */}
        <TrustStrip />

        {/* ── Product grid ── */}
        <section className="chase-product-band" aria-label="Banking products">
          {homeProducts.map((item) => <ProductTile key={item.title} {...item} />)}
        </section>

        {/* ── Current offers ── */}
        <OffersSection />

        {/* ── Mobile banking split ── */}
        <section className="chase-split-section">
          <div>
            <p className="chase-eyebrow">Mobile banking</p>
            <h2>Take your bank with you.</h2>
            <p>
              View balances, manage cards, move funds, approve business transfers, and review reports from any device — 24 hours a day, 7 days a week.
            </p>
            <div className="chase-hero-actions" style={{ marginTop: "1.5rem" }}>
              <a href="/register" className="chase-primary">Get started</a>
              <a href="/security" style={{ fontSize: "0.82rem", fontWeight: 700, color: "#006DAE" }}>
                How we protect you →
              </a>
            </div>
          </div>
          <div className="chase-phone-card">
            <Smartphone size={30} />
            <strong>$12,480.22</strong>
            <span>Available balance</span>
            <div className="chase-mini-list">
              <p><CheckCircle2 size={15} /> Card controls active</p>
              <p><CheckCircle2 size={15} /> Payroll transfer approved</p>
              <p><CheckCircle2 size={15} /> Savings goal on track</p>
              <p><CheckCircle2 size={15} /> No unusual activity detected</p>
            </div>
          </div>
        </section>

        {/* ── Stats band ── */}
        <StatsBand />

        {/* ── Business callout ── */}
        <section className="chase-blue-callout">
          <div>
            <p className="chase-eyebrow">Business banking</p>
            <h2>Tools for owners, operators, and finance teams.</h2>
            <p>Control team access, issue cards, review budgets, and route larger transfers through dual-control approvals — all in one operating layer.</p>
          </div>
          <a href="/business" className="chase-primary light">Explore business banking</a>
        </section>

        {/* ── Testimonials ── */}
        <TestimonialsSection />

      </main>
    </PublicShell>
  )
}

function ProductTile({ icon: Icon, title, text, href, cta }) {
  return (
    <article className="chase-product-tile">
      <Icon size={30} />
      <h2>{title}</h2>
      <p>{text}</p>
      <a href={href}>{cta} <ChevronRight size={15} /></a>
    </article>
  )
}

export function BankingCategoryPage({ type }) {
  const page = categoryPages[type] || categoryPages.checking
  const Icon = page.icon
  return (
    <PublicShell>
      <main className="chase-main">
        <section className="chase-category-hero">
          <div>
            <p className="chase-eyebrow">{page.eyebrow}</p>
            <h1>{page.title}</h1>
            <p>{page.text}</p>
            <div className="chase-hero-actions">
              <a href="/register" className="chase-primary">{page.primary}</a>
              <a href="/contact" className="chase-secondary">Talk to a banker</a>
            </div>
          </div>
          <div className="chase-category-card">
            <Icon size={42} />
            <strong>{page.eyebrow}</strong>
            <span>VaultWise banking product</span>
          </div>
        </section>
        {page.disclosure ? <p className="chase-disclosure-strip">{page.disclosure}</p> : null}
        <section className="chase-feature-list">
          {page.highlights.map((item) => (
            <div key={item}>
              <CheckCircle2 size={18} />
              <span>{item}</span>
            </div>
          ))}
        </section>
        <ProductCrossSell />
      </main>
    </PublicShell>
  )
}

function ProductCrossSell() {
  return (
    <section className="chase-cross-sell">
      <h2>More ways to manage your money</h2>
      <div>
        {homeProducts.slice(0, 4).map((item) => <ProductTile key={item.title} {...item} />)}
      </div>
    </section>
  )
}

export function ProductPage() {
  return (
    <PublicShell>
      <main className="chase-main">
        <PageIntro
          eyebrow="Products"
          title="Choose the VaultWise product that fits your next financial step."
          text="From everyday checking to business banking and investing, VaultWise keeps each product connected to one secure online banking experience."
        />
        <section className="chase-product-band no-top">
          {homeProducts.map((item) => <ProductTile key={item.title} {...item} />)}
        </section>
      </main>
    </PublicShell>
  )
}

export function PricingPage() {
  return (
    <PublicShell>
      <main className="chase-main">
        <PageIntro
          eyebrow="Pricing"
          title="Simple plans for personal banking, business teams, and enterprise operations."
          text="Start with the everyday workspace, then add controls and support when your workflow needs more governance."
        />
        <section className="chase-pricing-grid">
          {pricingPlans.map(([name, price, text, points]) => (
            <article key={name} className="chase-plan">
              <h2>{name}</h2>
              <strong>{price}</strong>
              <p>{text}</p>
              <ul>
                {points.map((point) => <li key={point}><CheckCircle2 size={15} /> {point}</li>)}
              </ul>
              <a href={name === "Enterprise" ? "/contact" : "/register"} className="chase-primary">
                {name === "Enterprise" ? "Contact sales" : "Get started"}
              </a>
            </article>
          ))}
        </section>
      </main>
    </PublicShell>
  )
}

export function SecurityPage() {
  return (
    <PublicShell>
      <main className="chase-main">
        <PageIntro
          eyebrow="Security center"
          title="Tools that help protect your accounts and your team."
          text="VaultWise uses layered controls across identity, sessions, cards, approvals, and audit records."
        />
        <section className="chase-security-grid">
          {securityControls.map((item) => (
            <div key={item}>
              <LockKeyhole size={18} />
              <span>{item}</span>
            </div>
          ))}
        </section>
      </main>
    </PublicShell>
  )
}

export function ContactPage() {
  return (
    <PublicShell>
      <main className="chase-main">
        <PageIntro
          eyebrow="Contact"
          title="How can we help?"
          text="Talk with VaultWise support, schedule a business banking conversation, or get help choosing the right product."
        />
        <section className="chase-contact-layout">
          <div className="chase-contact-card">
            <Mail size={28} />
            <h2>Send us a message</h2>
            <ContactForm />
          </div>
          <div className="chase-contact-stack">
            <ContactMethod icon={Phone} title="Sales" text="1-800-555-1234" sub="Mon-Fri, 8am-6pm ET" />
            <ContactMethod icon={Mail} title="Support" text="support@vaultwise.com" sub="Response within 4 hours" />
            <ContactMethod icon={MapPin} title="Branch appointments" text="Schedule a meeting" sub="Virtual and in-person options" />
          </div>
        </section>
      </main>
    </PublicShell>
  )
}

// ─── New homepage sections ────────────────────────────────────────────────

function TrustStrip() {
  return (
    <div className="chase-trust-strip">
      <div className="chase-trust-strip-inner">
        <span className="chase-trust-item"><Shield size={14} /> FDIC Insured · Member FDIC</span>
        <span className="chase-trust-sep" />
        <span className="chase-trust-item"><Award size={14} /> SOC 2 Type II Certified</span>
        <span className="chase-trust-sep" />
        <span className="chase-trust-item"><ShieldCheck size={14} /> PCI DSS Level 1</span>
        <span className="chase-trust-sep" />
        <span className="chase-trust-item"><Globe size={14} /> Equal Housing Lender</span>
      </div>
    </div>
  )
}

const offers = [
  { eyebrow: "Checking", heading: "Up to $300 bonus", sub: "Open a new checking account and set up direct deposit.", cta: "Learn more", href: "/checking" },
  { eyebrow: "Savings", heading: "Earn competitive APY", sub: "High-yield savings designed to help your money grow faster.", cta: "Open savings", href: "/savings" },
  { eyebrow: "Credit cards", heading: "0% intro APR for 15 months", sub: "On purchases and balance transfers for new cardmembers.", cta: "Compare cards", href: "/credit-cards" },
]

function OffersSection() {
  return (
    <section className="chase-offers-section">
      <div className="chase-offers-header">
        <h2>Current offers</h2>
        <a href="/product" className="chase-offers-seeall">See all offers <ChevronRight size={14} /></a>
      </div>
      <div className="chase-offers-grid">
        {offers.map(({ eyebrow, heading, sub, cta, href }) => (
          <article key={heading} className="chase-offer-card">
            <p className="chase-eyebrow">{eyebrow}</p>
            <h3>{heading}</h3>
            <p>{sub}</p>
            <a href={href}>{cta} <ChevronRight size={13} /></a>
          </article>
        ))}
      </div>
    </section>
  )
}

const platformStats = [
  ["$2.4B+", "Transactions processed"],
  ["14,000+", "Enterprise accounts"],
  ["99.99%", "Uptime SLA"],
  ["4.8 ★", "App store rating"],
]

function StatsBand() {
  return (
    <div className="chase-stats-band">
      {platformStats.map(([value, label]) => (
        <div key={label} className="chase-stat-tile">
          <strong>{value}</strong>
          <span>{label}</span>
        </div>
      ))}
    </div>
  )
}

const testimonials = [
  { quote: "VaultWise replaced three separate tools for our treasury team. One platform, full audit trail, and the CFO approved on day one.", name: "Marcus Chen", title: "VP of Finance, Meridian Capital", stars: 5 },
  { quote: "The dual-control approval workflow stopped two unauthorized transfers in the first month. It paid for itself immediately.", name: "Sarah Whitmore", title: "Controller, NovaTech Industries", stars: 5 },
  { quote: "Card controls, step-up auth, and RBAC — all production-ready without a six-month implementation. Exceptional product.", name: "David Okafor", title: "CFO, Pacific Growth Ventures", stars: 5 },
]

function TestimonialsSection() {
  return (
    <section className="chase-testimonials-section">
      <div className="chase-testimonials-header">
        <h2>What our customers say</h2>
        <div className="chase-rating-badge"><Star size={16} fill="#F5A623" color="#F5A623" /> <strong>4.8</strong> / 5 avg rating</div>
      </div>
      <div className="chase-testimonials-grid">
        {testimonials.map(({ quote, name, title, stars }) => (
          <article key={name} className="chase-testimonial-card">
            <div className="chase-stars">
              {Array.from({ length: stars }).map((_, i) => <Star key={i} size={13} fill="#F5A623" color="#F5A623" />)}
            </div>
            <p>"{quote}"</p>
            <div className="chase-testimonial-author">
              <div className="chase-testimonial-avatar">{name[0]}</div>
              <div>
                <strong>{name}</strong>
                <span>{title}</span>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

function ContactMethod({ icon: Icon, title, text, sub }) {
  return (
    <article className="chase-contact-method">
      <Icon size={22} />
      <div>
        <h2>{title}</h2>
        <p>{text}</p>
        <span>{sub}</span>
      </div>
    </article>
  )
}

function PageIntro({ eyebrow, title, text }) {
  return (
    <section className="chase-page-intro">
      <p className="chase-eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p>{text}</p>
    </section>
  )
}

function PublicFooter() {
  return (
    <footer className="chase-footer">
      <div className="chase-footer-main">
        <div>
          <a href="/" className="chase-brand">
            <span className="chase-mark"><Landmark size={18} /></span>
            <span>VaultWise</span>
          </a>
          <p>Online banking, cards, lending, investing, and business controls in one secure workspace.</p>
          <div className="chase-footer-badges">
            <span className="chase-footer-badge"><Shield size={11} /> FDIC Insured</span>
            <span className="chase-footer-badge"><Award size={11} /> SOC 2 Type II</span>
          </div>
        </div>
        <FooterColumn title="Personal" links={[
          ["Checking", "/checking"],
          ["Savings & CDs", "/savings"],
          ["Credit Cards", "/credit-cards"],
          ["Home Loans", "/home-loans"],
          ["Auto", "/auto"],
        ]} />
        <FooterColumn title="Business" links={[
          ["Business Banking", "/business"],
          ["Business Cards", "/credit-cards"],
          ["Business Loans", "/product"],
          ["Approvals", "/business"],
          ["Pricing", "/pricing"],
        ]} />
        <FooterColumn title="Platform" links={[
          ["Investing", "/investing"],
          ["Security Center", "/security"],
          ["API & Integrations", "/product"],
          ["System Status", "/security"],
          ["Developer Docs", "/product"],
        ]} />
        <FooterColumn title="Help & Support" links={[
          ["Customer Service", "/contact"],
          ["Find ATM / Branch", "/contact"],
          ["Fraud & Disputes", "/contact"],
          ["Contact Us", "/contact"],
          ["Sign In", "/login"],
        ]} />
      </div>
      <div className="chase-footer-legal-links">
        <a href="/privacy">Privacy Policy</a>
        <a href="/terms">Terms of Use</a>
        <a href="/security-policy">Security Policy</a>
        <a href="/cookie-policy">Cookie Settings</a>
        <a href="/contact">Accessibility</a>
        <a href="/contact">Site Map</a>
      </div>
      <div className="chase-legal">
        <p>
          © 2025 VaultWise Financial Technologies, Inc. All rights reserved. VaultWise is a financial technology company, not a bank. Banking services are provided through partner FDIC-insured institutions. NMLS #123456. Investment products are not FDIC insured, are not bank deposits or obligations, and may lose value. Equal Housing Opportunity. Member FDIC.
        </p>
        <span>Member FDIC · Equal Housing Lender</span>
      </div>
    </footer>
  )
}

function FooterColumn({ title, links }) {
  return (
    <div className="chase-footer-col">
      <h2>{title}</h2>
      {links.map(([label, href]) => <a key={label} href={href}>{label}</a>)}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────
// Policy page shell
// ─────────────────────────────────────────────────────────────────────────

function PolicyShell({ title, eyebrow, updated, children }) {
  return (
    <PublicShell>
      <main className="chase-main">
        <div className="policy-hero">
          <p className="chase-eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p className="policy-updated">Last updated: {updated}</p>
        </div>
        <div className="policy-body">
          <nav className="policy-toc" aria-label="Table of contents">
            <p className="policy-toc-heading">On this page</p>
            {children.map?.((section) => section?.props?.id
              ? <a key={section.props.id} href={`#${section.props.id}`}>{section.props["data-toc"]}</a>
              : null
            )}
          </nav>
          <article className="policy-content">{children}</article>
        </div>
      </main>
    </PublicShell>
  )
}

function PolicySection({ id, "data-toc": toc, title, children }) {
  return (
    <section id={id} data-toc={toc} className="policy-section">
      <h2>{title}</h2>
      {children}
    </section>
  )
}

// ─────────────────────────────────────────────────────────────────────────
// Privacy Policy
// ─────────────────────────────────────────────────────────────────────────

export function PrivacyPolicyPage() {
  return (
    <PolicyShell
      eyebrow="Legal"
      title="Privacy Policy"
      updated="April 30, 2025"
    >
      <PolicySection id="overview" data-toc="Overview" title="Overview">
        <p>VaultWise Financial Technologies, Inc. ("VaultWise," "we," "our," or "us") is committed to protecting your personal information. This Privacy Policy describes how we collect, use, share, and safeguard data when you access our website, mobile applications, and financial services platform (collectively, the "Services"). By using our Services, you agree to the practices described in this policy.</p>
        <p>If you are a resident of California or another jurisdiction with specific privacy rights, please refer to the applicable regional disclosures at the end of this policy.</p>
      </PolicySection>

      <PolicySection id="information-we-collect" data-toc="Information We Collect" title="Information We Collect">
        <p>We collect information in the following categories:</p>
        <h3>Information you provide directly</h3>
        <ul>
          <li><strong>Account registration:</strong> Full name, email address, password, and phone number.</li>
          <li><strong>Identity verification:</strong> Government-issued ID, date of birth, Social Security Number (last four digits), and address.</li>
          <li><strong>Financial information:</strong> Bank account numbers, routing numbers, card numbers, transaction records, and balance data you import or generate within the platform.</li>
          <li><strong>Communications:</strong> Support requests, feedback, survey responses, and correspondence with our team.</li>
        </ul>
        <h3>Information collected automatically</h3>
        <ul>
          <li><strong>Device and usage data:</strong> IP address, browser type, operating system, pages visited, click paths, session duration, and referring URLs.</li>
          <li><strong>Cookies and tracking technologies:</strong> Session cookies, persistent cookies, pixel tags, and local storage identifiers. See our <a href="/cookie-policy">Cookie Policy</a> for full details.</li>
          <li><strong>Location data:</strong> Approximate geolocation derived from IP address for fraud detection and regional compliance.</li>
        </ul>
        <h3>Information from third parties</h3>
        <ul>
          <li>Identity verification providers, credit bureaus, fraud detection services, and financial data aggregators (e.g., bank feed connections) may supply additional data to help us verify your identity and detect fraud.</li>
        </ul>
      </PolicySection>

      <PolicySection id="how-we-use" data-toc="How We Use Your Information" title="How We Use Your Information">
        <p>We use collected information to:</p>
        <ul>
          <li>Provide, operate, and improve our banking and financial management Services.</li>
          <li>Authenticate your identity and manage your session securely.</li>
          <li>Process transactions, fund transfers, and card operations.</li>
          <li>Detect, prevent, and investigate fraud, unauthorized access, and financial crime.</li>
          <li>Comply with applicable laws including the Bank Secrecy Act, anti-money laundering regulations, and KYC requirements.</li>
          <li>Send transactional notifications, security alerts, and account updates.</li>
          <li>Send marketing communications, where permitted and with your consent where required.</li>
          <li>Conduct analytics and research to improve our products and user experience.</li>
          <li>Respond to legal process, regulatory inquiries, and enforce our agreements.</li>
        </ul>
        <p>We do not sell your personal financial data to third parties for their marketing purposes.</p>
      </PolicySection>

      <PolicySection id="sharing" data-toc="Sharing Your Information" title="Sharing Your Information">
        <p>We may share your information with:</p>
        <ul>
          <li><strong>Partner banking institutions:</strong> FDIC-insured banks that hold deposit accounts on your behalf.</li>
          <li><strong>Payment networks:</strong> Visa, Mastercard, and ACH networks to process card and transfer transactions.</li>
          <li><strong>Service providers:</strong> Cloud hosting, identity verification, fraud screening, analytics, customer support, and email delivery vendors who process data on our behalf under confidentiality obligations.</li>
          <li><strong>Regulatory authorities:</strong> Federal and state regulators, law enforcement, and courts when required by law or to protect rights and safety.</li>
          <li><strong>Business transfers:</strong> In connection with a merger, acquisition, or sale of assets, subject to confidentiality commitments.</li>
          <li><strong>With your consent:</strong> Any other sharing we describe at the point of collection or for which you provide explicit authorization.</li>
        </ul>
      </PolicySection>

      <PolicySection id="data-security" data-toc="Data Security" title="Data Security">
        <p>We implement technical and organizational measures designed to protect your information against unauthorized access, loss, or misuse, including:</p>
        <ul>
          <li>TLS encryption for all data in transit between your device and our servers.</li>
          <li>AES-256 encryption for sensitive data at rest, including financial records and credentials.</li>
          <li>Field-level encryption for MFA secrets and card token data.</li>
          <li>JWT access and refresh token rotation with short expiry windows.</li>
          <li>Multi-factor authentication (TOTP) for account access and step-up verification for sensitive operations.</li>
          <li>Role-based access controls limiting employee and system access to data on a need-to-know basis.</li>
          <li>Continuous monitoring, intrusion detection, and security incident response procedures.</li>
          <li>Third-party penetration testing and SOC 2 Type II audits.</li>
        </ul>
        <p>No system is perfectly secure. If you believe your account has been compromised, contact us immediately at <a href="mailto:security@vaultwise.com">security@vaultwise.com</a>.</p>
      </PolicySection>

      <PolicySection id="retention" data-toc="Data Retention" title="Data Retention">
        <p>We retain personal data for as long as necessary to provide our Services and comply with legal obligations. Specific retention periods include:</p>
        <ul>
          <li><strong>Account data:</strong> Retained for the lifetime of your account and for up to 7 years after closure, as required by financial regulations.</li>
          <li><strong>Transaction records:</strong> Minimum 5 years pursuant to BSA/AML requirements.</li>
          <li><strong>Audit logs:</strong> 3 years for access and security event logs.</li>
          <li><strong>Marketing data:</strong> Until you withdraw consent or request deletion, subject to applicable law.</li>
        </ul>
      </PolicySection>

      <PolicySection id="your-rights" data-toc="Your Rights" title="Your Rights">
        <p>Depending on your jurisdiction, you may have the right to:</p>
        <ul>
          <li><strong>Access:</strong> Request a copy of the personal data we hold about you.</li>
          <li><strong>Correction:</strong> Request correction of inaccurate or incomplete data.</li>
          <li><strong>Deletion:</strong> Request deletion of your data, subject to legal retention obligations.</li>
          <li><strong>Portability:</strong> Receive your data in a machine-readable format.</li>
          <li><strong>Objection / Restriction:</strong> Object to or request restriction of certain processing activities.</li>
          <li><strong>Withdrawal of consent:</strong> Withdraw consent for marketing communications at any time.</li>
        </ul>
        <p>To exercise your rights, contact us at <a href="mailto:privacy@vaultwise.com">privacy@vaultwise.com</a> or through your account settings. We will respond within 30 days (or as required by applicable law).</p>
      </PolicySection>

      <PolicySection id="cookies" data-toc="Cookies" title="Cookies and Tracking">
        <p>We use cookies and similar technologies to operate our Services and understand how they are used. You can manage cookie preferences through your browser settings or our <a href="/cookie-policy">Cookie Policy</a> page. Note that disabling certain cookies may affect the functionality of the Services.</p>
      </PolicySection>

      <PolicySection id="children" data-toc="Children's Privacy" title="Children's Privacy">
        <p>Our Services are not directed to individuals under the age of 18. We do not knowingly collect personal information from children. If we become aware that we have inadvertently collected data from a minor, we will delete it promptly. Contact us at <a href="mailto:privacy@vaultwise.com">privacy@vaultwise.com</a> if you believe a child's data has been submitted.</p>
      </PolicySection>

      <PolicySection id="changes" data-toc="Changes to This Policy" title="Changes to This Policy">
        <p>We may update this Privacy Policy from time to time. Material changes will be communicated by email to registered users or through a prominent notice on our website at least 30 days before they take effect. The "Last updated" date at the top of this page reflects the most recent revision. Continued use of the Services after the effective date constitutes acceptance of the updated policy.</p>
      </PolicySection>

      <PolicySection id="contact" data-toc="Contact Us" title="Contact Us">
        <p>For privacy-related questions, requests, or concerns, please reach out:</p>
        <ul>
          <li><strong>Email:</strong> <a href="mailto:privacy@vaultwise.com">privacy@vaultwise.com</a></li>
          <li><strong>Mail:</strong> VaultWise Financial Technologies, Inc., Attn: Privacy Officer, 100 Financial District Plaza, New York, NY 10004</li>
          <li><strong>Phone:</strong> 1-800-555-1234 (Mon–Fri, 8am–6pm ET)</li>
        </ul>
        <p>If you are located in the European Economic Area, you may also lodge a complaint with your local data protection authority.</p>
      </PolicySection>
    </PolicyShell>
  )
}

// ─────────────────────────────────────────────────────────────────────────
// Terms of Use
// ─────────────────────────────────────────────────────────────────────────

export function TermsOfUsePage() {
  return (
    <PolicyShell
      eyebrow="Legal"
      title="Terms of Use"
      updated="April 30, 2025"
    >
      <PolicySection id="acceptance" data-toc="Acceptance of Terms" title="Acceptance of Terms">
        <p>Welcome to VaultWise. These Terms of Use ("Terms") govern your access to and use of the VaultWise website, mobile applications, APIs, and financial management platform (collectively, the "Services") operated by VaultWise Financial Technologies, Inc. ("VaultWise," "we," "our," or "us"). By creating an account or using the Services, you agree to be bound by these Terms and our <a href="/privacy">Privacy Policy</a>. If you do not agree, do not use the Services.</p>
        <p>These Terms constitute a legally binding agreement. Please read them carefully.</p>
      </PolicySection>

      <PolicySection id="eligibility" data-toc="Eligibility" title="Eligibility">
        <p>To use VaultWise Services, you must:</p>
        <ul>
          <li>Be at least 18 years of age.</li>
          <li>Be a legal resident or citizen of a jurisdiction where our Services are available.</li>
          <li>Have the legal capacity to enter into a binding agreement.</li>
          <li>Not be barred from using financial services under applicable law.</li>
          <li>Provide accurate, current, and complete registration information.</li>
        </ul>
        <p>By using the Services, you represent and warrant that you meet all eligibility requirements. We reserve the right to suspend or terminate accounts that do not meet these requirements.</p>
      </PolicySection>

      <PolicySection id="account" data-toc="Your Account" title="Your Account">
        <p>You are responsible for maintaining the confidentiality of your login credentials and for all activity that occurs under your account. You agree to:</p>
        <ul>
          <li>Create a strong, unique password and enable multi-factor authentication.</li>
          <li>Notify us immediately at <a href="mailto:security@vaultwise.com">security@vaultwise.com</a> if you suspect unauthorized access.</li>
          <li>Not share your credentials with any third party.</li>
          <li>Keep your contact information (especially email) current and accurate.</li>
          <li>Not use automated tools to access the Services unless through our documented API with proper authorization.</li>
        </ul>
        <p>We are not liable for losses resulting from unauthorized account access caused by your failure to maintain credential security.</p>
      </PolicySection>

      <PolicySection id="permitted-use" data-toc="Permitted Use" title="Permitted Use">
        <p>Subject to these Terms, VaultWise grants you a limited, non-exclusive, non-transferable, revocable license to use the Services for your personal and business financial management purposes. You may not:</p>
        <ul>
          <li>Use the Services for any unlawful purpose, including money laundering, fraud, or financing prohibited activities.</li>
          <li>Attempt to gain unauthorized access to any part of the Services or other users' accounts.</li>
          <li>Reverse-engineer, decompile, or disassemble any portion of the Services.</li>
          <li>Transmit malware, spam, or any disruptive or harmful code.</li>
          <li>Use the Services to process transactions on behalf of third parties without authorization.</li>
          <li>Reproduce, resell, or redistribute the Services or any portion thereof without written consent.</li>
          <li>Interfere with or disrupt the integrity or performance of the Services or servers.</li>
        </ul>
      </PolicySection>

      <PolicySection id="financial-services" data-toc="Financial Services" title="Financial Services and Accounts">
        <p>VaultWise is a financial technology company, not a bank. Deposit accounts, payment processing, and other banking services are provided through our FDIC-insured partner financial institutions. The following terms apply:</p>
        <ul>
          <li><strong>Deposit accounts</strong> are held at partner FDIC-insured banks and are subject to their deposit account agreements in addition to these Terms.</li>
          <li><strong>Investment products</strong> are not FDIC insured, are not deposits or obligations of VaultWise or any bank, and are subject to investment risk including possible loss of principal.</li>
          <li><strong>Card services</strong> are issued subject to network rules (Visa/Mastercard) and our Card Agreement.</li>
          <li><strong>Transfers and payments</strong> are subject to applicable ACH, wire, and network rules, and may be subject to review and delay for compliance purposes.</li>
          <li><strong>Business banking</strong> services, including dual-control approvals and team access, are subject to additional business account terms provided at enrollment.</li>
        </ul>
        <p>Approval for any financial product is not guaranteed and is subject to eligibility review.</p>
      </PolicySection>

      <PolicySection id="fees" data-toc="Fees and Payments" title="Fees and Payments">
        <p>Certain Services require payment of fees as described on our <a href="/pricing">Pricing</a> page. By subscribing to a paid plan, you authorize us to charge the applicable fees to your payment method on a recurring basis. All fees are in U.S. dollars unless stated otherwise.</p>
        <ul>
          <li>Subscription fees are billed monthly or annually in advance.</li>
          <li>Fees are non-refundable except where required by law or as described in our cancellation policy.</li>
          <li>We reserve the right to change fees with at least 30 days' notice to current subscribers.</li>
          <li>Failure to pay may result in service suspension or termination.</li>
        </ul>
      </PolicySection>

      <PolicySection id="intellectual-property" data-toc="Intellectual Property" title="Intellectual Property">
        <p>All content, software, trademarks, logos, and materials available through the Services are owned by or licensed to VaultWise and are protected by intellectual property laws. You may not copy, modify, distribute, sell, or lease any part of our Services or included software. You may not reverse-engineer or attempt to extract the source code of our software.</p>
        <p>Any feedback, suggestions, or ideas you submit regarding the Services may be used by VaultWise without obligation to you.</p>
      </PolicySection>

      <PolicySection id="disclaimers" data-toc="Disclaimers" title="Disclaimers">
        <p>THE SERVICES ARE PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. VAULTWISE DOES NOT WARRANT THAT THE SERVICES WILL BE UNINTERRUPTED, ERROR-FREE, OR FREE OF HARMFUL COMPONENTS.</p>
        <p>Financial data displayed within the Services is provided for informational purposes only and may not reflect real-time balances. Do not rely solely on VaultWise data for critical financial decisions without independent verification.</p>
      </PolicySection>

      <PolicySection id="limitation" data-toc="Limitation of Liability" title="Limitation of Liability">
        <p>TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, VAULTWISE AND ITS OFFICERS, DIRECTORS, EMPLOYEES, AND PARTNERS SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING FROM YOUR USE OF OR INABILITY TO USE THE SERVICES. OUR TOTAL LIABILITY TO YOU FOR ANY CLAIM ARISING FROM THESE TERMS SHALL NOT EXCEED THE GREATER OF (A) THE FEES YOU PAID TO VAULTWISE IN THE 12 MONTHS PRECEDING THE CLAIM, OR (B) $100.</p>
        <p>Some jurisdictions do not allow the exclusion of certain warranties or limitations on liability, so the above limitations may not apply to you.</p>
      </PolicySection>

      <PolicySection id="indemnification" data-toc="Indemnification" title="Indemnification">
        <p>You agree to indemnify, defend, and hold harmless VaultWise and its affiliates, officers, agents, and employees from any claims, damages, losses, liabilities, costs, and expenses (including reasonable attorneys' fees) arising from: (a) your use of the Services; (b) your violation of these Terms; (c) your violation of any third-party rights; or (d) any content you submit through the Services.</p>
      </PolicySection>

      <PolicySection id="termination" data-toc="Termination" title="Termination">
        <p>We reserve the right to suspend or terminate your access to the Services at any time, with or without notice, for any reason, including violation of these Terms, suspected fraud, or regulatory requirement. You may close your account at any time through account settings or by contacting us. Upon termination, your right to use the Services ceases immediately, though certain provisions of these Terms survive termination.</p>
      </PolicySection>

      <PolicySection id="governing-law" data-toc="Governing Law" title="Governing Law and Disputes">
        <p>These Terms are governed by the laws of the State of New York, without regard to its conflict of laws provisions. Any dispute arising from these Terms or the Services shall be resolved through binding arbitration administered by the American Arbitration Association under its Consumer Arbitration Rules, except that either party may seek injunctive relief in a court of competent jurisdiction. You waive any right to participate in a class action lawsuit or class-wide arbitration.</p>
      </PolicySection>

      <PolicySection id="changes" data-toc="Changes to Terms" title="Changes to Terms">
        <p>We may update these Terms from time to time. We will notify you of material changes by email or prominent notice at least 30 days before the effective date. Your continued use of the Services after the effective date of any changes constitutes acceptance of the updated Terms.</p>
      </PolicySection>

      <PolicySection id="contact" data-toc="Contact" title="Contact">
        <p>If you have questions about these Terms, please contact us:</p>
        <ul>
          <li><strong>Email:</strong> <a href="mailto:legal@vaultwise.com">legal@vaultwise.com</a></li>
          <li><strong>Mail:</strong> VaultWise Financial Technologies, Inc., Attn: Legal Department, 100 Financial District Plaza, New York, NY 10004</li>
        </ul>
      </PolicySection>
    </PolicyShell>
  )
}

// ─────────────────────────────────────────────────────────────────────────
// Security Policy
// ─────────────────────────────────────────────────────────────────────────

export function SecurityPolicyPage() {
  return (
    <PolicyShell
      eyebrow="Legal"
      title="Security Policy"
      updated="April 30, 2025"
    >
      <PolicySection id="commitment" data-toc="Our Commitment" title="Our Security Commitment">
        <p>VaultWise is committed to maintaining the security of your accounts and financial data. This Security Policy describes the controls, practices, and certifications that underpin our security posture. We continuously evaluate and improve our security program as threats evolve.</p>
      </PolicySection>

      <PolicySection id="infrastructure" data-toc="Infrastructure Security" title="Infrastructure Security">
        <ul>
          <li><strong>Encryption in transit:</strong> All communications between your browser or app and VaultWise are encrypted using TLS 1.2 or higher.</li>
          <li><strong>Encryption at rest:</strong> Data stored in our databases is encrypted using AES-256.</li>
          <li><strong>Field-level encryption:</strong> Highly sensitive fields — including MFA secrets and card token data — receive an additional layer of field-level encryption.</li>
          <li><strong>Cloud infrastructure:</strong> Hosted on SOC 2-certified cloud infrastructure with isolated network environments, private subnets, and automated backups.</li>
          <li><strong>Idempotency enforcement:</strong> All financial operations include idempotency keys to prevent duplicate processing under retry conditions.</li>
        </ul>
      </PolicySection>

      <PolicySection id="access" data-toc="Access Controls" title="Access Controls">
        <ul>
          <li><strong>Role-based access control (RBAC):</strong> User permissions are scoped to their role — customer, operator, approver, admin, compliance, risk, and support roles each have distinct access boundaries.</li>
          <li><strong>Multi-factor authentication:</strong> TOTP-based MFA is available to all users and required for sensitive operations.</li>
          <li><strong>Step-up authentication:</strong> High-risk actions (card issuance, large transfers, admin changes) require a fresh authentication challenge regardless of session state.</li>
          <li><strong>Trusted device tracking:</strong> Devices can be designated as trusted to reduce friction while maintaining security context.</li>
          <li><strong>Session management:</strong> JWT access tokens expire within 15 minutes. Refresh tokens are rotated on use and expire within 7 days.</li>
          <li><strong>Admin isolation:</strong> Administrative routes and dashboards are separated from customer-facing surfaces and require elevated roles.</li>
        </ul>
      </PolicySection>

      <PolicySection id="fraud" data-toc="Fraud Detection" title="Fraud and Anomaly Detection">
        <ul>
          <li>Real-time transaction risk screening flags unusual activity before it posts to the ledger.</li>
          <li>Compliance case management automatically holds and escalates flagged transactions for review.</li>
          <li>Velocity and pattern checks identify anomalous login attempts, transfer patterns, and card usage.</li>
          <li>Automated alerts notify you of significant account events including logins from new devices, large transfers, and card activity.</li>
        </ul>
      </PolicySection>

      <PolicySection id="certifications" data-toc="Certifications" title="Certifications and Audits">
        <ul>
          <li><strong>SOC 2 Type II:</strong> Annual audit of our security, availability, and confidentiality controls by an independent CPA firm.</li>
          <li><strong>PCI DSS Level 1:</strong> The highest level of Payment Card Industry compliance for organizations processing card transactions.</li>
          <li><strong>ISO 27001:</strong> Internationally recognized information security management standard.</li>
          <li><strong>Penetration testing:</strong> Annual third-party penetration tests with remediation tracking.</li>
          <li><strong>FDIC insured deposits:</strong> Deposit accounts held at partner institutions are insured by the FDIC up to $250,000 per depositor, per institution.</li>
        </ul>
      </PolicySection>

      <PolicySection id="reporting" data-toc="Vulnerability Reporting" title="Vulnerability Reporting">
        <p>We welcome responsible disclosure of security vulnerabilities. If you discover a potential security issue, please report it to us before making it public:</p>
        <ul>
          <li><strong>Email:</strong> <a href="mailto:security@vaultwise.com">security@vaultwise.com</a></li>
          <li><strong>PGP key:</strong> Available at <a href="#">/security/pgp-key.txt</a></li>
        </ul>
        <p>We commit to acknowledging reports within 3 business days and providing a resolution timeline within 10 business days. We do not pursue legal action against researchers who follow responsible disclosure practices.</p>
      </PolicySection>

      <PolicySection id="incident" data-toc="Incident Response" title="Incident Response">
        <p>In the event of a security incident affecting your data, VaultWise will:</p>
        <ul>
          <li>Notify affected users within 72 hours of becoming aware of the breach, as required by applicable law.</li>
          <li>Provide details of what data was affected, steps we are taking, and actions you should take.</li>
          <li>Work with regulatory authorities as required.</li>
          <li>Conduct a post-incident review and implement preventive measures.</li>
        </ul>
      </PolicySection>
    </PolicyShell>
  )
}

// ─────────────────────────────────────────────────────────────────────────
// Cookie Policy
// ─────────────────────────────────────────────────────────────────────────

export function CookiePolicyPage() {
  return (
    <PolicyShell
      eyebrow="Legal"
      title="Cookie Policy"
      updated="April 30, 2025"
    >
      <PolicySection id="what-are-cookies" data-toc="What Are Cookies" title="What Are Cookies">
        <p>Cookies are small text files placed on your device by websites you visit. They are widely used to make websites work efficiently, remember your preferences, and provide information to site owners. Similar technologies — including web beacons, pixel tags, and local storage — serve analogous purposes and are collectively referred to as "cookies" in this policy.</p>
      </PolicySection>

      <PolicySection id="how-we-use" data-toc="How We Use Cookies" title="How VaultWise Uses Cookies">
        <p>We use cookies in the following categories:</p>
        <h3>Strictly necessary cookies</h3>
        <p>These cookies are essential to the operation of our Services and cannot be disabled. They include session authentication tokens, CSRF protection, and load-balancing cookies. Without these, the Services cannot function.</p>
        <h3>Functional cookies</h3>
        <p>These cookies remember your preferences and settings — such as your language, remembered username, and display options — to provide a more personalized experience. You can disable these, but doing so may affect functionality.</p>
        <h3>Analytics cookies</h3>
        <p>We use analytics tools to understand how users interact with our Services — which pages are visited most, where users encounter errors, and how navigation flows. This helps us improve the product. Analytics cookies collect anonymized, aggregated data and do not identify you personally.</p>
        <h3>Marketing and advertising cookies</h3>
        <p>With your consent, we may use cookies to deliver relevant advertisements and measure their effectiveness. You can withdraw consent at any time through the cookie preference center (accessible via the footer link).</p>
      </PolicySection>

      <PolicySection id="third-party" data-toc="Third-Party Cookies" title="Third-Party Cookies">
        <p>Some cookies on our site are set by third-party providers, including:</p>
        <ul>
          <li><strong>Analytics providers</strong> (e.g., aggregated usage statistics)</li>
          <li><strong>Fraud detection services</strong> (session integrity and bot detection)</li>
          <li><strong>Customer support tools</strong> (session context for support interactions)</li>
        </ul>
        <p>Third-party cookies are subject to those providers' own privacy and cookie policies. We do not control third-party cookies.</p>
      </PolicySection>

      <PolicySection id="managing" data-toc="Managing Cookies" title="Managing Your Cookie Preferences">
        <p>You can manage cookies in several ways:</p>
        <ul>
          <li><strong>Browser settings:</strong> Most browsers allow you to block or delete cookies through their settings menu. Note that blocking strictly necessary cookies will prevent you from signing in.</li>
          <li><strong>Cookie preference center:</strong> Use the "Cookie Settings" link in our footer to manage optional cookie categories at any time.</li>
          <li><strong>Opt-out tools:</strong> Industry opt-out tools such as the Digital Advertising Alliance's opt-out tool at <a href="https://optout.aboutads.info" target="_blank" rel="noopener noreferrer">optout.aboutads.info</a>.</li>
        </ul>
        <p>Changes to your preferences take effect immediately for new cookies. Previously stored cookies may remain until they expire or are cleared manually.</p>
      </PolicySection>

      <PolicySection id="retention" data-toc="Cookie Retention" title="Cookie Retention Periods">
        <ul>
          <li><strong>Session cookies:</strong> Deleted when you close your browser.</li>
          <li><strong>Authentication cookies:</strong> Expire after 7 days (or 24 hours for standard sessions without "remember me").</li>
          <li><strong>Preference cookies:</strong> Retained for up to 1 year.</li>
          <li><strong>Analytics cookies:</strong> Retained for up to 13 months.</li>
          <li><strong>Marketing cookies:</strong> Retained for up to 90 days.</li>
        </ul>
      </PolicySection>

      <PolicySection id="contact" data-toc="Contact" title="Contact">
        <p>For questions about our use of cookies, contact us at <a href="mailto:privacy@vaultwise.com">privacy@vaultwise.com</a>.</p>
      </PolicySection>
    </PolicyShell>
  )
}
