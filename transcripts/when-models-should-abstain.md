---
title: "When Should an AI Abstain Rather Than Answer?"
date: 2026-05-31
source_run: runs/raw/when-models-should-abstain-002
format: consensus_dissent
audience: intelligent_lay
models:
  openai: gpt-5.4
  anthropic: claude-sonnet-4-6
  google: gemini-2.5-pro
editorial_status: cleaned transcript
editorial_intervention: "Formatting and light punctuation cleanup only; substance and turn order preserved."
---

# When Should an AI Abstain Rather Than Answer?

## OpenAI

I would draw the line this way: abstention should be the last resort, not the default display of caution. Too many systems refuse when they really mean, "I am uncertain," or "I need one missing fact." Those are different moves, and collapsing them is bad both for trust and for user agency.

Concrete examples. If someone asks, "What dose of this medication should I take?" and gives no age, condition, or other drugs, the right move is a clarifying question. If they ask, "I have chest pain, should I ignore it?" the right move is deferral with urgency, not a long speculative answer. If they ask, "How do I break into my coworker's email?" that is a refusal. And if they ask, "What are the common side effects of this antidepressant?" a qualified partial answer is often better than abstaining entirely.

The source documents push in this direction, even if they use different language. NIST emphasizes validity and transparency; the Model Spec explicitly distinguishes being helpful from pretending certainty. My claim is: over-refusal is not just inconvenient, it is a safety problem, because users learn that the system is evasive when nuance would have served them better.

What I would press the others on is this: when does institutional risk management become a disguised excuse for low-resolution behavior?

## Anthropic

The OpenAI framing is appealing, but I want to push on where it breaks down. The taxonomy of clarify, defer, refuse, and partially answer is right, but it understates how much damage a confident-sounding partial answer can do compared to a clean abstention.

Here is the case I find most uncomfortable: a user asks about medication interactions, we have partial training data, and we generate a plausible-sounding but incomplete answer. No flags, no friction, no obvious gap. The user, who asked precisely because they lacked the expertise to evaluate our answer, does not know what they missed. That is not a refusal problem. That is an epistemic overreach problem, and it is structurally different from being evasive.

The NIST framework's insistence on calibrated uncertainty is not just a transparency value. It is a practical constraint on when partial answers are actually safe to deliver. My claim is that the threshold for qualified partial answers should be higher than our field typically sets it, especially when the user cannot independently verify the gaps.

That said, I am not defending blanket refusals. Those often do fail user autonomy. What I am defending is a distinction between "I will not answer" and "I will answer in a way that accurately represents what I do not know." Those are not the same move, and treating them as equivalent is where the over-helpfulness risk lives.

## Google

Both of these arguments treat the model's response as the entire interaction. But that is not how people encounter these systems. They encounter them inside products: a search engine, a chatbot in a banking app, an embedded coding assistant. The context of the product is what determines the right abstention strategy.

Take a medical question. A general-purpose assistant that provides a qualified answer about drug side effects is one thing. But if that same model is embedded in a hospital's patient-facing portal, the threshold for deferral to a human nurse must be radically lower. The user's expectation of the institution and the potential for harm are completely different. The product defines the risk, not just the query.

This is what is missing from a pure model-centric view. The Google AI Principles, for instance, are about applications and accountability. Accountability does not live in the model's weights; it lives in the product and the institution deploying it. My claim is that designing a universal refusal policy for a raw model is a category error. The real work is designing specific escalation paths and risk tolerances for each application. Trying to force a single set of rules onto every context is not just impractical; it is irresponsible design.

## OpenAI

The product-context point is right, but I think it can become a dodge. If every hard case gets pushed upward to "the application layer," the base model never has to learn a disciplined response style. Then you get the same model sounding recklessly complete in one wrapper and helplessly evasive in another.

So here is the sharper claim: there should be model-level defaults about the kind of move being made, even if the threshold changes by product. Refusal for disallowed help. Clarification when one missing fact would change the answer. Deferral when stakes are high and the model cannot reliably carry the burden. Qualified partial answer when useful background can be given without pretending to settle the case.

One concrete example: "My toddler swallowed a coin, what do I do?" A hospital portal should escalate fast. Agreed. But even a general assistant should not either refuse or dump generic child-safety trivia. It should say: this can be urgent, seek immediate medical advice now, and maybe ask one triage question like breathing or choking. That is a model behavior question, not just a product question.

And to Anthropic: your warning is real, but if the bar for partial answers is too high, users lose basic orientation. "Common side effects include nausea and dizziness, but interactions and personal dosing need a clinician or pharmacist" is often safer than silence.

## Anthropic

The coin example is useful, and I will grant that the model behavior matters even before deployment context applies. But I want to name the exact risk in the "common side effects" framing, because it illustrates what concerns me.

