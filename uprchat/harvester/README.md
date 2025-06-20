## How to Run a Recollection

To perform a recollection process, use the `poetry run` command followed by one of the available scripts described below.

### Available Scripts

- **`simple-recollection`**  
  Executes a basic recollection. It does not generate summaries or extract entities. It only adds representations to the graph as either *page* or *document* nodes and saves the output to a specific file.  
  ⚠️ *Does not rely on external models.*

- **`summary-creation-recollection`**  
  Performs a recollection that includes generating a summary field for each source node. It can be used after a simple recollection to enrich nodes with summaries.  
  ⚠️ *Requires access to a language model.*

- **`entity-extraction-recollection`**  
  Extracts entities from each node and links them to their originating *page* or *document* node. Useful to enhance previously collected data that lacks entity information.  
  ⚠️ *Requires access to a language model.*

- **`complete-recollection`**  
  Executes a full recollection process: both summary generation and entity extraction. Ideal for starting from scratch when models are available.  
  ⚠️ *Requires access to external models.*

---

### ⚙️ Command-Line Parameters

The following parameters can be passed when running a recollection script:

- **`URL`** (required)  
  Specifies the starting point of the recollection process.  
  **Example:**
  ```
  poetry run simple-recollection www.upr.edu.cu
  ```
- **`Recollection`** --recollection / -r (optional)
    Assigns a unique identifier to the recollection run. Defaults to 0.
    Example:
    ```
    poetry run simple-recollection www.upr.edu.cu -r first
    ```
- **`Delay`** --delay / -d (optional)
    Sets the waiting time (in seconds) between requests sent to the model. Defaults to 60.
    Example:
        ```
        poetry run simple-recollection www.upr.edu.cu -d 1
        ```
✅ Recommended Workflow

For step-by-step execution, it's recommended to run the scripts in the following order:

1 - simple-recollection

2 - summary-creation-recollection

3 - entity-extraction-recollection

However, if you have access to the necessary models from the start, you can simplify the process by running complete-recollection