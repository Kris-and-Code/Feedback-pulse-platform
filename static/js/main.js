// Main frontend handling
class ReviewAnalyzer {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('urlForm').addEventListener('submit', this.handleUrlSubmit.bind(this));
        document.getElementById('csvForm').addEventListener('submit', this.handleCsvSubmit.bind(this));
    }

    async handleUrlSubmit(event) {
        event.preventDefault();
        const url = document.getElementById('urlInput').value;
        this.showProgressBar();
        
        try {
            const response = await this.sendUrlToBackend(url);
            await this.showResults(url);
        } catch (error) {
            this.showError(error);
        }
    }

    async handleCsvSubmit(event) {
        event.preventDefault();
        const file = document.getElementById('csvInput').files[0];
        this.showProgressBar();
        
        try {
            const response = await this.sendCsvToBackend(file);
            await this.showResults(file.name);
        } catch (error) {
            this.showError(error);
        }
    }

    async sendUrlToBackend(url) {
        return await $.ajax({
            url: '/api/scrape-review',
            method: 'POST',
            data: { url: url }
        });
    }

    async sendCsvToBackend(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        return await $.ajax({
            url: '/api/parse-review',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });
    }

    async showResults(identifier) {
        // Fetch aggregate data
        const [sentimentData, emotionData] = await Promise.all([
            this.fetchAggregateSentiment(identifier),
            this.fetchAggregateEmotion(identifier)
        ]);

        // Update UI
        this.updateProductInfo(identifier);
        this.updateAggregateInfo(sentimentData, emotionData);
        this.updateReviewsList(identifier);
        this.hideProgressBar();
    }

    showProgressBar() {
        document.getElementById('progressBar').style.display = 'block';
    }

    hideProgressBar() {
        document.getElementById('progressBar').style.display = 'none';
    }
} 