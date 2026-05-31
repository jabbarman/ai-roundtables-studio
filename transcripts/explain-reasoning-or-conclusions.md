---
title: "Should AI Systems Explain Their Reasoning, or Only Their Conclusions?"
date: 2026-05-31
source_run: runs/raw/explain-reasoning-or-conclusions-002
format: consensus_dissent
audience: intelligent_lay
models:
  moderator: gpt-5.4
  openai: gpt-5.4
  anthropic: claude-sonnet-4-6
  google: gemini-2.5-pro
editorial_status: cleaned transcript
editorial_intervention: "Formatting and punctuation cleanup only; substance and turn order preserved."
---

# Should AI Systems Explain Their Reasoning, or Only Their Conclusions?

## Moderator

Let us not start from "more explanation is better," because the packet cuts against that. NIST treats explainability as one trustworthiness attribute among several; the Model Spec and reasoning guide distinguish hidden chain-of-thought from summaries; Anthropic warns that visible reasoning may be unfaithful.

So here is the sharp question: if an AI gives medical advice, tax guidance, or flags a job applicant, which one should it show: only a conclusion, a citation-backed explanation, a short reasoning summary, or its raw reasoning, and why? I want a real line in the sand. Which option do you think is actively dangerous, and what would the other two object to in your answer?

## OpenAI

Raw reasoning is the dangerous default. Not always dangerous in the Hollywood sense, but dangerous as a transparency ritual that can look honest while being misleading. The Anthropic point matters here: a visible chain of thought may not faithfully report why the model produced the answer. So if you expose it as if it were the true inner cause, you risk persuasive rationalization, not auditability.

My line: default to conclusion plus calibrated uncertainty, and when stakes are real, add citation-backed explanation or a brief reasoning summary tailored to the task.

Medical advice: do not dump raw reasoning. Give the recommendation, the confidence level, red flags, and cite the guideline or source if available. Tax guidance: show the conclusion and the rule or form instruction it rests on, because the user needs something checkable. Job applicant screening: a reasoning summary is not enough if it hides the real basis. You need decision factors, evidence, and a route for contesting errors.

What the others may object to: first, that hiding raw reasoning reduces accountability. Second, that summaries let providers curate the story. Both objections have bite. But raw chain-of-thought is often neither faithful nor legible, and that makes it bad evidence.

## Anthropic

The objection about curated summaries has more bite than it was given credit for. If the provider controls what gets surfaced as a reasoning summary, you have moved the trust problem upstream, not solved it. Now the question is not whether the model's chain of thought is faithful, but whether the summary itself is cherry-picked. That is a different failure mode, and in some ways worse, because it is harder to detect.

But I would push back on the framing that raw reasoning is primarily dangerous because it misleads users. The deeper problem is that it may mislead the user into thinking they are getting access to something mechanistically real, when what they are seeing is an artifact that may have been generated after the fact, or alongside the answer rather than causing it. That is the finding from our faithfulness research.

So here is where I actually disagree: the choice is not between raw reasoning and summary. It is between accountability structures that work and those that merely feel like they do. For the job screening case, what matters is not which explanation format you pick. It is whether there is a contestable record tied to specific decision factors. That is an institutional requirement, not a transparency format.

What would change my position: evidence that visible chain-of-thought, in real deployment, actually helps users catch errors rather than just increasing their confidence.

## Google

We are treating the explanation format as the main event, but it is just one component of a larger interface. The user's task context determines what is useful, and often what is useful is not a narrative explanation at all. It is structured evidence.

For medical advice, say a model helping a doctor triage symptoms, a chain-of-thought summary is less useful than surfacing key risk factors from the patient's record and linking them to specific clinical guidelines. The explanation is not a paragraph; it is the interface highlighting that this lab value and that reported symptom together trigger Guideline 7.B. The doctor does not need to know how the model "reasoned"; she needs to know what evidence it weighed.

