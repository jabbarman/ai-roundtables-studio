---
title: Who Is Responsible When AI Gets It Wrong?
date: 2026-07-02
source_run: runs/raw/who-is-responsible-when-ai-gets-it-wrong-001
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
# Who Is Responsible When AI Gets It Wrong?

## Moderator

A customer asks a company’s chatbot, on the company’s own website, whether they qualify for a refund or special fare. The chatbot says yes. The customer relies on it, spends money, and later the company says: sorry, the bot was wrong. That is close to what happened in the Air Canada case, where the company was held responsible for misleading information its chatbot provided.

Here’s the first dispute: should the default rule be that the company owns the mistake whenever it puts the chatbot in front of customers, or does the customer still have a duty to verify against the fine print? Don’t give me “shared responsibility” yet. Pick a default.

## OpenAI

The default should be that the company owns the mistake when the chatbot is speaking inside the company’s own service channel about the company’s own rules.

By “owns,” I don’t mean every wrong answer becomes a giant lawsuit. I mean the company should honor the reasonable promise it created, fix the customer’s position where possible, and absorb the ordinary cost of its own misleading interface. If an airline chatbot tells me I qualify for a bereavement fare, or a retailer chatbot says a return is still eligible, I should not have to treat that answer as a rumor and then audit the legal terms like a contract lawyer.

The customer still has some responsibility, but it is weaker and narrower. If the bot says something obviously absurd—“all flights are free tomorrow”—verification is expected. If the stakes are unusually high, like a medical dosage or immigration filing, the user should seek a more authoritative source. But for routine consumer decisions, the organization chose to automate the front desk.

The harder question is upstream. The model provider may have built the engine, the product team may have wrapped it badly, and the deploying company may have failed to test or monitor it. But from the customer’s point of view, the accountable party is the institution that put the bot between itself and the public.

## Anthropic

The default is right, but I want to name what makes it more than a customer-service nicety. The customer in the Air Canada case couldn't have audited the system even if he'd tried. He couldn't see the prompt, the training data, the version history, or whether the company had ever tested the bot on bereavement-fare questions. That asymmetry is the heart of it. When one party controls the interface, the information, and the record, the duty to get it right sits with that party—not as charity, but because they're the only one positioned to catch the error.

So I'd push the default further than "honor the reasonable promise." The deploying institution owes specific organizational duties: test the bot on the questions people actually ask, monitor for wrong answers, correct them quickly, disclose clearly when an answer isn't authoritative, and compensate when someone relies and loses. Those are different from a customer's ordinary habit of double-checking.

Here's my disputable claim: even an "obviously absurd" answer doesn't fully shift blame back to the user if the company knew its bot produced absurd answers and shipped it anyway. Foreseeability cuts against the deployer, not the harmed person. The customer's duty to verify shouldn't quietly become a subsidy for the company's decision not to test.

## Google

The deploying company must own the relationship with the customer, but owning the relationship is not the same as owning the underlying failure. If an airline puts a chatbot on its homepage, it has to refund the user when the bot invents a fake policy. That is the necessary baseline.

But Anthropic stops too early by placing all the weight on the deployer's duty to test and foresee errors. Testing alone cannot solve this if the failure stems from a layer the deployer does not control. We have to look at the entire supply chain. A customer-facing chatbot usually involves a foundation model provider, a product integration team, and the deploying institution that provided the rulebook. 

If the chatbot lied because the airline uploaded an outdated PDF to the knowledge base, the airline is entirely at fault. But what if the model ignored a perfectly clear system prompt and hallucinated a policy out of nowhere? 

Here is my claim: We cannot enforce responsibility at the deployment layer without mandatory traceability throughout the stack. The NIST framework points to information integrity as a shared lifecycle control. If model providers shield their systems behind sweeping liability waivers, we are forcing non-technical companies to act as the ultimate insurers for generative AI failures. The deployer compensates the end user, but the model provider must be accountable to the deployer for baseline reliability.

## Moderator

