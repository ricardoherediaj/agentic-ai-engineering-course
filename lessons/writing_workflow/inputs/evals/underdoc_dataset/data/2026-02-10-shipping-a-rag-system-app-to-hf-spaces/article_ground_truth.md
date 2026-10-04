# Shipping a RAG System App to HF Spaces with Gradio

*Building the GUI for the end user and next steps to scale this*

This is the last article from the series: [Building a RAG System That Generates Football Post-Match Tactical Reports Automatically](https://substack.com/@theunderdoc/p-182493528)

In previous articles we’ve covered:

- Engineering the data pipeline: [RAG is a Data Engineering Heavy Problem: Building a Football ETL for AI](https://ricardoheredia.substack.com/p/rag-is-a-data-engineering-heavy-problem?r=56fjux)

- Evaluating the prompt and system outputs with EDD: [From Vibes to Metrics: How I Evaluated A Football RAG System](https://ricardoheredia.substack.com/p/from-vibes-to-metrics-how-i-evaluated)

Today I’ll be talking about the challenges of designing a user interface to interact with in an effort to make it as comfortable as possible.

This marks the end of these series on how I’ve built this MVP, which I’m scaling into an automated data platform that generates football post match reports and can run on your own computer.

You can find the entire code on the GitHub repository and the new releases: [Football RAG Intelligence](https://github.com/ricardoherediaj/football-rag-intelligence)

### What’s Gradio and Why I Chose it

If you haven’t heard of it already, Gradio is an open-source Python framework that allows developers to quickly build and deploy interactive web interfaces for ML models and data pipelines.

In the context of the Football RAG platform, I used it as a lightweight presentation layer to connect the user to all the backend logic (pipelines, LLM orchestration).

At this stage of development, the goal was to keep it simple. I chose Gradio over Streamlit for these reasons:

- Avoid rerunning the script each time there’s retrieval.

- **API capabilities**: Gradio automatically generates a REST API for your interface, making it easier to treat the UI as modular rather than a monolith.

- **LLM Integration**: Gradio’s `ChatInterface` component is purpose-built for the conversational nature of RAG, allowing me to focus on promptoptimization rather than building widgets.

- **Fast iteration**: working with 108 matches, it allowed for a full database rebuild and UI refresh in seconds.

Although in the future I could move to another frontend, this was enough to validate the idea.

### HuggingFace Spaces Deployment

The simplest way to host an AI/ML demo without becoming a full-time DevOps engineer was a using HuggingFace Spaces.

It’s basically a managed hosting service where you can drop your Gradio app.

Some characteristics:

- **GitHub-Style Deployment:** You push your code to a repository, and Spaces automatically builds the container and serves the app to a public URL.

- **Seamless Integration:** Since it’s natively built for the ecosystem, it handles the Gradio environment and Python dependencies out of the box.

- **Free Tier:** It provided the perfect “sandbox” for the MVP, giving me a URL to share it publicly using generous CPU compute.

#### A Reality Check: MVP vs. Production

Grado helped to build the UI easily, but making it "industrial-grade" meant facing a few technical issues.

##### 1\. Deployment Binary Bug

I hit a snag where the specific binaries for my vector store behaved differently on Mac vs. the Linux environment in Spaces.

Standardizing with **uv** and clean lockfiles was the way out.

##### 2\. The $0 Intent Routing Trick:

Saving tokens was necessary from the beginning, so I built a **Smart Router**:

- **Questions** like “How did this team play?” or “Why did this team had X metric during that match?” → It goes to the LLM for tactical analysis.

- **Visualization commands** like “Show passing network plot from the match” → These bypass the LLM and trigger my Matplotlib visualizers at zero cost.

##### The "Airlock" ETL

Talked about this in previous matches but decoupling the ingestion from the UI helped me caught data bugs like a "Home/Away swap" that was messing up team stats before they reached the user.

Here’s how the frontend looks for now in HF Spaces:

### Lesson Learned

The biggest takeaway from building this GUI and deploying the MVP is:

**90% is Data Engineering, and the AI part is just the tip.**

You need to provide a well crafted plumbing so the system does meaningful retrieval and the user, through a comfortable UI can obtain valuable information.

Precalculating everything (compute 38 tactical metrics during ETL) helps for instant retrieval.

Validate with data contracts before moving the data forward (Pydantic)

Keeping it simple for the GUI, for quick adoption.

Final Architecture

### What’s Next?

Now that the demo is live and the concept is validated, I’m scaling from 108 matches to 1,000+.

I’ll be documenting that journey. In the next series we’re talking about moving to a proper infrastructure:

- **MinIO** for object storage (S3-compatible, runs locally)

- Dagster orchestrating the pipelines

- dbt + DuckDB handling the analytical workloads.

- Everything on-premise with Docker services

- Modal free tier for serverless LLM inference on cloud GPU **s.**

The goal:

> An automated data platform that generates post-match tactical reports for any match, running entirely on your own machine, with cheap cloud costs for the heavy lifting.

If you’ve been following along, you now have a blueprint for building a working RAG system with documented engineering decisions.

The next series starts soon.

If there’s a specific part of the architecture you want me to dig deeper into, please let me know in the comments.

* * *

**Check out the code:** [Football RAG Intelligence GitHub Repository](https://ricardoheredia.substack.com/p/link)

**Try the live demo:** [HuggingFace Spaces](https://ricardoheredia.substack.com/p/link)
