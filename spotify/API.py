from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_music():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    print(f"🎧 Received URL: {url}")
    # כאן בהמשך תשולב ההורדה בפועל
    return jsonify({"status": "received", "url": url}), 200


@app.route("/", methods=['GET'])
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>YouTube Music Downloader</title>
    </head>
    <body>
        <h2>🎧 YouTube Music Downloader</h2>
        <p>Paste a YouTube URL below and click Download:</p>
        <input type="text" id="url" placeholder="https://www.youtube.com/..." size="60">
        <button onclick="download()">Download</button>
        <pre id="response" style="margin-top:20px; background:#eee; padding:10px;"></pre>

        <script>
            function download() {
                const url = document.getElementById('url').value;
                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                })
                .catch(err => {
                    document.getElementById('response').textContent = "❌ Error: " + err;
                });
            }
        </script>
    </body>
    </html>
    """


if __name__ == '__main__':
    app.run(port=5000)
