import {
  ArrowRight,
  BarChart3,
  BellRing,
  Building2,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  ClipboardCheck,
  Clock3,
  CreditCard,
  DatabaseZap,
  FileCheck2,
  FileText,
  Gauge,
  KeyRound,
  Landmark,
  Layers3,
  LineChart,
  LockKeyhole,
  Mail,
  Network,
  PieChart,
  ReceiptText,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  UsersRound,
  WalletCards
} from "lucide-react"

const productLinks = [
  ["Product", "/product"],
  ["Pricing", "/pricing"],
  ["Security", "/security"],
  ["Contact", "/contact"]
]

const proofPoints = [
  ["Entity view", "Multi-account"],
  ["Reporting", "Board-ready"],
  ["Controls", "Role-aware"]
]

const platformFeatures = [
  {
    icon: WalletCards,
    title: "Account command center",
    text: "Cash, bank, card, investment, and loan positions with ownership context, balance movement, and status."
  },
  {
    icon: PieChart,
    title: "Budget governance",
    text: "Monthly category controls, variance review, utilization signals, and overspend intervention workflows."
  },
  {
    icon: FileText,
    title: "Finance reporting",
    text: "Executive summaries, close packets, category breakdowns, cash flow reads, and export-ready data."
  },
  {
    icon: ShieldCheck,
    title: "Operational controls",
    text: "JWT sessions, admin surfaces, role-aware routing, service boundaries, and governance extension points."
  },
  {
    icon: CreditCard,
    title: "Enterprise card issuing",
    text: "Issue debit, credit, savings-linked, and virtual cards with on/off controls, limits, channels, and authorization rules."
  }
]

const productCapabilities = [
  {
    icon: Gauge,
    title: "Liquidity command",
    text: "Cash coverage, income, expense, debt, and net worth signals for leadership reviews.",
    metric: "2.2 mo coverage"
  },
  {
    icon: WalletCards,
    title: "Ledger operations",
    text: "Track bank, card, cash, investment, and loan accounts through consistent finance records.",
    metric: "5 account classes"
  },
  {
    icon: Building2,
    title: "Business oversight",
    text: "Admin metrics, user governance, reports, and audit-ready extension points for controlled growth.",
    metric: "role gated"
  },
  {
    icon: PieChart,
    title: "Budget intelligence",
    text: "Budget progress, variance, category mix, recurring costs, and top outflows surfaced for action.",
    metric: "variance aware"
  },
  {
    icon: BellRing,
    title: "Risk queue",
    text: "Flag overdraft risk, subscription creep, high card exposure, and unusual operating swings.",
    metric: "priority signals"
  },
  {
    icon: DatabaseZap,
    title: "API-shaped data",
    text: "Built around clean records that can grow into imports, approvals, reconciliation, and integrations.",
    metric: "FastAPI core"
  },
  {
    icon: CreditCard,
    title: "Card control room",
    text: "Tokenized card records, step-up issuing, channel controls, category blocks, and turn-off/turn-on workflows.",
    metric: "4 card types"
  }
]

const workflowSteps = [
  ["Ingest", "Create accounts and seed balances for cash, credit, investment, loan, and operating sources."],
  ["Normalize", "Classify transactions with category, status, date, counterparty, and account context."],
  ["Issue", "Create debit, credit, savings-linked, and virtual cards with limits, channels, and step-up authentication."],
  ["Control", "Compare budgets, exposure, card activity, recurring costs, and coverage against operating thresholds."],
  ["Report", "Publish close-ready summaries for finance reviews, planning meetings, and leadership handoff."]
]

const securityControls = [
  "Environment-managed secrets",
  "Password hashing service",
  "JWT access and refresh tokens",
  "Step-up authentication for card issuing",
  "Hashed internal card tokens",
  "Card on/off and channel controls",
  "Role-aware public and private routing",
  "Admin-only governance routes",
  "FastAPI service boundaries",
  "PostgreSQL production target",
  "Audit-log persistence path"
]

const pricingPlans = [
  {
    name: "Starter",
    price: "$0",
    text: "For founders and operators who need clean personal finance visibility.",
    points: ["Accounts and balances", "Transaction tracking", "Core dashboard", "Starter reports"]
  },
  {
    name: "Business",
    price: "$29",
    text: "For teams that need monthly controls, reporting cadence, and admin visibility.",
    points: ["Budget controls", "Card controls", "CSV exports", "Team-ready permissions"],
    highlighted: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    text: "For organizations with integrations, governance reviews, and compliance workflows.",
    points: ["Custom integrations", "Governance workflows", "Compliance mapping", "Priority support"]
  }
]

