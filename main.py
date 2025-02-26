from flask import Flask, request, render_template, redirect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# Base URL for Google search
SEARCH_ENGINE_URL = "https://www.google.com/search"

@app.route("/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("q")
        return redirect(f"/search?q={query}")  # Redirect to /search

    query = request.args.get("q")
    if not query:
        return render_template("index.html", results=None)

    # Fetch search results from Google
    response = requests.get(f"{SEARCH_ENGINE_URL}?q={query}", headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.startswith("/url?q="):
            full_url = href.split("/url?q=")[1].split("&")[0]  # Extracting the actual URL
            if "google.com" not in full_url:  # Ensure it's not a Google internal link
                proxy_url = f"/proxy?url={full_url}"  # Proxy the links
                title = link.text
                results.append({"title": title, "url": proxy_url})

    return render_template("index.html", results=results, query=query)

@app.route("/proxy")
def proxy():
    # Get the target URL from the query parameter
    target_url = request.args.get("url")
    if not target_url:
        return "No URL provided", 400

    # Fetch the content from the target URL and serve it through the proxy
    try:
        response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Ensure we handle any non-200 status codes
        return response.content  # Return the content fetched from the target URL
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}", 500

@app.route("/search")
def search_redirect():
    query = request.args.get("q")
    if not query:
        return redirect("/")  # If no query, go back to home page

    # Construct the Google search URL with the query
    search_url = f"{SEARCH_ENGINE_URL}?q={query}"

    # Redirect to the proxy with the search URL
    return redirect(f"/proxy?url={search_url}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

