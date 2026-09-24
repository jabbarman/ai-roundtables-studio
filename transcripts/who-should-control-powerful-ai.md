---
title: Who Should Control Powerful AI?
date: 2026-08-27
source_run: runs/raw/who-should-control-powerful-ai-001
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
# Who Should Control Powerful AI?

## Moderator

A company is about to release a much stronger general-purpose AI. It can carry out long chains of online tasks and is especially good at finding software vulnerabilities. That helps defenders, but internal tests show safeguards can be bypassed. A rival may release soon. Government testers rely on voluntary access. Outside researchers cannot fully inspect it. Customers are already building plans around it.

Here is the dispute: technical control sits with the lab, but public risk is not only the lab’s property. So who has lawful authority to delay this release for 90 days: the company, a government agency, an independent evaluator, a court, or no one? Pick one.

## OpenAI

A government agency should have the legal authority to impose the 90-day delay, but only under a narrow, risk-based rule set in advance.

The lab has the operational knowledge, so it should decide ordinary release details: mitigations, staged rollout, monitoring, customer terms. But when the question is whether the public must accept a contested systemic risk, the lab should not be judge in its own case. A rival being close to release is relevant commercially, not decisive publicly.

The agency’s authority should be triggered by specific evidence: unusually strong cyber capability, demonstrated safeguard bypasses, credible paths to misuse, and inadequate monitoring or containment. The lab should have to disclose the safety case, evaluation results, incident plans, and mitigation limits to qualified government and independent evaluators under confidentiality. Not to the whole internet, because publishing exploit-relevant details could increase the very risk at issue.

Independent evaluators should not themselves stop deployment. They supply adversarial evidence and reduce internal bias, which NIST and the UK AI Security Institute both emphasize. But they are not democratically accountable. Courts should provide fast review: did the agency apply the legal test, rely on evidence, and avoid arbitrary or protectionist delay?

So my answer is: government can pause; labs must evidence; evaluators test; courts police abuse. Markets and users do not get to vote with deployment after the harm may already be irreversible.

## Anthropic

The government agency should hold the delay authority, and I'll add the piece OpenAI left too soft: voluntary access is not a foundation you can build on.

In this scenario the government tests "rely on voluntary access." That means the lab controls whether the state can even see the risk it's being asked to judge. That's not oversight; it's a courtesy the lab can withdraw the moment findings turn inconvenient. So the trigger can't just be evidence the lab volunteers. Access itself must be mandatory above a capability threshold—the pre-release evaluation, the safeguard-bypass results, the incident-reporting duty. The EU AI Act's systemic-risk tier already points this way: for the most capable models, evaluation and incident reporting are obligations, not favors.

Here's where I'll push OpenAI. You said the rival being close is "commercially relevant, not decisive." Agreed—but that means the rule must apply to the rival too, or the responsible lab is simply punished for cooperating. A delay power that only bites the company that discloses honestly is worse than no power at all.

One claim others may dispute: with capabilities this irreversible—effective vulnerability discovery, safeguards known to fail—the burden should sit on the lab to show release is safe, not on the public to prove it dangerous.

## Google

The problem with handing a veto to a single national agency is that AI development does not happen in a single jurisdiction.

Anthropic correctly notes that a delay must apply to rivals, but a national agency has no authority over a foreign competitor. If a domestic regulator pauses this release for 90 days, and a lab operating under a more permissive regime deploys a comparable model on day ten, the public is exposed to the exact same cyber vulnerability risk. The only difference is that the compliant company loses its market position.

A purely national delay power is an illusion of control. Any binding pause for systemic risk requires cross-border coordination based on shared, interoperable standards, building on the groundwork of bodies like the OECD or the UN scientific panel.

Furthermore, treating a general-purpose model as a monolith to be either paused or released ignores how it is used. If the specific risk is automated software exploitation, the targeted intervention is to restrict how the model integrates with sensitive network tools, not to embargo the entire system. A single national gatekeeper tasked with holding up general-purpose models will inevitably become a bottleneck, delaying beneficial downstream uses while utterly failing to contain globally distributed risks.

## Moderator

