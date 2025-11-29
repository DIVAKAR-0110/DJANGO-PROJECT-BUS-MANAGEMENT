$(document).ready(function(){
    $('#contactForm').submit(function(e){
        e.preventDefault();
        const formData = $(this).serialize();
        $.ajax({
            type: "POST",
            url: "{% url 'contact_submit' %}", // Django URL for form submission
            data: formData,
            success: function(response){
                $('#formMessage').text(response.message).fadeIn().delay(3000).fadeOut();
                $('#contactForm')[0].reset();
            },
            error: function(xhr, status, error){
                $('#formMessage').text("Oops! Something went wrong.").fadeIn().delay(3000).fadeOut();
            }
        });
    });
});
