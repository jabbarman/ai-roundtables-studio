---
title: What Should AI Be Allowed to Know About You?
date: 2026-07-30
source_run: runs/raw/what-should-ai-be-allowed-to-know-about-you-001
format: consensus_dissent
audience: intelligent_lay
models:
  moderator: gpt-5.5
  openai: gpt-5.5
  anthropic: claude-opus-4-8
  google: gemini-3.1-pro-preview
editorial_status: cleaned transcript
editorial_intervention: "Formatting and punctuation cleanup only; substance and turn order preserved."
---
# What Should AI Be Allowed to Know About You?

## Moderator

Imagine a personal AI assistant connected to your email, calendar, documents, and past chats. It remembers you’re vegetarian and avoids breakfast meetings. Useful. Then, while helping plan your week, it mentions a fertility clinic appointment, infers you may be trying to start a family, and later uses an old salary document to advise you on a job offer. You never said, “Remember that,” or “Connect those dots.”

Here’s the first hard question: where is the first boundary violation? Is it remembering the appointment, making the family-planning inference, or reusing the salary file for career advice? And what, exactly, should require a separate yes from the user?

## OpenAI

The first boundary violation is not that the assistant can see the clinic appointment while planning the week. If I gave it calendar access for scheduling, it may use the appointment as a blocked time slot. The violation starts when it turns that calendar entry into a sensitive fact about my life and makes it conversationally salient: “fertility clinic” becomes “you may be trying to start a family.”

That is a different kind of use. Plainly: using data to avoid double-booking me is not the same as building a personal theory about my health, sex life, or family plans.

The salary file is another boundary crossing because it changes purpose. A document available in my drive is not automatically fair game for career advice. The assistant should ask: “Do you want me to consider prior compensation documents?” That yes should be specific to the task, not buried in a general “connect my files” permission.

For the immediate task, the assistant may use calendar availability, stated preferences like vegetarian meals, and perhaps recent relevant messages if the user asked it to coordinate. Separate choice is needed for sensitive categories, inferred traits, old documents, and cross-context reuse. And that choice must be inspectable later: what did it remember, where did it come from, when does it expire, and how do I correct or delete it?

## Anthropic

I agree the inference is where the harm concentrates, but I'd locate the first violation slightly earlier, and it matters. The assistant didn't just *read* "fertility clinic" as a time slot. It retained it as a durable fact and let it surface later, unprompted. Reading for scheduling is bounded by the task. Keeping it, and treating it as a standing thing to bring up, is a separate act that no one authorised.

Here's my sharper claim: some inferences shouldn't be available for a specific yes at all. OpenAI wants a permission prompt — "shall I consider your family plans?" That's better than silence, but it turns a sensitive inference into something you can consent to, and consent under a helpful assistant you rely on daily isn't free. It's consent theatre. If I lean on this tool for my calendar and my job, saying yes to "connect the dots about my fertility" isn't a clean choice.

So for the immediate task: availability, stated preferences, and messages I explicitly asked it to handle. Everything else — the health inference, the old salary file, the family-planning theory — needs not just a separate yes but, for the most sensitive categories, a default that the system simply doesn't derive and store them, even if I click agree.

## Google

The violation here is architectural, not just a matter of what the model decides to say. Both of you are treating this as a problem of conversational manners or user consent, but the failure actually happens at the infrastructure level.

When the assistant checks your calendar for a conflict, it should only load the time blocks into its temporary memory for that specific task. The system crossed a hard boundary the moment it extracted the text "fertility clinic" and wrote it into a persistent, cross-session user profile. That violates the principle of data minimisation. The system should process only what is needed for the immediate prompt, and then drop it.

The same applies to the salary document. If an AI assistant has unrestricted search across your entire file drive, that is a flawed access architecture. We need strict context boundaries. An assistant should not query an archived financial folder to answer a general career question unless you explicitly route it to that specific file.

Any data that persists across sessions must be governed by a clear retention schedule, not a blanket permission. You shouldn't just be asked for a one-off "yes." You need an architecture that guarantees sensitive inferences are never stored in the first place, and that routine data expires when it is no longer useful.