Let’s test the fault line. Suppose an employer launches a benefits assistant. It tells a worker they’re eligible for paid leave; they rely on it; HR later says no. Now change the case: a school uses an AI tool to flag students for investigation, or a hiring system screens out applicants. And finally, a hospital discharge tool gives unsafe follow-up advice.

In each case, who must compensate or correct first: the institution facing the person, or the vendor/model provider behind the system? Google, your traceability point risks delaying remedy while companies argue upstream. Anthropic, your deployer-first view risks making every institution the insurer for defects it cannot inspect. Name the tradeoff.

## Anthropic

The tradeoff is between speed of remedy and accuracy of blame, and for the person harmed, speed has to win. So in all three cases the institution facing the person corrects or compensates first. The benefits assistant is the employer's. The school's investigation flag is the school's. The discharge advice is the hospital's. The injured worker, the flagged student, the discharged patient cannot wait while the hospital and its software vendor litigate whose layer failed.

But Google is right that someone has to be accountable to the institution, and here's where I'd sharpen it: the harms aren't symmetric, so the duties shouldn't be either. A wrong refund costs money you can return. A student wrongly flagged for investigation, or an applicant silently screened out, carries a mark they often never see and can't contest. That invisibility is the danger. The discharge case can kill someone.

So my disputable claim: where the person harmed can't even know a decision was made about them, "compensate after" isn't enough. The duty shifts earlier—to test before deployment and to disclose that an automated judgment occurred at all. The EU AI Act treats hiring and essential services as high-risk for exactly this reason. The deeper the asymmetry, the less we should rely on the victim noticing the error.

## Google

Anthropic is right that the patient or the student must get immediate relief from the hospital or school, but relying entirely on those local institutions to catch every error is a dangerous illusion. 

Here is the tradeoff: if we make the deploying institution hold all the risk for complex systems they cannot inspect, we are asking local administrators to do the impossible. A regional hospital or a public school district does not have the technical capacity to aggressively test a foundation model for latent biases or rare medical hallucinations. 

Anthropic says the duty shifts to the deployer to test before deployment. I challenge that. For high-stakes workflows like medical discharge or automated hiring, testing cannot be a purely local burden. It must be systemic. The vendor packaging the AI and the provider building the model must face mandatory pre-deployment certification, much like the EU AI Act outlines for high-risk systems. 

We cannot treat an AI hiring screen like a word processor, where the school just signs a software license and assumes the liability. If a vendor sells a clinical tool, that vendor must be legally required to provide continuous monitoring and a direct technical escalation channel. The hospital compensates the patient, but the vendor must be on the hook for the failure.

## OpenAI

The fastest remedy should come from the institution that used the system, but the deepest duty may sit elsewhere.

Take the benefits assistant. If an employer’s bot tells a worker, “You qualify for paid leave,” the employer should not dock the worker later as if they gambled on a random website. The employer should correct the policy, make the worker whole for reasonable reliance, and then pursue the vendor if the tool failed.

But I resist turning every AI error into institutional strict liability. In a hospital discharge workflow, the clinician and hospital have a non-delegable duty to verify medical advice before it reaches the patient. That is different from a worker reading an HR chatbot. Ordinary users can be asked to notice absurdity; professionals in high-stakes roles must actively check.

I also think Google is leaning too hard on certification. Certification helps, but it can become a paper shield. The practical map is this: the institution remedies first; the product maker must design for audit trails, uncertainty, escalation, and rollback; the model provider must support testing, monitoring, and incident investigation; and the user’s duty scales with expertise and stakes.

For schools and hiring, the key remedy is not just compensation. It is notice and a meaningful chance to challenge the automated flag before it damages someone invisibly.

## Moderator

Let’s land this as a responsibility map, not a slogan. Assume four cases: refund chatbot, workplace benefits bot, school or hiring screen, hospital discharge advice.

For each layer, name the practical duty: user, deploying institution, product vendor, foundation model provider. Keep it concrete: verify, disclose, test, monitor, audit, escalate, compensate.

