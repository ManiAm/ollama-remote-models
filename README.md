# ollama-remote-models

ollama-remote-models is a lightweight Python-based tool designed to scrape model metadata from the Ollama model [search](https://ollama.com/search) page. It extracts key details such as model names and parameter sizes. This utility is ideal for researchers, developers, or enthusiasts looking to explore and analyze the remote Ollama model catalog. The program supports different output options, making it easy to integrate with documentation, dashboards, or automation scripts.

## Program Options

- `--output`

    Defines the desired output format.
    
    Supported values include json, markdown, and html. The default is json.

- `--sort`

    Determines the sorting criteria for the output.

    Options are name (alphabetical order) and time (last updated). The default is name.

- `--filter`

    Filters the results based on model names, allowing you to narrow the output to specific models of interest.

## Example Usage

Print remote Ollama models as JSON, sorted by name:

```bash
ollama_models.py
```

Print remote Ollama models as JSON, sorted by last update time:

```bash
ollama_models.py --sort time
```

Print remote Ollama models that have llama3 in their name, sorted by name:

```bash
ollama_models.py --filter=llama3
```

Print remote Ollama models that have llama3 in their name, sorted by last update time:

```bash
ollama_models.py --filter=llama3 --sort=time
```
