import click
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

@click.group()
def cli():
    """AegisNet CLI — Secure AI Infrastructure Control."""
    pass

@cli.command()
@click.argument("prompt")
@click.option("--model", help="Target model (e.g., local/llama3)")
@click.option("--key", envvar="AEGIS_API_KEY", help="AegisNet API Key")
def chat(prompt, model, key):
    """Send a chat request to AegisNet."""
    if not key:
        click.echo("Error: API Key must be provided via --key or AEGIS_API_KEY environment variable.", err=True)
        sys.exit(1)

    headers = {"Authorization": f"Bearer {key}"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "routing_strategy": "auto"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        click.echo(f"\n[AegisNet - {data['metadata']['model']}]")
        click.echo("-" * 40)
        click.echo(data["content"])
        click.echo("-" * 40)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option("--key", envvar="AEGIS_API_KEY", help="AegisNet API Key")
def metrics(key):
    """View live system metrics."""
    headers = {"Authorization": f"Bearer {key}"}
    try:
        response = requests.get(f"{BASE_URL}/api/v1/analytics", headers=headers)
        response.raise_for_status()
        click.echo(json.dumps(response.json(), indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()
