## Question 1: Context Engineering

Try the following experiment:

1. Open ChatGPT in a private browser window: https://chatgpt.com
2. Enter this prompt: "Create a Kestra flow that loads NYC taxi data from CSV to BigQuery"
3. Then, use Kestra's AI Copilot with the same prompt

After trying the same prompt in ChatGPT vs Kestra's AI Copilot, what is the primary reason AI Copilot generates better Kestra flows?

- AI Copilot uses a more powerful model
- AI Copilot has access to current Kestra plugin documentation
- AI Copilot uses more tokens
- AI Copilot has internet access

## Solution: 

ChatGPT: 

```
id: nyc_taxi_csv_to_bigquery
namespace: company.team

variables:
  project_id: your-gcp-project
  dataset: nyc_taxi
  table: yellow_tripdata
  bucket: your-gcs-bucket

tasks:
  - id: download_csv
    type: io.kestra.plugin.core.http.Download
    uri: https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2023-01.csv.gz

  - id: decompress
    type: io.kestra.plugin.compress.ArchiveDecompress
    from: "{{ outputs.download_csv.uri }}"

  - id: upload_to_gcs
    type: io.kestra.plugin.gcp.gcs.Upload
    serviceAccount: "{{ secret('GCP_SERVICE_ACCOUNT') }}"
    from: "{{ outputs.decompress.files[0] }}"
    bucket: "{{ vars.bucket }}"
    name: yellow_tripdata_2023-01.csv

  - id: load_to_bigquery
    type: io.kestra.plugin.gcp.bigquery.LoadFromGcs
    serviceAccount: "{{ secret('GCP_SERVICE_ACCOUNT') }}"
    projectId: "{{ vars.project_id }}"
    dataset: "{{ vars.dataset }}"
    table: "{{ vars.table }}"
    from:
      - "gs://{{ vars.bucket }}/yellow_tripdata_2023-01.csv"
    format: CSV
    autodetect: true
    skipLeadingRows: 1
    writeDisposition: WRITE_TRUNCATE
    createDisposition: CREATE_IF_NEEDED
```

Kestra's AI Copilot: 

```
id: load_nyc_taxi_data
namespace: company.team
tasks:
  - id: load_to_bq
    type: io.kestra.plugin.gcp.bigquery.Load
    from: "kestra://data/nyc_taxi.csv"
    destinationTable: "my_project.nyc_taxi_dataset.trips"
    format: CSV
    csvOptions:
      skipLeadingRows: 1
    writeDisposition: WRITE_APPEND
    createDisposition: CREATE_IF_NEEDED
    autodetect: true
```

**Correct answer - AI Copilot has access to current Kestra plugin documentation.**

## Question 2: RAG vs No RAG

Run both `1_chat_without_rag.yaml` and `2_chat_with_rag.yaml` in the Kestra UI. Read the execution logs for each.

The non-RAG response about Kestra 1.1 features is best described as:

- Accurate and specific, matching the actual release notes
- Vague, generic, or fabricated — the model guesses from training data
- Empty — the model refuses to answer without context
- Identical to the RAG version

```
2026-07-22 22:37:51.036❌ Response WITHOUT RAG (no retrieved context):
Kestra 1.1 was a significant release that focused heavily on enhancing the developer experience, improving performance, and expanding the platform’s security and governance capabilities.
Here are 5 major features introduced in Kestra 1.1:
### 1. Unified Namespace Strategy
Kestra 1.1 introduced a more robust and flexible approach to **Namespaces**. This feature allows organizations to better structure their workflows by grouping them logically. It enables granular control over permissions, configurations, and environment variables, making it significantly easier to manage multi-tenant environments or separate different business units/projects within the same Kestra instance.
### 2. Enhanced UI/UX and Flow Designer
This release brought major improvements to the **Flow Designer**. Key additions included better drag-and-drop functionality, improved visualization of task dependencies, and enhanced "live" debugging capabilities. The UI was refined to make it more intuitive for non-technical users while providing power users with deeper insights into execution logs and task states directly from the canvas.
### 3. Advanced Secret Management Integration
While secrets were supported previously, 1.1 introduced a more streamlined integration with external **Secret Managers** (such as HashiCorp Vault, AWS Secrets Manager, and Google Secret Manager). This allows teams to inject sensitive data (like API keys or database credentials) directly into flows at runtime without ever exposing them in the flow definition files, significantly improving security and compliance.
### 4. Improved Worker Task Queues
Kestra 1.1 overhauled the **Worker architecture** to allow for better resource isolation. Users can now assign specific task types or namespaces to specific Worker groups. This is a major feature for high-scale environments, as it allows administrators to ensure that resource-heavy tasks (like data processing) do not starve lighter tasks (like API calls) of execution capacity.
### 5. Enhanced Audit Logging and Observability
This release expanded Kestra’s **Audit Log capabilities**. It provided a more comprehensive trail of all actions performed within the platform, including who modified a flow, who triggered an execution, and who accessed specific resources. Combined with improved metrics and Prometheus integration, this feature made Kestra much more "enterprise-ready" for organizations with strict auditing requirements.
***
**Bonus Note:** Kestra 1.1 also heavily improved the **plugin ecosystem**, introducing a new way to handle plugin dependencies (the "Plugin Isolation" model), which prevents library conflicts when running multiple plugins that might share dependencies (like different versions of the AWS SDK).
🤔 Did you notice that this response seems to be:
- Incorrect?
- Vague/generic?
- Listing features that haven't been added in exactly this version but rather a long time ago?
👉 This is why context matters! Run `2_chat_with_rag.yaml` to see the accurate, context-grounded response.
```