const contactTopics = [
  ["Ledger migration", "Move account, card, loan, and historical transaction records into one workspace."],
  ["Operating reports", "Shape close-ready summaries for cash flow, budgets, category spend, and debt."],
  ["Access controls", "Plan admin roles, team permissions, service boundaries, and review workflows."]
]

const comparisonRows = [
  ["Account records", "Included", "Included", "Included"],
  ["Budget controls", "Basic", "Advanced", "Custom policy"],
  ["Card issuing", "View only", "Debit + virtual", "Debit, credit, savings + custom"],
  ["Card controls", "Basic lock", "On/off + limits", "Channels, categories + policy"],
  ["Reports and exports", "Monthly", "Monthly + CSV", "Custom packets"],
  ["Admin governance", "Single owner", "Team roles", "Advanced review"],
  ["Implementation", "Self serve", "Guided", "Dedicated"]
]

function PublicShell({ children }) {
  return (
    <div className="shell public-shell enterprise-shell">
      <header className="public-header enterprise-header">
        <div className="public-nav enterprise-nav">
          <a href="/" className="brand-lockup enterprise-brand" aria-label="BankOS home">
            <span className="brand-mark enterprise-brand-mark"><Landmark size={17} /></span>
            <span>BankOS</span>
          </a>
          <nav className="public-menu enterprise-menu" aria-label="Primary navigation">
            {productLinks.map(([label, path]) => (
              <a key={path} href={path} className="public-menu-link">{label}</a>
            ))}
          </nav>
          <div className="public-actions">
            <a href="/login" className="btn btn-secondary enterprise-btn-secondary">Login</a>
            <a href="/register" className="btn btn-primary enterprise-btn-primary">Start</a>
          </div>
        </div>
      </header>
      {children}
      <PublicFooter />
    </div>
  )
}

