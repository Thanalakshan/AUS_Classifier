Dropzone.autoDiscover = false;

$(document).ready(function() {
    console.log("ready!");
    $("#error").hide();
    $("#resultHolder").hide();
    $("#divClassTable").hide();

    init();
});

function init() {
    let dz = new Dropzone("#dropzone", {
        url: "/classify_image",
        maxFiles: 1,
        addRemoveLinks: true,
        autoProcessQueue: false,
        init: function() {
            this.on("addedfile", function(file) {
                if (this.files[1] != null) {
                    this.removeFile(this.files[0]);
                }
            });
            this.on("complete", function(file) {
                this.removeFile(file);
            });
        },
        sending: function(file, xhr, formData) {
            var reader = new FileReader();
            reader.onload = function(event) {
                formData.append("image_data", event.target.result);
            };
            reader.readAsDataURL(file);
        },
        success: function(file, response) {
            // Handle the response from the server if needed
            console.log(response);
            if (response.error) {
                $("#error").text(response.error);
                $("#error").show();
            } else {
                // Display results or do something with the response
                console.log(response);
            }
        },
        error: function(file, response) {
            console.log(response);
            $("#error").text("Error uploading file.");
            $("#error").show();
        }
    });

    $("#submitBtn").on('click', function(e) {
        e.preventDefault();
        dz.processQueue();
    });
}