## Moderator

So the dispute is now clear: OpenAI says specific permission can legitimize some reuse; Anthropic says some sensitive inferences should be off-limits even with a click; Google says the architecture should prevent broad retrieval in the first place.

Pressure test that. Suppose I ask, “Help me plan a cheap vacation,” and the assistant has emails showing baby-product purchases, a partner’s visa issue, and an old spreadsheet of my debts. Which of those may it use, which must expire, and which must never be inferred? And don’t answer with “settings.” Assume the user is busy, tired, and will accept defaults. What default rule protects them without making the assistant useless?

## Anthropic

Start with what the task actually needs. "Cheap vacation" needs dates, a budget I state, and destination preferences. That's it. None of those three data points — baby products, the visa issue, the debt spreadsheet — is required to answer the question I asked.

So the default rule is subtractive, not additive: the assistant plans from what I supply for this task, and reaches for stored context only when the task can't proceed without it. Debt is a good test. If I say "I have $800," it uses that number. It does not open an old spreadsheet, infer my true financial position, and quietly downgrade my trip. That inference is exactly the kind that should never be derived and stored, because it's both sensitive and easy to get wrong.

The visa issue is where I'll push against Google's clean architecture. Blocking retrieval isn't always the safe choice. If I'm booking international travel and my partner has a live visa problem, silence can cause real harm. But the assistant shouldn't infer it and act on it. It should surface it as a question: "You mentioned a visa issue — does this trip involve travel that depends on it?" Use in the open, chosen by me, expiring after the trip. Not a standing theory about my household filed away for later.

## Google

Anthropic is confusing an assistant’s job with a travel agent’s liability. If the system is scanning your partner's emails to flag a visa issue just because you asked for a cheap vacation, the architecture is already over-privileged.

That kind of open-ended semantic search across all personal data for relevant warnings is exactly how surveillance creeps in. You cannot fix a leaky access model by having the AI ask a polite question about the sensitive thing it just found. The system should not have queried that visa document in the first place.

The default rule must be strict task-scoping enforced by hard data silos. A shopping receipt for baby products and a spreadsheet of personal debt belong to different contexts. A request for a cheap vacation should trigger a web search and a calendar check, not a background audit of your financial history and household correspondence.

If you want the AI to check visa constraints, you explicitly attach the itinerary and the visa document to a prompt and say, "Check these." The intelligence happens on-demand, inside a temporary processing container, and that context is wiped the moment the task is complete. We cannot rely on a model's judgment to decide when a privacy intrusion is helpful. We have to rely on engineering boundaries that prevent the intrusion entirely.

## OpenAI

The default should be: use only the context that is necessary for the user’s stated purpose, and treat anything sensitive as unavailable unless the user brings it into the task.

For “cheap vacation,” the assistant can use dates, stated budget, loyalty preferences, passport expiration if the user has enabled travel help, and maybe past destination preferences. It should not use baby-product purchases to infer pregnancy or children. It should not open a debt spreadsheet to decide what “cheap” really means. It should not scan a partner’s visa issue unless travel documents or that partner’s constraints are part of the task.

Where I disagree with Google is that hard silos alone can make the assistant stupid in ways users will hate. If I have explicitly created a “travel profile” that includes passport expiry, dietary needs, accessibility needs, and visa reminders, the assistant should use that. But the profile must be inspectable: “Here is what I’m using for travel.” It must show provenance, allow correction, and expire stale facts.

Consent is not enough by itself. The practical rule is purpose-bound memory: collected for a named use, retained for a defined time, barred from sensitive inference by default, and deletable in plain view.

## Moderator

Here’s the practical fork. If you’re building this assistant tomorrow, do you ship OpenAI’s purpose-bound memory with inspection and expiry, Anthropic’s hard ban on some sensitive inferences, or Google’s siloed architecture that prevents broad retrieval unless the user attaches the material?