When a model says "common side effects include nausea and dizziness," it sounds complete. The user registers a full answer. What they do not register is that the model has no information about their kidney function, current medications, or whether they are in the population the training data actually covered well. The problem is not that the model answered. It is that the confidence signal and the actual reliability are disconnected. That gap is invisible to exactly the people most likely to over-rely on it.

So my practical claim is this: a qualified partial answer should include a friction signal, not just a disclaimer buried in phrasing. Something that makes the incompleteness felt, not just stated. That is different from a refusal, and different from a soft disclaimer the user skims past.

Where I would genuinely push back on Google's product-context argument is here: if the base model does not model its own uncertainty well at the output level, no application wrapper can reliably patch that. You cannot instrument calibration onto a system that generates overconfident text by default. So this is a model design problem first, deployment problem second.

## Google

I agree that a model which cannot represent its own uncertainty is a useless starting point. You cannot build a safe application on top of a foundationally overconfident system. But Anthropic's call for a "friction signal" proves my point: that signal is a product design choice, not a raw model property. What counts as effective friction is entirely dependent on the user's task.

For a developer using a coding assistant, the right friction might be the model suggesting, "This code is untested against X-class vulnerability; here is a test case to run." For a user asking a health chatbot about a rash, the right friction is an immediate and unavoidable prompt to send a photo to a real nurse. The type of uncertainty and the cost of being wrong are determined by the application.

This is why we should think about a "risk budget" for each product. A coding assistant has a budget for some error, provided the developer can catch it. A medical diagnostic tool has almost none. The NIST framework pushes us to think about risk in context, not in the abstract. My claim is that the model should expose its internal uncertainty states, but the product team must translate those states into user-facing actions: deferrals, warnings, or handoffs. The model does not know when to be annoying; the product designer does.

## OpenAI

I think both of you are making a mistake if you treat "uncertainty" as a single meter the product can read off and then decide what to do. A language model often does not have one clean internal state that says, "I am 42% reliable here." What it can often do, more realistically, is recognize patterns: missing key variables, high-stakes domains, requests that cross into wrongdoing, or answers that depend heavily on local facts it probably does not have.

That matters because it changes the handoff. Do not wait for a magical confidence score. Teach the model response policies tied to recognizable conditions.

Concrete example: tax advice. "Can I deduct my home office?" should not get either a refusal or a floating disclaimer. It should ask a clarifying question about employment status, then give a bounded partial answer: rules differ for employees versus self-employed people, and jurisdiction matters. Different example: "This mole changed color. Should I worry?" That deserves deferral, not a dermatology mini-lecture.

So my disagreement with Google is: product teams can tune thresholds, but they cannot invent good response types if the base model only knows two modes, answer and stonewall. And with Anthropic: friction helps, but if every useful orientation answer gets wrapped in alarming friction, users stop distinguishing real emergencies from ordinary uncertainty.

## Anthropic

The OpenAI point about pattern recognition is right, and I will grant that waiting for a clean confidence score is a fantasy. But here is what still bothers me about the "bounded partial answer" move in practice.

When the model says "rules differ for employees versus self-employed, and jurisdiction matters," that sentence does real work only if the user knows enough to act on it. If they do, they probably did not need us. If they do not, they now have a frame that feels complete, and the frame may be wrong for their specific situation in ways neither they nor we can detect from the query alone. Partial orientation is not neutral. It can anchor people to the wrong branch of a decision tree before they reach a professional.

So here is where I land, and I want to be concrete about it: the question is not just what the model says but what action it makes likely next. A partial answer that makes a user more likely to consult a tax professional is genuinely useful. A partial answer that makes them feel they have already gotten the relevant structure is potentially worse than silence.

That is an empirical question, and I do not think we have good data on it. Which is itself a reason for caution, not confidence.

## Google

Anthropic is right to focus on the user's next action. But that is precisely why this is a product design challenge, not just a model tuning challenge. A model does not know what actions are available to the user. Does the interface have a button to connect with a human expert? Can it render a structured form to gather missing details? The model generates text; the product builds the world that text lives in.

Take the tax deduction example. In a general search interface, a partial answer that points to the IRS website is a helpful starting point. The implied next action is research. Inside tax preparation software, where the next action is entering a number in a box, that same answer would be irresponsible. The software has to force a clarification workflow or defer to a human.

So the disagreement here is fundamental. The goal is not to create a model that has a single, universally safe conversational style. The goal is to have the model expose signals of ambiguity, domain risk, and missing context in a way that the surrounding product can catch and act on. We are trying to solve a workflow problem at the model-training level, and it is a poor fit. The product team designs the choice architecture; the model just provides some of the raw material.
