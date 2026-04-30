"use client"

import { ArrowRight } from "lucide-react"

export function ContactForm() {
  return (
    <form className="contact-form" onSubmit={(e) => e.preventDefault()}>
      <div className="contact-form-row">
        <div>
          <label className="field-caption">First name</label>
          <input className="input" placeholder="Jane" />
        </div>
        <div>
          <label className="field-caption">Last name</label>
          <input className="input" placeholder="Smith" />
        </div>
      </div>
      <div>
        <label className="field-caption">Work email</label>
        <input className="input" type="email" placeholder="jane@company.com" />
      </div>
      <div>
        <label className="field-caption">Company</label>
        <input className="input" placeholder="Your organization" />
      </div>
      <div>
        <label className="field-caption">Plan of interest</label>
        <select className="select">
          <option value="">Select a plan...</option>
          <option>Starter</option>
          <option>Business ($29/mo)</option>
          <option>Enterprise (custom)</option>
        </select>
      </div>
      <div>
        <label className="field-caption">How can we help?</label>
        <textarea className="textarea" placeholder="Tell us about your banking and finance needs..." />
      </div>
      <button type="submit" className="btn btn-primary enterprise-btn-primary contact-submit">
        Send message <ArrowRight size={14} />
      </button>
    </form>
  )
}