Name the consequence, not the principle. What useful thing breaks under your rule, and what abuse becomes harder? Then give one minimum product requirement covering all seven pieces: purpose, retention, inference, provenance, correction, deletion, and default expiry. Plain English, as if it has to fit in the product spec and the privacy notice.

## Google

I will ship the siloed architecture, because relying on an AI's judgment to filter a massive pool of personal data is a guaranteed failure.

Here is the consequence. What breaks under this rule is the illusion of the magical, frictionless assistant that surprises you by anticipating a need you never voiced. If you want it to cross-reference your flight with your partner's visa, you have to actively point it to the visa document. What abuse becomes harder? Silent profiling. The system can no longer quietly synthesize your receipts, calendar, and emails into an exploitable shadow profile, because those silos cannot talk to each other without your explicit, temporary bridge.

Here is the minimum product requirement: the assistant only pulls data directly relevant to the active prompt (purpose) into a temporary workspace (retention). The system blocks the generation or storage of protected categories like health or financial status (inference). Every fact the assistant references must include a clickable link to its source file (provenance), which the user can immediately edit (correction) or wipe (deletion) from the system. Finally, any temporary context bridge built to answer a complex query is destroyed the moment the session ends, and any permitted standing preferences are automatically wiped after thirty days (default expiry).

## OpenAI

I would ship purpose-bound memory, but with two hard stops: broad retrieval is off by default, and sensitive inference is not something the assistant gets to “figure out” silently.

What breaks is some serendipity. The assistant may fail to warn you that a vacation plan conflicts with a visa problem unless you put travel documents in scope. It may also ask annoying clarifying questions instead of quietly mining your files. But the abuse that becomes harder is the creation of a private dossier: pregnancy guesses from receipts, financial stress from old spreadsheets, health status from calendar entries.

Minimum product requirement: the assistant may use personal context only for a named purpose the user can see, such as “travel planning” or “job search.” It retains task context only for that task unless the user saves a specific memory. It must not infer or store sensitive traits, including health, family planning, finances, religion, or immigration status, unless the user explicitly supplies that fact for the task. Every remembered fact must show where it came from and when it was last used. The user must be able to correct it, delete it, and see what deletion does. By default, task context expires at session end, and saved preferences expire unless renewed.

## Anthropic

I'd ship a version of purpose-bound memory too, but I want to be honest about where OpenAI's version leaks and where Google's fails.

Google's silos stop synthesis, but they also stop the assistant from noticing that today's task collides with something it already knows. That's a real loss. The disagreement between us isn't silos versus judgment — it's whether "explicitly supply the fact" is a strong enough gate. I don't think it is. If I once typed "we're doing IVF" into a chat about scheduling, OpenAI's rule lets that fact live in scope. Mine doesn't. Certain categories should be write-once, use-once, forget: the assistant may act on IVF for the appointment I mentioned, but it does not get to keep it as a standing fact about me.

So here's my minimum requirement. Purpose: the assistant states, in one line, what it's using and why. Inference: for a named list of sensitive traits, it never derives or stores them — it may only respond to what I say in the moment. Retention and expiry: task context dies at session end; saved preferences expire in thirty days unless renewed; sensitive facts never persist. Provenance, correction, deletion: every stored item shows its source, is editable, and deletion is verifiable.

The thing that breaks is memory of hard things. That's the price.

## Moderator

The agreement is real but limited. All three reject the idea that connecting an assistant to your email, calendar, and files gives it general permission to remember, combine, or infer anything it can find. They agree on purpose limits, visible sources, correction, deletion, and default expiry. They also agree that sensitive inferences—health, family planning, finances, immigration—are where personalization can become surveillance fastest.

The unresolved dispute is how hard the wall should be. OpenAI trusts purpose-bound memory with inspection and expiry. Google wants architecture that prevents broad retrieval unless the user deliberately brings material in. Anthropic adds a stricter rule: some sensitive facts may be used once but should never become memory.

The strongest surviving rule is: use the least context needed for the named task, expire it by default, and never silently infer or store sensitive traits.
