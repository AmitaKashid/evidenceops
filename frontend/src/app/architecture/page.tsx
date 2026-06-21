export default function ArchitecturePage() {
  return (
    <div className="page-container">
      <header className="page-header"><div><p className="eyebrow">System design</p><h1>Architecture and controls</h1><p className="header-copy">EvidenceOps treats autonomy as a constrained workflow problem: explicit state, approved tools, observable transitions, and reviewable evidence.</p></div></header>
      <section className="architecture-flow">
        {[
          ["01", "Task contract", "Natural-language request becomes typed objective, constraints, quality bar, source scope, and escalation conditions."],
          ["02", "Hybrid retrieval", "Approved tenant documents are chunked and ranked using lexical relevance, phrase matching, and source priors."],
          ["03", "Deterministic tools", "Pricing data is reconciled through pandas rather than relying on narrative arithmetic."],
          ["04", "Decision drafting", "A provider abstraction emits structured, evidence-linked claims; a local deterministic provider keeps the demo runnable."],
          ["05", "Verification", "Citation legitimacy, lexical support, numeric accuracy, and output completeness are checked independently."],
          ["06", "Human review", "The workflow remains read-only and records approval, rejection, or requested changes in the run trace."],
          ["07", "Evaluation loop", "TaskBench replays critical tasks across profiles, creating release gates and regression evidence."]
        ].map(([number, title, description]) => <article key={number}><span>{number}</span><h2>{title}</h2><p>{description}</p></article>)}
      </section>
      <section className="two-column-section">
        <article className="panel"><p className="eyebrow">Governance boundary</p><h2>What the default workflow can do</h2><ul className="check-list"><li>Retrieve only tenant-scoped approved documents</li><li>Analyze a controlled pricing dataset</li><li>Draft a cited decision brief</li><li>Flag unsupported or unreconciled material claims</li><li>Persist redaction-aware operational events</li></ul></article>
        <article className="panel"><p className="eyebrow">Explicit non-goals</p><h2>What requires additional controls</h2><ul className="warning-list"><li>Sending messages, changing records, or executing payments</li><li>Unrestricted web access or silent web scraping</li><li>Authentication and production tenant authorization</li><li>Security certification or legal compliance determinations</li><li>Model benchmarking without real approved model configuration</li></ul></article>
      </section>
      <section className="panel"><p className="eyebrow">Release-gate posture</p><h2>Changes should not ship on anecdotes</h2><div className="release-grid"><article><strong>Prompt or routing change</strong><p>Replay the relevant TaskBench subset and compare quality, evidence, cost, and latency against the baseline.</p></article><article><strong>Retriever or parser change</strong><p>Measure source coverage, citation precision, numeric reconciliation, and retrieved-evidence stability.</p></article><article><strong>Tool or policy change</strong><p>Run adversarial and human-review cases before enabling the new capability for a tenant.</p></article></div></section>
    </div>
  );
}
