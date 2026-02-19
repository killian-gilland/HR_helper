# 💼 G-SHEET ANALYST: Business Model & Sales Strategy

## Executive Summary

**G-Sheet Analyst** transforms HR recruitment from a time-consuming manual process into an automated intelligence system. Target: Recruitment firms managing 50+ candidate searches annually.

**Price:** €49-99/month  
**Development Cost:** ~20 hours  
**Gross Margin:** 80-85%  
**Payback Period:** 1 week

---

## The Problem We Solve

### Current Pain Points (Recruitment Firms)

| Pain | Cost/Time Impact |
|------|-----------------|
| Manual candidate review (4-6 hours/week) | €180-270/week (€720-1,080/month) |
| Missed "good" candidates in large pools | Lost deals worth €5-20k per hire |
| No ranking system - gut feeling hiring | High turnover (80% first-year failure) |
| Inconsistent evaluation criteria | Legal risk + compliance issues |
| Spreadsheet chaos (no audit trail) | Time wasted tracking changes |

### Our Solution

✅ **Auto-rank candidates** using standardized KPIs (experience, skills, availability)  
✅ **AI-powered insights** - Claude analyzes 100+ candidates in seconds  
✅ **Weekly reports** - HR manager gets actionable summary every Monday morning  
✅ **No tool switching** - Works with Google Sheets they already use  
✅ **Compliance ready** - Full audit trail, no gut decisions  

---

## Target Market

### Primary: Recruitment Firms

**Size:** 10-50 recruiters per firm  
**Process:** Heavy Google Sheets usage (candidate databases, pipelines)  
**Pain:** Spending 40+ hours/week on "plumbing" vs "selling"  
**Budget:** €500-2,000/month for better tools  

**Segment 1: French Tech Recruitment Firms** ⭐ START HERE
- Agencies: Michael Page, Heidrick & Struggles, 10-Visions
- Market size: ~150 firms in France
- Adoption speed: Fast (Paris startup ecosystem mentality)
- ACV (Annual Contract Value): €600-1,200

**Segment 2: Boutique HR Consultancies**
- Size: 5-20 recruiters
- Budget: €300-800/month
- Decision-maker: Founder/HR Director
- Churn risk: Low (founder-led = sticky)

---

## Go-to-Market Strategy

### Phase 1: MVP Launch (Week 1-2)

**Goal:** Land 5 paying customers to validate product-market fit

```
Week 1:
- Reach out to 10 recruitment firms directly (LinkedIn + email)
- Pitch: "€49/month, free 2-week trial, no credit card"
- Offer: Custom onboarding + weekly check-in calls

Week 2:
- Close 5 customers
- Document use cases
- Gather feedback
```

**Outreach Template:**

```
Subject: 10 Hours Back Per Week? (Recruitment Automation)

Hi [Recruiter Name],

I noticed [Company] uses Google Sheets for candidate tracking.

I built a tool that:
✅ Auto-ranks candidates (experience + skills match)
✅ Sends weekly reports with top profiles
✅ Saves ~4 hours of manual review

Most recruiters see ROI in < 1 week.

Free trial: [link] (no credit card, no BS)

Let's jump on a quick call? [Calendar link]

Best,
[Your Name]
```

### Phase 2: Scale (Month 1-3)

**Target:** 20-30 customers, €1,000-3,000 MRR

**Tactics:**
1. **Product-led growth** - Make free tier irresistible
2. **Referrals** - "Refer a recruiting firm, get 3 months free"
3. **Content** - Blog: "Why AI Hiring is Better Than Gut Feelings"
4. **Partnerships** - Recruit agencies (if they use recruitment software)

### Phase 3: Enterprise (Month 4+)

**Target:** 50-100 customers, €5,000-10,000 MRR

**Tactics:**
1. **White-label** - Recruiting software can resell as their feature
2. **Enterprise tier** - Custom KPIs, API access, on-premises
3. **Integrations** - Workable, Lever, SmartRecruiters

---

## Pricing Strategy

### Freemium Model (Recommended)

| Tier | Features | Price | Target |
|------|----------|-------|--------|
| **Free** | 1 source, manual reports, monthly analysis | €0 | Founders, small firms |
| **Pro** | 5 sources, weekly auto-reports, email delivery | €49 | Growing firms (10-20 recruiters) |
| **Business** | Unlimited sources, custom KPIs, API, Slack integration | €149 | Larger firms (50+ recruiters) |
| **Enterprise** | White-label, on-premises, dedicated support | Custom | Enterprise recruitment firms |

### Pricing Rationale

- **€49** = 1 recruiter's saved time per month (€50/hour × 1 hour saved)
- **€149** = Small team savings (€50/hour × 3 hours saved)
- **High margin** because cost is just:
  - Claude API: €0.003/analysis
  - Cloud infrastructure: €0.05/month
  - Support: 30 min/customer/month

---

## Revenue Projections (12 Months)

