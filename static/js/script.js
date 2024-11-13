async function sendEmails() {
    const formData = new FormData(document.getElementById("uploadForm"));
    const statusDiv = document.getElementById("status");

    statusDiv.textContent = "Sending emails, please wait...";

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (response.ok) {
            statusDiv.innerHTML = result.status.join("<br>");
        } else {
            statusDiv.textContent = `Error: ${result.error}`;
        }
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
    }
}
