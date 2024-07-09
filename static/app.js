// Disable Dropzone autoDiscover
Dropzone.autoDiscover = false;

// Function to initialize Dropzone and handle file uploads
$(document).ready(function() {
    $("#error").hide();
    $("#resultHolder").hide();

    // Initialize the Dropzone instance
    initDropzone();
});

// Function to initialize Dropzone
function initDropzone() {
    let base64ImageData = "";

    // Create a new Dropzone instance
    let dz = new Dropzone("#dropzone", {
        url: "/classify_image", // Endpoint to handle file upload
        maxFiles: 1, // Limit to one file
        addRemoveLinks: true, // Enable remove file links
        autoProcessQueue: false, // Disable auto processing

        // Initialization callback
        init: function() {
            this.on("addedfile", function(file) {
                // Remove previous file if more than one file is added
                if (this.files[1] != null) {
                    this.removeFile(this.files[0]);
                }

                // Read file as base64 and store in base64ImageData
                var reader = new FileReader();
                reader.onload = function(event) {
                    base64ImageData = event.target.result;
                };
                reader.readAsDataURL(file);
            });
        },

        // Before sending callback
        sending: function(file, xhr, formData) {
            formData.append("image_data", base64ImageData); // Append base64 image data to form data
        },

        // Success callback
        success: function(file, response) {
            console.log("Success Response:", response); // Log response for debugging
            $("#error").hide(); // Hide any previous error messages

            if (response.error) {
                $("#error").text(response.error);
                $("#error").show();
            } else {
                $("#resultHolder").show();

                // Clear previous results
                $("#classTable tbody").empty();

                // Display the predicted player name(s)
                response.predicted_player.forEach(function(player_name) {
                    // Append player to table
                    $("#classTable tbody").append("<tr><td>" + player_name + "</td></tr>");

                    // Example: Update specific player card (if needed)
                    $(".card-wrapper[data-player='" + player_name.toLowerCase() + "']").addClass("border-success"); 
                });
            }
        },

        // Error callback
        error: function(file, response) {
            console.log("Error Response:", response); // Log error response for debugging
            $("#error").text("Error uploading file.");
            $("#error").show();
        }
    });

    // Event listener for 'Classify' button click
    $("#submitBtn").on('click', function(e) {
        e.preventDefault();
        dz.processQueue(); // Process the Dropzone queue
    });
}