Google, that risks becoming an argument for no one having authority until international law catches up. So be concrete: tomorrow morning, before any OECD or UN mechanism can bind anyone, can the national agency stop this release or not?

And to OpenAI and Anthropic: answer Google’s strongest objection. If your pause only binds the cooperative domestic lab, have you made the world safer or just shifted the market?

Now add two stress tests. First: the agency is captured by the incumbent and uses “safety” to block a smaller open-model developer. Second: an authoritarian government demands full model access in the name of evaluation. What rule prevents both abuses?

## Anthropic

Yes—tomorrow morning, before any treaty exists, the national agency can and should stop the domestic release. Google is describing a real leak, not a reason to do nothing. If your only move is a national one, you make a national one, and you use it as leverage: condition market access on the rival meeting the same evidence bar. The EU already does this—sell into the market, meet the systemic-risk obligations. That reaches the foreign lab through its customers, not its jurisdiction.

Have I just shifted the market? Partly, yes—and that's why the delay must attach to deployment into your territory, not to which flag the developer flies under. Same capability, same threshold, same duty to disclose.

Now the two abuses, because they need different cures. Capture: the rule must be capability-triggered, not size-triggered, with published thresholds and fast court review. A smaller open-model developer below the threshold is simply outside the regime—the agency has no lever to pull. Authoritarian access-grab: separate the two things people keep merging. Evaluation needs behavioral testing and safeguard results under confidentiality—not the weights, not the training data. A government demanding the full model "to evaluate" is demanding the capability itself. That's the tell. Mandatory access, narrowly scoped, is the safeguard against both.

## Google

Tomorrow morning, the national agency can halt the release, but their authority must be limited to restricting specific, high-risk deployments, not embargoing the base model entirely.

Anthropic argues we can manage foreign rivals by conditioning market access, pointing to the EU AI Act. But market rules do not contain cyber capabilities. If a foreign lab releases a model that excels at finding software vulnerabilities, malicious actors will access it regardless of whether it is legally sold in our jurisdiction. A domestic pause in that scenario only paralyzes our own defensive developers who need the model to patch those very vulnerabilities.

To prevent the agency from being captured by incumbents to crush smaller open-model developers, the delay trigger cannot just be a theoretical capability score. It must require proof of downstream harm—a demonstrated safeguard bypass in a realistic setting.

As for the authoritarian access-grab, Anthropic is right that evaluating behavior does not require handing over model weights. But we must go further. An agency cannot justify a pause using secret criteria. Relying on shared, public evaluation standards—like the NIST AI Risk Management Framework—ensures courts can verify if a delay is based on genuine safety science or political pretext. If the agency cannot publicly defend the standard it applied, it has no authority to pause the release.

## OpenAI

A domestic pause can make the world safer if it controls access to the domestic market and buys time for mitigations, but Google is right that it cannot be treated as containment of the planet.

That is why the pause should be paired with two narrower tools: first, market-access rules for any provider serving local users; second, deployment conditions aimed at the risky capability, such as limits on autonomous vulnerability chaining, tool access, rate limits, logging, and vetted security-research channels. I disagree with Google that the base model should never be paused. If the risky capability is inseparable from ordinary access, a model-level delay is sometimes the least bad option.

On capture: the agency should not be able to say “small open model, therefore dangerous” or “incumbent model, therefore safe.” The trigger should be capability plus realistic misuse evidence plus failed mitigations. The public version of the decision should state that reasoning, while sensitive exploit details go to courts and accredited evaluators. That gives challengers something to contest without publishing a misuse manual.

On authoritarian demands: evaluation access is not ownership access. No automatic handover of weights, training data, or unrestricted system access. Use secure testing environments, audited queries, and independent evaluators. If a state demands the capability itself, the lab should be legally permitted, even required, to refuse.

A false alarm is handled by fast review and compensation or sunset: the pause expires unless the agency renews it with fresh evidence.

## Moderator

Here is the live disagreement: OpenAI and Anthropic allow a model-level pause when capability and failed safeguards create systemic risk; Google wants narrower restrictions unless real downstream harm is shown. That difference matters tomorrow.

