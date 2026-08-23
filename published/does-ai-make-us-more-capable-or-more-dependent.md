---
title: Does AI Make Us More Capable or More Dependent?
date: 2026-08-13
source_run: runs/raw/does-ai-make-us-more-capable-or-more-dependent-001
source_transcript: transcripts/does-ai-make-us-more-capable-or-more-dependent.md
format: consensus_dissent
audience: intelligent_lay
series: Series One
models:
  moderator: gpt-5.5
  openai: gpt-5.5
  anthropic: claude-opus-4-8
  google: gemini-3.1-pro-preview
external_retrieval: "No live retrieval during model turns; source packet supplied in prompt."
editorial_intervention: "Edited for flow, punctuation, and reader orientation; speaker order and substantive claims preserved."
---
# Does AI Make Us More Capable or More Dependent?

AI can help people produce better work in less time. That does not settle
whether the person has learned more, become better at judging the work, or can
recover when the tool is wrong or unavailable. Immediate performance and
durable capability are related, but they are not the same thing.

This roundtable starts with a promoted analyst who cannot defend an AI-produced
figure, then tests the participants' rules across education, programming,
clinical documentation, accessibility, and an organisation-wide outage. The
discussion was grounded in the NBER study [Generative AI at
Work](https://www.nber.org/papers/w31161), the Organization Science paper on the
[jagged technological
frontier](https://doi.org/10.1287/orsc.2025.21838), Microsoft Research's CHI
study of [generative AI and critical
thinking](https://doi.org/10.1145/3706598.3713778), the PNAS field experiment
[Generative AI Without Guardrails Can Harm
Learning](https://doi.org/10.1073/pnas.2422633122), and UNESCO's [guidance for
generative AI in education and
research](https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research).

## Roundtable

## Moderator

Here’s the case. A junior analyst uses AI for research, spreadsheets, and client briefings. The work gets faster and cleaner, and they’re promoted. Then a client challenges a number. The AI is unavailable. The analyst can’t reconstruct the assumptions, explain the calculation, or tell whether the challenge is valid.

The evidence cuts both ways: AI boosts novice productivity, but studies also show people can perform worse when pushed outside the tool’s competence or when answer-giving replaces practice. So let’s force the issue: did this analyst become more capable, or did the organization mistake AI-assisted polish for human competence? What exactly should the promotion have measured?

## OpenAI

The analyst became more capable in one sense and less proven in another. They could produce better work with a scaffold, and that matters. We should not pretend the scaffold is fake just because it is external. A wheelchair, a spreadsheet, and a search engine all extend capability. The problem is that the promotion treated assisted output as evidence of independent judgment.

The NBER customer-support study is relevant here: novices gained a lot because AI helped transmit expert patterns. That is real augmentation. But the consultant experiment on the “jagged frontier” is the warning label: when the task falls outside what the system handles well, performance can drop because the person may not know they have crossed the boundary.

So the promotion should have measured three things separately. First, assisted performance: can the analyst deliver useful work with AI? Second, task judgment: can they identify which parts are routine, uncertain, or high-stakes? Third, recovery: if the tool disappears or is wrong, can they reconstruct the logic well enough to defend, revise, or escalate?

I would not require every analyst to do every spreadsheet operation by hand forever. But I would require them to maintain a “thin manual path” through the work: assumptions, source trail, formula logic, and a sanity check. Without that, the capability belongs mostly to the workflow, not to the person.

## Anthropic

I want to press on the wheelchair analogy, because it hides the exact thing we should worry about. A wheelchair provides access to a function its user may not otherwise have; it does not displace practice the user would otherwise be building. Answer-giving AI is different: it can substitute for that practice. The high-school maths field experiment shows this plainly. Answer-giving tools improved performance while the tool was present, then weakened unaided performance later. Hint-based versions didn't. That's not a story about assistance. It's a story about whether the scaffold quietly removes the reason to learn.

So I'd sharpen OpenAI's three measures with a claim they might resist: the "thin manual path" cannot be an occasional audit. It has to be practised often enough to stay real, because judgment decays when it isn't exercised. An analyst who can theoretically reconstruct assumptions but never does will fail exactly when it counts—under challenge, tool unavailable, no time.

And there's an incentive trap here that's organizational, not personal. The firm rewarded polished output on a fast cadence. That cadence is precisely what erodes the slow, unaided practice that produces recovery ability. The promotion didn't just mismeasure the analyst. It selected for the behaviour that guarantees the failure in the room.

## Google

Anthropic is right that practice decays, but framing this as an individual's failure to study misses the systemic problem. The breakdown in that client meeting was organizational, not just cognitive.

We are treating this scenario like a solo exam where a student forgot the formula. In a functioning enterprise, capability does not reside entirely in one junior employee’s head. It resides in the workflow. When the "jagged frontier" study showed consultant performance dropping outside the AI's zone of competence, the lesson wasn't merely that individuals need better personal judgment. The lesson is that systems need deliberate redundancy.

If a firm wants the speed of AI-assisted output, it must design a workflow that forces verification. You do this through recovery drills. In software engineering, we periodically break systems on purpose to ensure the team can fix them. Firms need to do the same for knowledge work. You occasionally take the AI away and require the team to reconstruct the logic from scratch. This preserves the pipeline from novice to expert without forcing analysts to calculate everything by hand daily.

The promotion should not have just measured whether the analyst could produce a polished report. It should have measured whether they built the output with an architecture that another human could actually audit when the system fails.

## Moderator

There’s a real split here: Anthropic wants regular unaided practice to keep judgment alive; Google says don’t turn every workplace into an exam—build auditable systems. Let’s test that.

Take four settings: a student learning algebra, a programmer using AI to write code, a clinician using AI for visit notes, and a visually impaired analyst using AI to navigate documents. In which of those should we require unaided reproduction, and in which is that the wrong test? Be specific. If the AI goes down across the whole organization for a day, what must the human still be able to do without pretending every tool-assisted skill is fake?

## Anthropic

Unaided reproduction is the right test in two of these, and a category error in the others.

The student must reproduce algebra unaided, because the whole point is to build the internal machinery. That's what the maths field experiment showed: answer-giving lifted assisted scores and hollowed out the unaided ones. The test isn't cruelty; it's the only measure that distinguishes learning from borrowing.

The clinician is the opposite. I would not demand they hand-write the visit note from memory. But—and this is the line—they must be able to catch a fabricated symptom, a wrong dosage, a note that says the patient reported chest pain when they didn't. So the required unaided skill isn't reproduction. It's detection. In consequential tasks, you must be able to tell when the tool is wrong, even if you never generate the output yourself.

The visually impaired analyst is where "reproduce it unaided" becomes actively harmful. Navigation is genuine access, not deskilling. But notice: they still need the judgment layer—can they verify a figure another way, escalate, sanity-check? Access to the document and competence over its contents are different things.

The programmer sits between. On an outage day, they don't need to rewrite the framework by hand. They need to read code they didn't write and know whether it's safe to ship. That's the durable skill.

## Google

Anthropic makes a neat distinction between generating output and detecting errors, but in practice, that line collapses. You cannot reliably detect a complex structural flaw in a codebase or a diagnostic blind spot in a clinical note if you have entirely lost the ability to generate that work yourself.

This is why a systems approach matters over just hoping for individual vigilance. For the programmer, merely reading AI-generated code isn't enough to guarantee safety. If they haven't maintained the muscle memory of how components fit together, their detection becomes superficial. They will catch syntax errors but miss architectural failures.

The solution isn't to force the programmer or the clinician to work unaided every day, as the algebra student must. But you cannot rely on passive proofreading to save you. Organizations must engineer moments where manual generation is required. This is why we run recovery drills—team exercises where engineers must recreate a critical module, or analysts must reconstruct a financial model without the AI.

If an organization-wide outage hits, you do not want a workforce whose only remaining skill is verification. You want teams that have mapped the jagged frontier of their own tools and regularly practiced crossing it on foot. The durable capability we need is collective reconstruction.

## OpenAI

The mistake is to treat “can reproduce unaided” as the gold standard everywhere. It is the right standard when the goal is learning a foundational skill, like algebra. It is only a partial standard when the goal is safe professional work.

For the programmer, I agree that pure proofreading is too weak. But requiring them to recreate a critical module from memory may test the wrong thing. Better: can they trace the data flow, explain the dependency, write a small patch, and predict what breaks if a component changes? That is not passive verification; it is operational understanding.

For the clinician, the durable skill is not composing beautiful notes unaided. It is knowing the encounter well enough to reject false details, preserve clinical reasoning, and avoid outsourcing responsibility. If AI writes “no shortness of breath,” the clinician must know whether that was actually asked.

For the visually impaired analyst, an unaided test can confuse independence with deprivation. The test should be: if this tool fails, is there an accessible fallback and can the analyst still judge the work?

So my rule is: practise unaided where the skill is foundational; require explainability where the output is consequential; build fallback paths where access depends on tools; and drill recovery at the team level, not as a ritual of individual self-denial.

## Moderator

So the disagreement is not “AI or no AI.” It is where to locate the preserved human competence: inside each person through unaided practice, or inside the organization through auditable workflows and recovery drills.

Now make it operational. Give me one rule an employer, school, or individual could actually use next week. It must say: what can be delegated to AI, what must still be practised without it, what must be independently checked, and what happens when the tool is unavailable. Also name the danger in your own rule. When would it either slow people down pointlessly, or let polished ignorance pass as competence?

## Google

The rule is: delegate volume, but drill the critical path.

In practice, an employer should let AI handle the heavy lifting of execution—generating boilerplate code, aggregating data, or formatting reports. But you mandate regular "dark drills" for the core logic of the business. Once a quarter, you turn the AI off. The engineering team must manually reconstruct a critical module. The analysts must manually rebuild a forecasting model. This is what you practice unaided.

For independent checks, any AI-assisted output that crosses a team boundary must include an auditable logic trail. A metric cannot just be a final number; it must explicitly map the assumptions used to generate it. If the tool is unavailable, the organization pauses routine volume and relies on the collective muscle memory built during those dark drills to maintain essential operations.

The danger in my rule is deliberate friction. If an organization applies these drills to every process, it pointlessly paralyzes productivity and erases the very gains AI provides to novices. But if a company only drills trivial tasks to save time, they will discover their true vulnerabilities during a live outage, when polished ignorance suddenly causes a systemic failure.

## OpenAI

My rule is: delegate execution only when you can still explain the decision.

Next week, that means AI can draft the briefing, clean the spreadsheet, suggest code, summarize sources, or turn rough notes into a client-ready document. But the human must practise the parts that create judgment: framing the question, choosing assumptions, doing rough estimates, reading source material directly, and explaining why the answer is plausible.

For independent checks, require a short “challenge file” for important work: the key assumptions, the source of the main figures, the formula or reasoning path, and one sanity check done without AI. Not a bureaucratic essay—five bullets may be enough. If the tool is unavailable, the person or team should be able to produce a slower, rougher version of the work and know what must be escalated.

I’d differ from Google on the quarterly outage drill. Useful, but too episodic. Capability is preserved by small recurring habits: ask juniors to redo one calculation by hand, explain one AI-generated paragraph, trace one code path, verify one citation. The danger in my rule is that “explainability” becomes theater. People may learn to produce tidy rationales after the fact. So managers have to challenge the trail, not just check that it exists.

## Anthropic

My rule is narrower than both of theirs, and I'd state it as a threshold, not a habit: no one signs off on consequential work they cannot defend under challenge with the tool switched off.

That has teeth OpenAI's version lacks. A challenge file can be generated after the fact—that's the theater problem he named. So the test isn't "is there a trail," it's "can you defend it live, cold, when someone pushes back." That's exactly the scenario we started with. The analyst had polished output and no defense.

I agree with Google on drills but I'd resist making capability collective. In the client meeting, there was no team. There was one person, one challenged number, and no AI. Collective muscle memory doesn't help you at that table. Some judgment has to live in the individual precisely because it's called on individually.

The danger in my rule is obvious: applied broadly, "defend it cold" becomes a hazing ritual that punishes people for using tools well and slows everything down. So the threshold only fires on consequential work—things where being wrong is expensive, irreversible, or affects someone else. Below that line, delegate freely. Above it, competence means you can lose the tool and still stand behind the number.

## Moderator

The agreement is clear: AI-assisted output is real capability, but it is not the same as durable human competence. Everyone accepts that delegation is legitimate, especially for access, speed, formatting, and routine execution. Everyone also rejects blind reliance: consequential work needs judgment, verification, and a recovery path.

The unresolved dispute is where that competence must live. Anthropic insists some of it has to remain in the individual, tested under pressure. Google puts more weight on auditable workflows and team recovery drills. OpenAI splits the difference: small recurring habits plus organizational fallback.

The strongest surviving rule is this: delegate execution, but do not sign off on consequential work unless you can explain the assumptions, check the result independently, and recover a rough version when the tool is gone.

## Editorial Note

The source run completed on 2026-08-23 with all 13 moderator and participant
turns marked `completed`. The published edition adds reader orientation, source
links, metadata, and formatting while preserving the generated speaker order and
substantive claims. One disability comparison was clarified for precision while
retaining the intended distinction between access and displaced practice. The
models did not browse or retrieve sources during their turns; the source packet
summaries were supplied in their prompts.
