import httpx

def fetch_url(url: str) -> str:
    """This probably should be updated."""
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
    

# let's test it out
if __name__ == "__main__":
    url = "https://www.example.com"
    content = fetch_url(url)
    import re
    print(re.search(r"<h1>(.*?)</h1>", content).group(1))