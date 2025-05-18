# ollama-remote-models

ollama-remote-models is a lightweight Python-based tool designed to scrape model metadata from the Ollama model [search](https://ollama.com/search) page. It extracts key details such as model names and parameter sizes. The tool outputs the collected data in either JSON or Markdown format, making it easy to integrate with documentation, dashboards, or automation scripts. Users can optionally filter the results by model name or parameter size to focus on specific subsets of interest. This utility is ideal for researchers, developers, or enthusiasts looking to explore and analyze the remote Ollama model catalog.

Print remote Ollama models as JSON, sorted by name:

```bash
ollama_scraper.py
```

Print remote Ollama models as JSON, sorted by update time:

```bash
ollama_scraper.py --sort time
```

Print remote Ollama models that have llama3 in their name, sorted by name:

```bash
ollama_scraper.py --filter=llama3
```

Print remote Ollama models that have llama3 in their name, sorted by last update time:

```bash
ollama_scraper.py --filter=llama3 --sort=time
```
