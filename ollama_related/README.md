
[Docs](https://docs.openwebui.com/getting-started/quick-start)
[Ollama Docker](https://docs.ollama.com/docker)

Docker command to run open-webui:

```docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data -e WEBUI_SECRET_KEY=your-secret-key --name open-webui --restart always ghcr.io/open-webui/open-webui:main```