```
Month 1-2: 5 customers × €49 = €245/month
Month 3: 15 customers × €52 avg = €780/month
Month 6: 40 customers × €65 avg = €2,600/month (includes €149 tier)
Month 12: 80 customers × €72 avg = €5,760/month

Year 1 Total MRR: €5,760
Year 1 Annual Revenue: ~€35,000
Gross Profit (80% margin): ~€28,000

---

Year 2 Projection:
- 180 customers × €85 avg = €15,300/month
- Annual Revenue: ~€184,000
- Gross Profit: ~€147,000
```

---

## Product Roadmap

### MVP (Now)
- ✅ Google Sheets integration
- ✅ KPI calculation (experience, skills, availability)
- ✅ LLM analysis (Claude)
- ✅ Email delivery
- ✅ Cloud Function deployment

### v1.1 (Month 1)
- 🔄 LinkedIn integration (import candidate profile data)
- 🔄 Slack notifications (daily alerts for top candidates)
- 🔄 Custom KPI builder (drag-and-drop)

### v1.2 (Month 2)
- 🔄 API access (webhooks, candidate scoring API)
- 🔄 Recruit firm integrations (Workable, Lever)
- 🔄 Advanced analytics (trends, hiring velocity)

### v2.0 (Month 3+)
- 🔄 White-label platform
- 🔄 On-premises deployment
- 🔄 Advanced LLM fine-tuning per firm

---

## Competitive Landscape

### Direct Competitors
- **Greenhouse, Lever, Workable** - Full ATS (€1,000-5,000/month, overly complex)
- **Hirevue, Pymetrics** - AI-first but expensive, B2C not B2B2C

### Our Advantages
✅ Simple (just Google Sheets + email)  
✅ Cheap (€49 vs €2,000)  
✅ No switching cost (works with existing tools)  
✅ Focused on recruitment firms (not enterprises)  

---

## Customer Testimonial Template

*"We were spending 30 hours/week reviewing candidate pools. G-Sheet Analyst cut that to 5 hours. Worth every penny." - Claire, Founder of [Recruitment Firm]*

---

## Risk & Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Google Sheets API rate limits | Low | Cache + async processing |
| LLM cost explosion | Low | Use cheaper Haiku model, set quota limits |
| Customer churn (month 3) | Medium | Monthly check-ins, free training |
| Competitive copy | High | Speed to market, customer loyalty, switching cost |
| Data privacy concerns | Medium | GDPR compliance doc, SOC 2 roadmap |

---

## Sales Playbook

### Qualification Criteria (ICP)

```
✅ Has 10+ recruiters
✅ Manages 50+ candidates/month
✅ Uses Google Sheets for candidate tracking
✅ Wants to reduce manual reporting
✅ Budget: €300-500/month available
```

### Sales Cycle

1. **Outreach** (Email + LinkedIn) - Target 50 firms
2. **Free trial** (2 weeks) - Let product speak
3. **Discovery call** (30 min) - Understand pain, show ROI
4. **Proposal** (1 page) - Simple pricing, no BS
5. **Close** (5-7 days) - Move fast

### Sales Metrics to Track

```
Outreach → Free Trial: 20% conversion
Free Trial → Paid: 50% conversion
Paid → Retained (Month 3): 80% retention
```

---

## Marketing Messaging

### Headline
**"Your recruitment firm was built to sell, not to process spreadsheets."**

### Sub-headline
Automate candidate analysis. Get weekly intelligence reports. Stop manual ranking.

### Social Media Posts

```
Tweet: "Spent 4 hours ranking candidates yesterday. 
We built a tool that does it in 4 minutes. 
If you recruit, DM for beta access."

LinkedIn: "How we cut candidate review time from 30h to 5h/week.
The secret? Treating recruitment intelligence like a feature, not a chore.
[Link to blog]"
```

---

## Legal & Compliance

- [ ] Privacy Policy (GDPR compliant)
- [ ] Terms of Service
- [ ] Data Processing Agreement (DPA) for enterprise
- [ ] SOC 2 Type I certification (Month 6)

---

## Key Metrics (Dashboard)

```
Acquisition:
- Signups/month
- Free → Paid conversion rate
- Customer Acquisition Cost (CAC)

Retention:
- Monthly churn rate
- Customer lifetime value (LTV)
- NPS (Net Promoter Score)

Monetization:
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- Gross margin %
```

---

## Launch Checklist

- [ ] Product: MVP is live & tested
- [ ] Website: 1-pager with pricing + demo video
- [ ] Legal: Privacy policy, ToS
- [ ] Go-to-market: 50 target firms list + outreach template
- [ ] Support: Help doc + email support setup
- [ ] Metrics: Dashboard set up to track KPIs
- [ ] Sales: 1-pager sales deck ready

---

## Conclusion

G-Sheet Analyst is a **boring, profitable product** for a real pain point. No innovation theater, no pivot later.

- **Simple to build** (20 hours)
- **Simple to sell** (€49 price point)
- **Simple to operate** (fully automated)
- **High margin** (80%+)

**Ready to launch in 1 week.**

---

*Made for founders who think "boring but profitable" > "exciting but burning."*