export function PublicHome() {
  return (
    <PublicShell>
      <main>
        <section className="hero-section enterprise-hero">
          <div className="hero-copy enterprise-hero-copy">
            <p className="eyebrow enterprise-eyebrow">Finance operating system</p>
            <h1 className="hero-title enterprise-title">A controlled banking workspace for finance teams.</h1>
            <p className="hero-subtitle enterprise-subtitle">
              BankOS turns accounts, budgets, transactions, liquidity, and admin governance into a board-ready operating layer for modern finance teams.
            </p>
            <div className="hero-actions">
              <a href="/register" className="btn btn-primary enterprise-btn-primary">Create workspace <ArrowRight size={15} /></a>
              <a href="/product" className="btn btn-secondary enterprise-btn-secondary">View platform</a>
            </div>
            <div className="proof-grid enterprise-proof-grid">
              {proofPoints.map(([label, value]) => <Proof key={label} label={label} value={value} />)}
            </div>
          </div>
          <EnterpriseConsole />
        </section>

        <LogoStrip />

        <section className="enterprise-kpi-band">
          <KpiTile label="Cash coverage" value="2.2 months" tone="mint" />
          <KpiTile label="Forecast delta" value="+18%" tone="blue" />
          <KpiTile label="Budget variance" value="-7%" tone="coral" />
          <KpiTile label="Review status" value="On track" tone="gold" />
        </section>

        <section className="public-band enterprise-band">
          <div className="feature-grid enterprise-feature-grid">
            {platformFeatures.map((feature) => <Feature key={feature.title} {...feature} />)}
          </div>
        </section>

        <section className="public-section enterprise-split">
          <SectionIntro
            eyebrow="Operating model"
            title="A finance cockpit for recurring monthly control."
            text="BankOS gives operators a repeatable path from record intake to classification, budget review, reporting, and executive handoff."
          />
          <WorkflowRail />
        </section>

        <section className="public-section enterprise-insight-grid">
          <CardIssuingShowcase />
          <div className="insight-copy">
            <p className="eyebrow enterprise-eyebrow">Card issuing</p>
            <h2 className="public-heading enterprise-section-title">Cards customers can control without calling support.</h2>
            <p className="public-copy">
              Issue the right card for the job, then manage usage with practical banking controls: turn cards off, turn them back on, block channels, limit spend, and decline risky authorization attempts.
            </p>
            <div className="signal-list">
              {["Debit, credit, savings-linked, and virtual products", "Online, in-store, tap-to-pay, ATM, and international toggles", "Blocked merchant categories and transaction caps", "Step-up protected issuing and control changes"].map((item) => (
                <SignalRow key={item} text={item} />
              ))}
            </div>
          </div>
        </section>

        <section className="public-section enterprise-insight-grid">
          <ExecutivePanel />
          <div className="insight-copy">
            <p className="eyebrow enterprise-eyebrow">Executive readiness</p>
            <h2 className="public-heading enterprise-section-title">Know where money is moving before the close.</h2>
            <p className="public-copy">
              The public experience now mirrors the product promise: dense information, clear controls, and confident operating signals instead of a lightweight brochure.
            </p>
            <div className="signal-list">
              {["Coverage above two months", "Subscriptions reviewed weekly", "Loan movement reconciled", "Category overspend flagged"].map((item) => (
                <SignalRow key={item} text={item} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </PublicShell>
  )
}

export function ProductPage() {
  return (
    <PublicShell>
      <PublicSection
        title="Product"
        eyebrow="Banking platform"
        text="A practical finance management surface for accounts, budgets, transactions, reporting, and admin oversight."
      >
        <div className="product-showcase enterprise-product-showcase">
          <div className="capability-grid enterprise-capability-grid">
            {productCapabilities.map((feature) => <CapabilityCard key={feature.title} {...feature} />)}
          </div>
          <EnterpriseConsole compact />
        </div>
        <section className="public-section compact-section enterprise-module-section">
          <SectionIntro
            eyebrow="Workspace"
            title="Built for repeatable finance and card operations."
            text="Each module is intentionally quiet, dense, and scannable so teams can compare information, issue cards, manage controls, and move through daily operating routines."
          />
          <div className="module-grid enterprise-module-grid">
            {["Dashboard", "Accounts", "Cards", "Transactions", "Budgets", "Reports", "Admin"].map((item, index) => (
              <ModuleCard key={item} index={index + 1} title={item} />
            ))}
          </div>
        </section>
        <section className="public-section enterprise-insight-grid">
          <div className="insight-copy">
            <p className="eyebrow enterprise-eyebrow">Issuing controls</p>
            <h2 className="public-heading enterprise-section-title">Enterprise-style card management, built into the customer app.</h2>
            <p className="public-copy">
              The authenticated Cards workspace now supports card product selection, step-up protected issuing, card off/on, channel controls, per-transaction limits, and authorization decisions.
            </p>
          </div>
          <CardIssuingShowcase compact />
        </section>
        <section className="enterprise-table-section">
          <SectionIntro
            eyebrow="Coverage"
            title="A product map leaders can understand quickly."
            text="From daily account health to monthly governance, the platform is organized around decisions finance teams already make."
          />
          <ProductMatrix />
        </section>
      </PublicSection>
    </PublicShell>
  )
}

export function PricingPage() {
  return (
    <PublicShell>
      <PublicSection
        title="Pricing"
        eyebrow="Plans"
        text="Start with the core workspace, then add controls and support as the finance operation matures."
      >
        <div className="pricing-grid enterprise-pricing-grid">
          {pricingPlans.map((plan) => <Plan key={plan.name} {...plan} />)}
        </div>
        <section className="enterprise-table-section">
          <SectionIntro
            eyebrow="Plan comparison"
            title="Choose by governance needs, not just user count."
            text="The plans are structured around operating maturity: visibility first, then team control, then custom governance."
          />
          <PricingComparison />
        </section>
      </PublicSection>
    </PublicShell>
  )
}

export function SecurityPage() {
  return (
    <PublicShell>
      <PublicSection
        title="Security"
        eyebrow="Trust"
        text="Security posture starts with clear service boundaries, environment-managed secrets, and role-aware access patterns."
      >
        <div className="security-layout enterprise-security-layout">
          <div className="security-card enterprise-security-card">
            <LockKeyhole className="security-icon" />
            <h2 className="section-title">Secure by structure</h2>
            <p className="small-copy mt-2">
              Environment-managed secrets, password hashing, JWT access and refresh tokens, role gates, and separated backend services.
            </p>
            <div className="security-meter" aria-label="Security readiness meter">
              <span style={{ width: "86%" }} />
            </div>
            <div className="security-score-grid">
              <Metric label="Session model" value="JWT" tone="text-blue" />
              <Metric label="Control path" value="Admin" tone="text-mint" />
            </div>
          </div>
          <div className="control-grid enterprise-control-grid">
            {securityControls.map((item) => <ControlRow key={item} text={item} />)}
          </div>
        </div>
        <section className="enterprise-table-section">
          <SectionIntro
            eyebrow="Governance"
            title="Designed to grow toward audit and compliance review."
            text="BankOS does not claim certification here. It gives the app the structural foundation teams need before formal compliance work begins."
          />
          <GovernanceGrid />
        </section>
      </PublicSection>
    </PublicShell>
  )
}

export function ContactPage() {
  return (
    <PublicShell>
      <PublicSection
        title="Contact"
        eyebrow="Sales"
        text="Bring your ledger, reporting, liquidity, and access-control questions. BankOS is ready to extend into deeper workflows."
      >
        <div className="contact-layout enterprise-contact-layout">
          <div className="contact-panel enterprise-contact-panel">
            <Mail className="contact-icon" />
            <h2 className="section-title">Build a banking workspace</h2>
            <p className="small-copy mt-2">
              Tell us about your ledger, reporting, liquidity, and access-control needs. BankOS is ready to extend into onboarding, imports, approvals, and compliance workflows.
            </p>
            <a href="/register" className="btn btn-primary enterprise-btn-primary mt-4">Create account</a>
          </div>
          <div className="contact-topic-grid enterprise-contact-topic-grid">
            {contactTopics.map(([title, text]) => <InfoTile key={title} title={title} text={text} />)}
          </div>
        </div>
        <section className="enterprise-table-section">
          <SectionIntro
            eyebrow="Implementation"
            title="Bring the finance workflow you already run."
            text="The strongest implementation path starts with your current records, review cadence, reports, and permission model."
          />
          <ImplementationTimeline />
        </section>
      </PublicSection>
    </PublicShell>
  )
}

function PublicSection({ eyebrow, title, text, children }) {
  return (
    <main className="public-page enterprise-page">
      <section className="public-hero-small enterprise-page-hero">
        <p className="eyebrow enterprise-eyebrow">{eyebrow}</p>
        <h1 className="page-title enterprise-page-title mt-2">{title}</h1>
        {text ? <p className="public-copy public-hero-copy enterprise-page-copy">{text}</p> : null}
      </section>
      <section className="public-content enterprise-content">{children}</section>
    </main>
  )
}

function SectionIntro({ eyebrow, title, text }) {
  return (
    <div className="section-intro enterprise-section-intro">
      <p className="eyebrow enterprise-eyebrow">{eyebrow}</p>
      <h2 className="public-heading enterprise-section-title">{title}</h2>
      <p className="public-copy">{text}</p>
    </div>
  )
}

function EnterpriseConsole({ compact = false }) {
  return (
    <div className={compact ? "enterprise-console enterprise-console-compact" : "enterprise-console"}>
      <div className="enterprise-console-top">
        <div>
          <p className="enterprise-console-kicker">Treasury operations</p>
          <h2>Liquidity Control Room</h2>
        </div>
        <span className="enterprise-live-dot">Live</span>
      </div>
      <div className="enterprise-console-grid">
        <Metric label="Deposits" value="$12.0k" tone="text-mint" />
        <Metric label="Outflow" value="$6.3k" tone="text-coral" />
        <Metric label="Coverage" value="2.2 mo" tone="text-blue" />
        <Metric label="Health" value="86" tone="text-ink" />
      </div>
      <div className="enterprise-console-body">
        <MiniBars />
        <div className="enterprise-risk-panel">
          <div className="enterprise-risk-head">
            <span>Risk queue</span>
            <strong>3 open</strong>
          </div>
          {["Card exposure within policy", "Payroll reconciled", "Budget variance under review"].map((item) => (
            <SignalRow key={item} text={item} />
          ))}
        </div>
      </div>
      <div className="enterprise-console-footer">
        <span>Forecast refreshed</span>
        <strong>Apr operating view</strong>
      </div>
    </div>
  )
}

function ExecutivePanel() {
  return (
    <div className="executive-panel">
      <div className="executive-panel-header">
        <div>
          <p className="enterprise-console-kicker">Board packet</p>
          <h3>Monthly finance readout</h3>
        </div>
        <FileCheck2 size={20} />
      </div>
      <div className="executive-grid">
        <InfoTile title="Liquidity" text="Coverage remains above threshold with income trend improving." />
        <InfoTile title="Budget" text="Operating variance is under review across software and payroll." />
        <InfoTile title="Debt" text="Loan movement reconciled against scheduled repayment plan." />
        <InfoTile title="Actions" text="Three controls assigned to owners before the next close meeting." />
      </div>
    </div>
  )
}

function CardIssuingShowcase({ compact = false }) {
  const controls = [
    ["Card status", "Turn off / turn on"],
    ["Channels", "Online, in-store, tap, ATM"],
    ["Limits", "Daily, monthly, per transaction"],
    ["Risk", "Category blocks and declines"]
  ]
  return (
    <div className={compact ? "executive-panel enterprise-card-issuing-panel compact" : "executive-panel enterprise-card-issuing-panel"}>
      <div className="executive-panel-header">
        <div>
          <p className="enterprise-console-kicker">Customer cards</p>
          <h3>Enterprise issuing console</h3>
        </div>
        <CreditCard size={20} />
      </div>
      <div className="enterprise-card-preview">
        <div className="enterprise-card-face">
          <span>BankOS</span>
          <strong>**** 4829</strong>
          <small>Virtual vendor card</small>
        </div>
        <div className="enterprise-card-state">
          <span className="status-pill enterprise-pill">Active</span>
          <span className="status-pill">Tokenized</span>
        </div>
      </div>
      <div className="executive-grid">
        {controls.map(([title, text]) => <InfoTile key={title} title={title} text={text} />)}
      </div>
    </div>
  )
}

function MiniBars() {
  const rows = [
    ["Jan", 42, 28],
    ["Feb", 54, 33],
    ["Mar", 47, 38],
    ["Apr", 72, 44],
    ["May", 62, 39],
    ["Jun", 78, 46]
  ]
  return (
    <div className="mini-bars enterprise-mini-bars" aria-label="Income and outflow trend">
      {rows.map(([label, income, expense]) => (
        <div key={label} className="mini-bar-group">
          <div className="mini-bar-track">
            <div className="mini-bar mini-bar-income" style={{ height: `${income}%` }} />
            <div className="mini-bar mini-bar-expense" style={{ height: `${expense}%` }} />
          </div>
          <span className="mini-bar-label">{label}</span>
        </div>
      ))}
    </div>
  )
}

function Feature({ icon: Icon, title, text }) {
  return (
    <article className="feature-card enterprise-card">
      <div className="enterprise-icon-wrap"><Icon size={18} /></div>
      <h3 className="section-title">{title}</h3>
      <p className="small-copy mt-2">{text}</p>
    </article>
  )
}

function CapabilityCard({ icon: Icon, title, text, metric }) {
  return (
    <article className="capability-card enterprise-card">
      <div className="capability-topline">
        <span className="enterprise-icon-wrap"><Icon size={18} /></span>
        <span>{metric}</span>
      </div>
      <h3 className="section-title">{title}</h3>
      <p className="small-copy mt-2">{text}</p>
    </article>
  )
}

function Metric({ label, value, tone }) {
  return (
    <div className="metric-card enterprise-metric-card">
      <p className="metric-label">{label}</p>
      <p className={`metric-value ${tone}`}>{value}</p>
    </div>
  )
}

function KpiTile({ label, value, tone }) {
  return (
    <div className={`enterprise-kpi-tile enterprise-kpi-${tone}`}>
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  )
}

function Proof({ label, value }) {
  return (
    <div className="proof-card enterprise-proof-card">
      <p className="metric-label">{label}</p>
      <p className="proof-value">{value}</p>
    </div>
  )
}

function Plan({ name, price, text, points, highlighted }) {
  return (
    <article className={highlighted ? "plan-card enterprise-plan-card plan-card-highlight" : "plan-card enterprise-plan-card"}>
      <div className="plan-head">
        <h3 className="section-title">{name}</h3>
        {highlighted ? <span className="status-pill enterprise-pill">Recommended</span> : null}
      </div>
      <p className="plan-price">{price}</p>
      <p className="small-copy mt-2">{text}</p>
      <div className="plan-list">
        {points.map((point) => <SignalRow key={point} text={point} />)}
      </div>
      <a href="/register" className={highlighted ? "btn btn-primary enterprise-btn-primary plan-action" : "btn btn-secondary enterprise-btn-secondary plan-action"}>Choose plan</a>
    </article>
  )
}

function WorkflowRail() {
  return (
    <div className="workflow-rail enterprise-workflow-rail">
      {workflowSteps.map(([title, text], index) => (
        <article key={title} className="workflow-step enterprise-workflow-step">
          <span className="workflow-number">{index + 1}</span>
          <div>
            <h3 className="section-title">{title}</h3>
            <p className="small-copy mt-1">{text}</p>
          </div>
        </article>
      ))}
    </div>
  )
}

function SignalRow({ text }) {
  return (
    <div className="signal-row enterprise-signal-row">
      <span>{text}</span>
      <CheckCircle2 size={15} className="text-mint" />
    </div>
  )
}

function ControlRow({ text }) {
  return (
    <div className="control-row enterprise-control-row">
      <span>{text}</span>
      <CheckCircle2 size={15} className="text-mint" />
    </div>
  )
}

function InfoTile({ title, text }) {
  return (
    <article className="info-tile enterprise-info-tile">
      <h3 className="section-title">{title}</h3>
      <p className="small-copy mt-2">{text}</p>
    </article>
  )
}

function ModuleCard({ index, title }) {
  const icons = [Gauge, WalletCards, ReceiptText, SlidersHorizontal, FileCheck2, UsersRound]
  const Icon = icons[index - 1] || Layers3
  return (
    <article className="module-card enterprise-module-card">
      <span className="module-index">{String(index).padStart(2, "0")}</span>
      <span className="enterprise-icon-wrap"><Icon size={18} /></span>
      <h3 className="section-title">{title}</h3>
      <ChevronRight size={16} className="module-arrow" />
    </article>
  )
}

function ProductMatrix() {
  return (
    <div className="enterprise-matrix">
      {[
        [BarChart3, "Operating dashboard", "Cash coverage, net worth, debt movement, and monthly health scoring."],
        [Network, "Connected modules", "Accounts, budgets, transactions, reports, and admin governance share one language."],
        [ClipboardCheck, "Review cadence", "Workflows support weekly operating checks and monthly leadership reporting."]
      ].map(([Icon, title, text]) => (
        <InfoTile key={title} title={<span className="matrix-title"><Icon size={16} /> {title}</span>} text={text} />
      ))}
    </div>
  )
}

function PricingComparison() {
  return (
    <div className="comparison-table-wrap">
      <table className="comparison-table">
        <thead>
          <tr>
            <th>Capability</th>
            <th>Starter</th>
            <th>Business</th>
            <th>Enterprise</th>
          </tr>
        </thead>
        <tbody>
          {comparisonRows.map(([feature, starter, business, enterprise]) => (
            <tr key={feature}>
              <td>{feature}</td>
              <td>{starter}</td>
              <td>{business}</td>
              <td>{enterprise}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function GovernanceGrid() {
  return (
    <div className="governance-grid">
      {[
        [KeyRound, "Identity", "Session and role boundaries are explicit across the app."],
        [ShieldCheck, "Policy", "Admin surfaces create a clear path for approval and review rules."],
        [DatabaseZap, "Data", "Structured records keep audit and export work practical."],
        [FileCheck2, "Evidence", "Report outputs can grow into compliance-ready evidence packets."]
      ].map(([Icon, title, text]) => (
        <InfoTile key={title} title={<span className="matrix-title"><Icon size={16} /> {title}</span>} text={text} />
      ))}
    </div>
  )
}

function ImplementationTimeline() {
  return (
    <div className="implementation-timeline">
      {[
        ["01", "Map accounts", "Document account types, balance sources, owners, and reporting requirements."],
        ["02", "Define controls", "Set budget thresholds, admin roles, review cadence, and export needs."],
        ["03", "Launch workspace", "Load initial records, validate dashboard metrics, and start the monthly rhythm."]
      ].map(([number, title, text]) => (
        <article key={number} className="implementation-step">
          <span>{number}</span>
          <div>
            <h3 className="section-title">{title}</h3>
            <p className="small-copy mt-1">{text}</p>
          </div>
        </article>
      ))}
    </div>
  )
}

function LogoStrip() {
  return (
    <section className="logo-strip enterprise-logo-strip" aria-label="Platform highlights">
      <div className="logo-strip-inner">
        {[
          [CircleDollarSign, "Cash control"],
          [LineChart, "Forecasting"],
          [ClipboardCheck, "Review loops"],
          [Clock3, "Close rhythm"],
          [Sparkles, "Clean reports"]
        ].map(([Icon, label]) => (
          <div key={label} className="logo-pill enterprise-logo-pill">
            <Icon size={16} />
            <span>{label}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

function PublicFooter() {
  return (
    <footer className="public-footer enterprise-footer">
      <div className="public-footer-inner">
        <a href="/" className="brand-lockup">
          <span className="brand-mark enterprise-brand-mark"><Landmark size={17} /></span>
          <span>BankOS</span>
        </a>
        <div className="footer-links">
          {productLinks.map(([label, path]) => <a key={path} href={path}>{label}</a>)}
        </div>
      </div>
    </footer>
  )
}
