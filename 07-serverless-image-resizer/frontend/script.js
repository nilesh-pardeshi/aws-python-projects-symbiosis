const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");

const originalImage = document.getElementById("originalImage");
const resizedImage = document.getElementById("resizedImage");

const originalSize = document.getElementById("originalSize");
const resizedSize = document.getElementById("resizedSize");
const compression = document.getElementById("compression");
const progressBar = document.getElementById("progressBar");

const statOriginal = document.getElementById("statOriginal");
const statCompressed = document.getElementById("statCompressed");
const statPercent = document.getElementById("statPercent");

const status = document.getElementById("status");

const API =
"https://2uzzpwhd26.execute-api.ap-south-1.amazonaws.com/upload-url";

uploadBtn.onclick = async () => {

    if (fileInput.files.length === 0) {
        alert("Choose an image");
        return;
    }

    const file = fileInput.files[0];

    // Show original image
    originalImage.src = URL.createObjectURL(file);

    // Reset UI
    resizedImage.src = "";
    resizedSize.innerHTML = "";
    compression.innerHTML = "";

    // Show original size
    if (file.size >= 1024 * 1024) {

        originalSize.innerHTML =
            "Size : " + (file.size / (1024 * 1024)).toFixed(2) + " MB";

    } else {

        originalSize.innerHTML =
            "Size : " + (file.size / 1024).toFixed(2) + " KB";
    }

    status.innerHTML = "Getting Upload URL...";

    console.log("File Name:", file.name);
console.log("File Type:", file.type);
console.log("File Size:", file.size);
    try {

        const response = await fetch(API);
        const data = await response.json();

        const uploadURL = data.uploadURL;
        const fileName = data.fileName;

        status.innerHTML = "Uploading Image...";
        await fetch(uploadURL, {
            method: "PUT",
            headers: {
                "Content-Type": file.type
            },
            body: file
        });

        status.innerHTML = "Image Uploaded ✔";

        waitForResized(fileName, file.size);

    } catch (err) {

        console.error(err);
        status.innerHTML = "Upload Failed ❌";

    }

};

async function waitForResized(fileName, originalBytes) {

    status.innerHTML = "Waiting for Lambda...";

    const imageURL =
    "https://nilesh-image-output-2026.s3.ap-south-1.amazonaws.com/resized/" +
    fileName;

    let attempts = 0;

    const timer = setInterval(() => {

        attempts++;

        const img = new Image();

        img.onload = async () => {

            clearInterval(timer);

            resizedImage.src =
            imageURL + "?" + Date.now();

            try {

                const head = await fetch(imageURL, {
                    method: "HEAD"
                });

                const bytes =
                Number(head.headers.get("content-length"));

                if (bytes >= 1024 * 1024) {

                    resizedSize.innerHTML =
                    "Size : " +
                    (bytes / (1024 * 1024)).toFixed(2) +
                    " MB";

                } else {

                    resizedSize.innerHTML =
                    "Size : " +
                    (bytes / 1024).toFixed(2) +
                    " KB";

                }

                const percent =
                ((originalBytes - bytes) / originalBytes) * 100;

                compression.innerHTML =
                "Compression : " +
                percent.toFixed(1) + "%";

            } catch {

                resizedSize.innerHTML = "";
                compression.innerHTML = "";

            }

            status.innerHTML = "Resize Completed ✔";

        };

        img.onerror = () => {

            if (attempts > 30) {

                clearInterval(timer);

                status.innerHTML = "Timeout ❌";

            }

        };

        img.src =
        imageURL + "?" + Date.now();

    }, 2000);

}