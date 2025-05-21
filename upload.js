// document.addEventListener('DOMContentLoaded', function() {
//     const imageBtn = document.getElementById('image-btn');
//     const videoBtn = document.getElementById('video-btn');
//     const uploadForm = document.getElementById('upload-form');
//     const fileInput = document.getElementById('file');
//     const analyzeBtn = document.getElementById('analyze-btn');
//     const resultDiv = document.getElementById('result');
//     const loadingSpinner = document.getElementById('loading-spinner');
//     const videoFeed = document.getElementById('video-feed');
//     const videoStream = document.getElementById('video-stream');
//     const liveResult = document.getElementById('live-result');

//     let currentMode = null;
//     let isProcessing = false;

//     imageBtn.addEventListener('click', () => setMode('image'));
//     videoBtn.addEventListener('click', () => setMode('video'));

//     function setMode(mode) {
//         currentMode = mode;
//         imageBtn.classList.toggle('btn-primary', mode === 'image');
//         videoBtn.classList.toggle('btn-primary', mode === 'video');

//         fileInput.accept = mode === 'image' 
//             ? '.png,.jpg,.jpeg'
//             : '.mp4,.avi,.mov';

//         uploadForm.style.display = 'block';
//         videoFeed.style.display = 'none';
//         resultDiv.innerHTML = '';
//     }

//     analyzeBtn.addEventListener('click', async (e) => {
//         e.preventDefault();
//         if (!currentMode || !fileInput.files.length) {
//             alert('Please select a file first');
//             return;
//         }

//         const formData = new FormData();
//         formData.append('file', fileInput.files[0]);

//         try {
//             if (currentMode === 'video') {
//                 videoFeed.style.display = 'block';
//                 videoStream.src = '/video_feed';
//                 liveResult.textContent = 'Starting analysis...';
//                 isProcessing = true;
//             }

//             loadingSpinner.style.display = currentMode === 'image' ? 'block' : 'none';
//             resultDiv.innerHTML = '';

//             const response = await fetch(`/upload/${currentMode}`, {
//                 method: 'POST',
//                 body: formData
//             });

//             const data = await response.json();

//             if (data.error) {
//                 throw new Error(data.error);
//             }

//             if (currentMode === 'video') {
//                 isProcessing = false;
//                 videoFeed.style.display = 'none';
//             }

//             resultDiv.innerHTML = `
//                 <div class="alert ${data.prediction === 'Real' ? 'alert-success' : 'alert-danger'}">
//                     <h4>Analysis Results</h4>
//                     <p>Prediction: ${data.prediction}</p>
//                     <p>Confidence: ${(data.confidence * 100).toFixed(2)}%</p>
//                 </div>
//             `;
//         } catch (error) {
//             resultDiv.innerHTML = `
//                 <div class="alert alert-danger">
//                     Error: ${error.message}
//                 </div>
//             `;
//             if (currentMode === 'video') {
//                 isProcessing = false;
//                 videoFeed.style.display = 'none';
//             }
//         } finally {
//             loadingSpinner.style.display = 'none';
//         }
//     });

//     // Update video feed status
//     if (currentMode === 'video' && isProcessing) {
//         const updateStatus = async () => {
//             try {
//                 const response = await fetch('/video_status');
//                 const data = await response.json();
//                 if (data.prediction) {
//                     liveResult.textContent = `Current frame: ${data.prediction} (${(data.confidence * 100).toFixed(2)}% confidence)`;
//                 }
//             } catch (error) {
//                 console.error('Error updating status:', error);
//             }
//             if (isProcessing) {
//                 setTimeout(updateStatus, 1000);
//             }
//         };
//         updateStatus();
//     }
// });


document.addEventListener('DOMContentLoaded', function() {
    const imageBtn = document.getElementById('image-btn');
    const videoBtn = document.getElementById('video-btn');
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultDiv = document.getElementById('result');
    const loadingSpinner = document.getElementById('loading-spinner');
    const videoFeed = document.getElementById('video-feed');
    const videoStream = document.getElementById('video-stream');
    const liveResult = document.getElementById('live-result');

    let currentMode = null;
    let isProcessing = false;

    imageBtn.addEventListener('click', () => setMode('image'));
    videoBtn.addEventListener('click', () => setMode('video'));

    function setMode(mode) {
        currentMode = mode;
        imageBtn.classList.toggle('btn-primary', mode === 'image');
        videoBtn.classList.toggle('btn-primary', mode === 'video');

        fileInput.accept = mode === 'image' ? '.png,.jpg,.jpeg' : '.mp4,.avi,.mov';

        uploadForm.style.display = 'block';
        videoFeed.style.display = 'none';
        resultDiv.innerHTML = '';
    }

    analyzeBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!currentMode || !fileInput.files.length) {
            alert('Please select a file first');
            return;
        }

        videoFeed.style.display = currentMode === 'video' ? 'block' : 'none';
        videoStream.src = currentMode === 'video' ? "/video_feed" : "";

        loadingSpinner.style.display = currentMode === 'image' ? 'block' : 'none';
        resultDiv.innerHTML = '';
    });
});