```
2026-07-22 22:39:40.617✅ RAG Response (with retrieved context):
Kestra 1.1 introduced several new capabilities to enhance usability, automation, and enterprise readiness. Here are 5 major features released in version 1.1:
1. **No-Code Dashboard Editor**: A multi-panel, visual editor that allows you to create and customize dashboards, charts, and visualizations directly from the UI without needing to write YAML.
2. **Human-in-the-Loop Workflows**: Introduced via the `HumanTask` (Enterprise Edition), this allows workflows to pause and wait for manual approval from specific users or groups before proceeding, which is ideal for sensitive operations or validation steps.
3. **Multi-Agent AI Systems**: AI agents can now be configured to use other specialized AI agents as tools, enabling hierarchical orchestration where a primary agent delegates subtasks (such as data analysis or research) to expert agents.
4. **Fix with AI**: A diagnostic feature that analyzes failed task runs and provides AI-powered suggestions to help users quickly identify and resolve workflow issues.
5. **Redesigned Filters**: A complete UI overhaul of filtering across the platform, offering a more intuitive, user-friendly interface that allows users to save filter combinations and easily manipulate table columns.
Additionally, Kestra 1.1 included **dozens of new plugins** (such as Liquibase, dlt, Stripe, and YouTube integrations), **improved air-gapped support** for offline environments, and new **email-based triggers** (`MailReceivedTrigger`).
🎉 Note that this response is detailed, accurate, and grounded in the actual release documentation. Compare this with the output from 1_chat_without_rag.yaml!
```

**Correct answer - Vague, generic, or fabricated — the model guesses from training data**

## Question 3: Token usage — short summary

Run `4_simple_agent.yaml` with `summary_length = short` (leave the other inputs as defaults).

Open the execution logs and find the token usage logged by the `log_token_usage` task.

What is the approximate **output** token count for `multilingual_agent`?

- 5-15 tokens
- 60-100 tokens
- 200-400 tokens
- 500+ tokens

```
2026-07-22 22:46:00.925📊 Token Usage Summary:
Multilingual Agent:
- Input tokens: 282
- Output tokens: 57
- Total tokens: 339
English Brevity Agent:
- Input tokens: 72
- Output tokens: 30
- Total tokens: 102
💡 Tip: Monitor token usage to understand costs and optimize prompts!
```

**Correct answer - 60-100 tokens**

## Question 4: Token usage — long summary

Run `4_simple_agent.yaml` again with `summary_length = long`.

Compare the `multilingual_agent` output token count to your result from Question 3. Roughly how many times more output tokens does the long summary use?

- About the same (within 20%)
- 2-5x more
- 10-20x more
- 50x more

```
2026-07-22 22:51:04.860📊 Token Usage Summary:
Multilingual Agent:
- Input tokens: 282
- Output tokens: 154
- Total tokens: 436
English Brevity Agent:
- Input tokens: 169
- Output tokens: 36
- Total tokens: 205
💡 Tip: Monitor token usage to understand costs and optimize prompts!
```

**Correct answer - 2-5x more**

## Question 5: Modifying a flow

Open `4_simple_agent.yaml` in the Kestra flow editor. Find the `english_brevity` task and change its prompt from asking for exactly **1 sentence** to asking for exactly **3 sentences**.

Save the flow, then run it with `summary_length = long`.

Compare the `english_brevity` output token count to the original 1-sentence version (also with `summary_length = long`). How do they compare?

- About the same (within 20%)
- 2-4x more
- 5-10x more
- 10x+ more

```
2026-07-22 22:55:40.524📊 Token Usage Summary:
Multilingual Agent:
- Input tokens: 282
- Output tokens: 160
- Total tokens: 442
English Brevity Agent:
- Input tokens: 175
- Output tokens: 84
- Total tokens: 259
💡 Tip: Monitor token usage to understand costs and optimize prompts!
```

**Correct answer - 2-4x more**

## Question 6: Best Practices

Based on what you learned in this module, for production workflows requiring deterministic, repeatable results with strict compliance requirements (e.g., financial reporting, workflows in highly regulated industries), which approach is most appropriate?

- Always use AI agents for maximum flexibility and adaptation
- Use traditional task-based workflows for predictability and auditability
- Use only RAG without agents for better performance
- Use web search tools exclusively to ensure current data

**Correct answer - Use traditional task-based workflows for predictability and auditability**