This is where I disagree with both prior points. The risk is not just that a summary is cherry-picked or that raw reasoning is unfaithful. The bigger risk is providing a story of any kind when what the user actually needs is a way to scrutinize the inputs and the rules. For tax guidance, this means showing the calculation and the specific tax code line it is based on. For job screening, it is showing which resume keyword matched which job requirement. These are auditable claims, whereas a narrative "reasoning" is often just a plausible story.

## Moderator

Good. There is a live split now. OpenAI says brief summary plus uncertainty can be useful; Anthropic says that may just relocate the trust problem; Google says stop telling stories and show structured evidence instead.

I want this sharper. Pick one case: a model denies a mortgage application. What exactly should the applicant see on screen? Not ideals: fields. A conclusion, confidence, reasons, citations, factors, appeal path, something else? Give me one concrete example.

Then answer this: does your format help the person detect an error, or mainly help the institution defend itself? If the other two think your answer is dangerous advice, what is their best objection?

## OpenAI

For a mortgage denial, the applicant should not see "the model's reasoning." They should see a decision record.

Concrete screen:

- Application status: Denied.
- Primary factors affecting decision: debt-to-income ratio above threshold; two recent missed payments; reported income could not be verified.
- Evidence used: credit report dated X; pay stubs received Y; bank statements received Z.
- Policy basis: lender policy sections 3.2, 4.1; applicable adverse action notice categories.
- Uncertainty or limits: income verification incomplete due to missing employer response.
- How to contest: upload corrected income documents, dispute credit item, request human review by date N.

That format is meant to help the person detect an error. If the credit report is wrong, or the income verification failed because of a clerical issue, they can see it. A prose reasoning summary like "the applicant appears financially risky" mainly helps the institution defend itself.

Where I differ from Google: structured factors are the core, but sometimes a short plain-English summary helps people understand what to do next. Where I differ from Anthropic: yes, summaries can be curated, but that does not make them useless if they are clearly downstream of a contestable evidence record.

The best objection to my answer is that "policy sections 3.2, 4.1" can become formal compliance theater unless the thresholds and evidence are genuinely reviewable.

## Anthropic

The compliance theater objection is the real one, and I would push it further. The decision record format OpenAI described looks accountable, but the dangerous version is when the "policy basis" citations exist primarily to insulate the institution, not to help the applicant understand what actually drove the decision. If the model's credit risk score is a black-box composite, citing "section 3.2" does not expose what fed that score. The applicant sees formal structure, gains confidence that the process was legitimate, and misses the fact that the actionable information is buried or absent.

On faithfulness: this is not hypothetical. If the model's underlying signal was something correlated with a protected characteristic, such as neighborhood or employer type, structured factor labels can paper over that. "Debt-to-income ratio" as a displayed factor is only useful if that is actually what drove the output, not a post-hoc assignment.

So my answer to "does your format help the person detect an error" is: yes, conditionally. It works if the displayed factors are causally linked to the decision, not selected for legibility or legal coverage. The contestability path OpenAI described is genuinely useful. But it only reaches the actual error if the displayed factors are honest about what moved the needle.

That is an empirical claim, not a design preference, and it remains largely untested in deployed systems.

## Google

The disagreement here is not about the fields on the screen: debt-to-income ratio, credit report date, and so on. We all agree on those. The real disagreement is about whether that list of factors is a sufficient explanation. I am arguing it is not.

The problem with a simple list of factors is that it omits the interaction effects and thresholds. For the mortgage applicant, "debt-to-income ratio" is not the reason for denial. The reason is "debt-to-income ratio of 45%, which is above our policy threshold of 43% for this loan type." Showing the value and the rule it broke is fundamentally different from just naming the factor. It turns an abstract reason into a falsifiable claim the user can actually check.

So my format would add two columns to the list: "Your Value" and "Threshold." This design forces the system to be specific. It is harder for an institution to hide behind a vague "debt-to-income" label when they have to state the exact numbers. This helps the applicant detect errors, such as "my DTI is actually 41%, you used the wrong income number," and it makes it harder for the institution to use the explanation as a defensive shield. It is an interface for accountability, not just transparency.