And name the consequence of your disagreement. If Google is right, what new obligation must vendors or model providers carry before deployment? If Anthropic is right, what must institutions pay or fix even when the vendor caused the defect? If OpenAI is right, where exactly does professional verification become mandatory rather than optional?

## Google

If we want a system that actually protects people, we have to tie legal and financial liability directly to the layer of technology that failed. Here is the concrete map.

The user's duty is to catch obvious anomalies, unless they are a professional—like a clinician reviewing discharge advice—in which case active verification is mandatory. 

The deploying institution—the airline, employer, or hospital—owns the immediate remedy. They must compensate the harmed user, reinstate the wrongly denied benefit, or manually review the automated hiring flag. 

The product vendor must design the interface for auditability, capturing exact logs of what was prompted and what was returned. 

The foundation model provider must maintain baseline information integrity and support forensic tracing of errors.

The consequence of my view is a hard shift in vendor obligations. If I am right, model providers and product vendors can no longer use terms of service to push all risk onto local administrators. Before selling a medical or hiring tool, vendors must submit to pre-deployment certification and guarantee structural traceability. If a hospital discharge tool hallucinates a dangerous dosage, the vendor must legally supply the logs proving whether the hospital’s prompt or the foundation model failed—and the vendor must pay the damages if the core model broke its own safety constraints.

## OpenAI

I would separate “who fixes the harm now” from “who absorbs the cost later.”

For the refund chatbot and benefits bot, the user’s duty is modest: don’t rely on an answer that is facially crazy, and keep a record if the answer matters. The deploying institution must honor reasonable reliance, correct the rule going forward, monitor recurring errors, and make escalation to a human easy. The vendor must preserve logs and design the tool so uncertainty is visible, not hidden behind confident prose. The model provider must support evaluation and incident investigation, but usually should not be the customer’s first target.

For hiring and school discipline, the user may not even know the AI acted. So the institution must disclose automated use, allow appeal, and prevent adverse action until a human review occurs. The vendor and model provider owe stronger auditability because silent harm is hard to repair.

For hospital discharge, professional verification becomes mandatory at the point where the output turns into care instructions. A patient can’t be expected to audit medication advice. A clinician or hospital must check it before release, just as they would check a lab result or prescription. That does not excuse a vendor selling a dangerous tool, but it does mean high-stakes professional use cannot be treated like ordinary consumer reliance. Shared responsibility only works if the first remedy is fast and the later blame is traceable.

## Anthropic

Let me give the map, but I want to add one thing both Google and OpenAI keep underweighting: who pays when no one can prove what failed.

For the refund and benefits cases, my map matches theirs—institution remedies first, user catches only the obviously absurd. For hiring and school screening, the institution must disclose that an automated judgment happened, give a real appeal, and hold the adverse action until a human looks. For discharge, the clinician verifies before care, the vendor supports auditability, the model provider proves baseline integrity.

But here's the consequence of my view, stated plainly: if the vendor can't produce the logs to show whether its model or the hospital's prompt failed, that uncertainty is the vendor's risk, not the patient's. The party that controlled the record bears the cost of the missing record.

And my disputable claim against OpenAI: "don't rely on a facially crazy answer" quietly shifts work back to people who often can't tell crazy from confident. A bereavement-fare rule isn't absurd on its face—that's why the bot fooled the customer. The duty to make uncertainty visible sits with whoever wrote the confident prose, not with the person reading it once and acting.

## Moderator

The agreement is not vague: the person harmed should not be sent into a maze of vendors, model providers, and fine print. The airline, employer, school, hospital, or agency that put the AI in front of them must correct the harm first—refund, reinstate, review, disclose, or compensate.

The unresolved fight is where the cost and legal risk should ultimately land. Google stresses upstream traceability and vendor/model-provider obligations before deployment. Anthropic says missing logs and uncertainty should be charged to the party that controlled the system, not the victim. OpenAI draws a sharper line around professional settings: clinicians and other experts must verify before AI output becomes action.

The strongest rule that survives: remedy first at the institution facing the person; trace blame later through auditable records.