So give me your final rule in operational terms. In this case, who is stopped: the base model, particular tool uses, certain customers, or no one? What evidence must the lab disclose, to whom, before release? Who can see confidential exploit-relevant details? Who hears the appeal, and how fast? And name the cost of your rule: slower defensive use, more public risk, more state power, or more private control.

## Google

The national agency can restrict specific, high-risk integrations of the model, but it cannot embargo the base model itself. We stop the model from connecting to autonomous execution tools or unvetted networks, but we do not stop the model's release to developers who need it for defensive cybersecurity.

Before release, the lab must disclose its internal capability evaluations and safeguard-bypass results to the agency and to accredited independent evaluators working against public standards such as the NIST AI Risk Management Framework. Sensitive exploit details must remain in secure, lab-hosted testing environments. Evaluators and agency staff query the system there, rather than taking possession of the underlying data or the model weights.

An administrative court must hear any appeal within fourteen days, judging strictly whether the agency's deployment restriction matches a published, internationally recognized standard of risk. If the agency relies on secret criteria, the restriction is lifted.

The tradeoff here is real: this rule limits the state's power to completely block a technology. We accept a higher risk that malicious actors might eventually bypass our deployment restrictions, in exchange for ensuring our domestic defensive developers are not left disarmed against foreign cyber threats. Attempting to lock down the base model entirely just cedes the timeline to rivals operating in jurisdictions that will not wait for us.

## OpenAI

My rule is broader than Google’s because some capabilities are not safely separable at the tool layer.

In this case, the agency may impose a 90-day model-level pause if three facts are present together: the model substantially improves autonomous vulnerability discovery; safeguards are bypassed in realistic tests; and the lab cannot show that deployment controls will reliably prevent misuse at scale. If those facts are not all present, the agency should use narrower conditions: no autonomous network access, strict rate limits, logging, vetted security users, and staged release.

Before release, the lab must disclose its safety case, capability evaluations, red-team results, known safeguard failures, proposed mitigations, monitoring plan, and incident-response procedures. The agency and accredited independent evaluators can see confidential exploit-relevant details in secure environments. Courts can review the full record under seal. The public gets a non-sensitive explanation of the decision and the standard applied.

Appeal should go to a specialized administrative court within fourteen days. The pause expires at 90 days unless renewed with fresh evidence, and renewal should require a higher showing.

The cost of my rule is more state power and slower defensive use. I accept that cost because a tool-only restriction is too weak when ordinary access already enables harmful cyber workflows.

## Anthropic

My rule sits closer to OpenAI's, but I want to be blunt about the split with Google, because it's the whole disagreement.

Google's rule says: no model-level pause without demonstrated downstream harm. In this scenario that means we wait for the first real-world exploitation before we're allowed to act on capabilities we already measured. For irreversible harms—working vulnerability discovery, safeguards known to fail—that's the wrong default. You don't require a breach before you're permitted to lock the door.

So: the agency may pause the base model when capability, realistic safeguard bypass, and inadequate controls all hold. Same threshold for the rival, enforced through market access. Disclosure before release is mandatory, not voluntary—safety case, red-team results, known failures—to the agency and accredited evaluators in secure environments, never weights or training data to any state. Appeal to a specialized court in fourteen days; pause sunsets at 90 unless renewed on a higher bar.

Now name my cost honestly, since Google keeps hinting at it: I am giving a government real power to slow a beneficial technology, and that power can be abused. I accept it because the alternative—firms setting society's risk tolerance because they moved first—is the larger and less legitimate concentration of power.

## Moderator

The agreement is not trivial: none of the participants thinks the lab alone should decide public risk, and none trusts voluntary access as sufficient. All accept mandatory pre-release disclosure to a public authority and accredited evaluators, secure handling of exploit-relevant details, no automatic handover of weights, fast court review, and time-limited action.

The unresolved fight is over the base model. Google would restrict dangerous deployments and tool integrations unless real-world harm is shown. OpenAI and Anthropic would allow a 90-day model-level pause when strong cyber capability, realistic safeguard bypass, and inadequate controls appear together.

The strongest rule that survived is risk-tiered authority: labs provide evidence, independent evaluators test, governments can impose proportionate conditions or pauses, courts review quickly, and every restriction must expire unless renewed with fresh evidence.
