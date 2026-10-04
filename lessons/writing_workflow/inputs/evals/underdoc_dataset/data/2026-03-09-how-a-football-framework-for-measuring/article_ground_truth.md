# How a Football Framework for Measuring Performance Works For Other Industries

*How you can apply this to healthcare, business or any other industry*

I used to think starting a data project was about jumping straight to the data, looking at what’s available and drawing conclusions.

That led to dashboards and models nobody used or cared.

Then last week in the Twelve Football Context Engineering course, I realized how the concept behind the framework for measuring team and player performance they teach could be used for solving problems in other areas.

#### Asking questions first, then data

I’ve been taking this course for the past two weeks and the knowledge compounds incrementally from one week to another. The goal is to create a project around qualities, metrics, pitch visuals and time series approach that they emphasize at Twelve.

Their framework starts with a simple instruction:

**Start with football. Not data.**

The first step is asking a human question like “what you are trying to answer and for whom?”.

What insight can you bring that no-one else has brought before?

An initial question might be: _What makes a good midfielder?_ or _What makes a team dangerous in defensive transitions?_

Once you’ve answered that in plain football language you move to the data. The idea is to build _Qualities →_ composite scores that capture a specific aspect of player or team performance.

You choose 3 to 10 metrics that capture different aspects of the concept. Assign weights based on how important each one is to the original definition. Compute scores using z-scores and compare each player against the right group.

That last part is highly important.

For example when building a _Passing Quality_ score for midfielders, you can end up with five metrics: Passes (xT), Passes into the final third (xT), Passes in the final third (xT), Crosses (xT), and Creative passes weighted at 30%, 20%, 20%, 20%, and 10% respectively. The result is a single score that tells you how threatening a midfielder’s passing is.

Example for Kevin De Bruyne in PL 2022/2023 season

In this image you can see Belgian player Kevin De Bruyne scores near the top but the framework also tells you _why_, and which specific dimension he excels at versus where he’s merely good compared to other players.

That’s the useful part.

#### Context is everything

> _“Metrics are meaningless without context. Choosing the correct comparison group is essential.”_

The comparison group (position, age, league, minutes played) is where we need to emphasize the analysis. Posing the problem and thinking clearly about it before writing the first line of code.

For example a midfielder with high progressive passes has a different meaning than an attacking midfield who sits deep in the field.

A 25 y/o player that has an elevated duel success rate has a different interpretation than a 32 y/o player in the same league.

To produce accurate insights, we need to use the same comparison pool of players.

#### How you can use it in other industries

Take diabetic patient monitoring. A case I’ve been actively working on in my day job.

The human question becomes: _How well is this patient managing their blood sugar?_

You define it in clinical terms first, consistent glucose levels, avoiding dangerous highs and lows, showing improvement over time. Then you look at what you can measure: HbA1c, time above range, time below range, trend direction, glucose variability.

You weight them by clinical importance to finally compare against patients of similar age, diabetes type, and diagnosis duration.

The output is a sentence a physician can actually use:

> _“This patient’s glycemic control is below average for their profile, but trending in the right direction over the last six months. The main challenge is post-meal spikes, not overnight lows.”_

The focus is on turning data into a decision.

You could also apply this template for industries like customer churn in SaaS or credit risk in finance, by always starting with a human question.

#### Key Takeaways

The best analytical frameworks are domain-agnostic. They travel between industries.

Start with the human question by defining the concept before you open the dataset, choosing your comparison group deliberately, then let the data answer.

The framework already exists in your field and most people just never look outside their own.

[Share The Underdoc](https://ricardoheredia.substack.com/?utm_source=substack&utm_medium=email&utm_content=share&action=share)

Thanks for reading one more time.

Till next time,

Ricardo.
