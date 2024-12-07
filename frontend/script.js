$(document).ready(function () {
    // Analyze from URL
    $("#analyze-url-btn").click(function () {
      const url = $("#url-input").val();
      if (!url) {
        alert("Please enter a URL.");
        return;
      }
  
      // Show loading message
      $("#results-container").hide();
      $("#results-container").html("<p>Analyzing URL...</p>").show();
  
      // Send URL to backend
      $.ajax({
        url: "/scrape-review",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ url }),
        success: function (response) {
          console.log('Response:', response);
          if (response && typeof response === 'object') {
            displayResults(response);
          } else {
            $("#results-container").html("<p>Error: Invalid response from server</p>");
          }
        },
        error: function (xhr) {
          $("#results-container").html(`<p>Error: ${xhr.responseText || 'Failed to analyze URL'}</p>`);
        },
      });
    });
  
    // Analyze from CSV
    $("#analyze-csv-btn").click(function () {
      const file = $("#csv-input")[0].files[0];
      if (!file) {
        alert("Please select a file.");
        return;
      }
  
      // Show loading message
      $("#results-container").hide();
      $("#results-container").html("<p>Uploading and Analyzing CSV...</p>").show();
  
      const formData = new FormData();
      formData.append("file", file);
  
      // Send CSV file to backend
      $.ajax({
        url: "/parse-review",
        type: "POST",
        processData: false,
        contentType: false,
        data: formData,
        success: function (response) {
          console.log('Response:', response);
          if (response && typeof response === 'object') {
            displayResults(response);
          } else {
            $("#results-container").html("<p>Error: Invalid response from server</p>");
          }
        },
        error: function (xhr) {
          $("#results-container").html(`<p>Error: ${xhr.responseText || 'Failed to analyze CSV'}</p>`);
        },
      });
    });
  
    // Display results
    function displayResults(data) {
      $("#results-container").html("");
      $("#results-container").show();
  
      // Safely display product info with HTML escaping
      const productInfo = $("<div/>").text(data.productInfo || "N/A").html();
      $("#results-container").append(`<h3>Product Info</h3><p>${productInfo}</p>`);
  
      // Display aggregate info with safe defaults
      $("#results-container").append(`
        <h3>Aggregate Information</h3>
        <p><strong>Average Rating:</strong> ${data.averageRating?.toFixed(1) || "N/A"}</p>
        <p><strong>Overall Sentiment:</strong> ${$("<div/>").text(data.overallSentiment || "N/A").html()}</p>
        <p><strong>Overall Emotion:</strong> ${$("<div/>").text(data.overallEmotion || "N/A").html()}</p>
      `);
  
      // Display Individual Reviews
      const reviews = data.reviews || [];
      const reviewsList = $("<ul></ul>");
      reviews.forEach((review) => {
        reviewsList.append(`
          <li>
            <strong>Text:</strong> ${review.text}<br>
            <strong>Rating:</strong> ${review.rating}<br>
            <strong>Sentiment:</strong> ${review.sentiment}<br>
            <strong>Emotion:</strong> ${review.emotion}
          </li>
        `);
      });
      $("#results-container").append(`<h3>Reviews</h3>`).append(reviewsList);
    }
  });
  