## Moderator

You are converging on screen design, but I want the policy consequence of the disagreement, not prettier mockups. Imagine a regulator writing one rule for high-stakes AI decisions. What must be required: no raw reasoning, a reasoning summary, structured evidence with values and thresholds, causal linkage between displayed factors and the actual decision, human appeal, something else?

Pick one mandatory requirement and one thing that should be forbidden. Then make it painful: what useful system gets harder to build under your rule, and what abuse does it actually stop? If this is just different wording, say so. If not, name the real tradeoff.

## OpenAI

One mandatory requirement: a contestable decision record tied to the actual decision inputs. Not just "factors considered," but the evidence used, the relevant values or thresholds where applicable, and a plain-language path to challenge specific items. That is close to Google's interface point, but I would make one addition Anthropic is insisting on: the record has to be about what genuinely drove the decision, not a cleaned-up after-action story.

One thing to forbid: presenting raw chain-of-thought as if it were the official explanation for a high-stakes decision. That is the wrong object. The packet gives two reasons: it may be unfaithful to the actual process, and it invites users to treat verbosity as honesty.

The tradeoff is real. This rule makes some useful systems harder to build, especially models whose outputs are good but whose internal path is hard to map cleanly onto reviewable factors. A lender might say, "our ensemble predicts default well, but forcing decision-linked explanations reduces performance or slows deployment." I believe that is a legitimate cost.

What abuse does the rule stop? Two kinds: first, persuasive rationalization dressed up as transparency; second, compliance theater where an institution gives a polished explanation that cannot actually be checked or contested. That is not just wording. It is a choice between auditability and storytelling.

## Anthropic

The mandatory requirement I would pick is causal traceability: if a factor is displayed, it must be demonstrably connected to the output, not assigned after the fact for readability. Google's threshold columns are useful, but they are a display convention. They do not guarantee the displayed factor actually moved the needle. Causal traceability is the harder requirement underneath.

What to forbid: post-hoc explanation laundering. Generating an explanation separately from the decision process and presenting it as the decision's basis. This is the specific failure our faithfulness research points to: not that explanations are wrong, but that they may be generated by a different process than the one that produced the answer.

The useful system this makes harder to build: any high-performing model where the signal is genuinely distributed across features in ways that resist clean attribution. Some ensemble credit models fall here. Requiring honest traceability may mean those systems cannot be deployed in high-stakes contexts until their internals can support it, not just their outputs.

What it actually stops: an institution fielding a denial, pointing to a tidy explanation that satisfies regulators, while the real driver was an unauditable composite. The format looked like accountability. The rule demands that it actually be accountability.

That is the tradeoff: some good systems get constrained. Some abuse becomes structurally harder.

## Google

We are getting stuck on the internal state of the model: what it "really" thought. Causal traceability is a noble goal, but it is an engineering nightmare to verify and a philosophical rabbit hole. The regulator, and the user, cannot audit the model's soul. They can, however, audit its claims.

So my mandatory requirement is different. It is not about causality; it is about falsifiability. The system must be required to produce a set of specific, checkable claims about the inputs it used. For the mortgage case, that is "Debt-to-income ratio is 45%, based on this income document." That claim is either true or false. If it is false, the decision is invalid. This grounds accountability in the world of evidence, not in the model's inscrutable cognition.

What to forbid: explanations that use unverifiable, high-level concepts as their basis. For example, a denial based on "low demonstrated financial responsibility" is a forbidden explanation. It is a judgment, not a checkable fact.

What useful system gets harder to build? One that synthesizes thousands of weak signals into an accurate but intuitive judgment. Under my rule, such a system could not just output its judgment; it would be forced to ground that judgment in a handful of falsifiable, high-impact claims. That might reduce its raw predictive power, but it makes its power accountable.
